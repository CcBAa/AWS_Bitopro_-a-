import json
import boto3
import csv
import io
import os
import base64

# ── 初始化 AWS 服務客戶端 ──────────────────────────────────────────
sm_client = boto3.client('sagemaker-runtime')
# 提醒：請確認你的 Claude 模型權限是在 us-west-2 開通的
bedrock_client = boto3.client('bedrock-runtime', region_name='us-west-2')

# ── 設定（從 Lambda 環境變數讀取） ─────────────────────────────────
ENDPOINT_NAME = os.environ.get('SAGEMAKER_ENDPOINT', 'BitoGuard-Final-1774575590')
CLAUDE_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
RISK_THRESHOLD = float(os.environ.get('RISK_THRESHOLD', '0.65'))
MAX_SAR_COUNT = int(os.environ.get('MAX_SAR_COUNT', '3'))
TIME_BUFFER_MS = 5000 

# ⚠️ 必須與訓練時的特徵順序完全一致
FEATURE_COLUMNS = [
    'twd_total_amt', 'twd_tx_count', 'twd_avg_amt', 'twd_std_amt', 'twd_max_amt', 
    'twd_min_amt', 'twd_days', 'twd_velocity', 'twd_cv', 'twd_top1_share', 
    'twd_amt_range_ratio', 'twd_skewness', 'twd_kurtosis', 'twd_spike_ratio',
    'twd_avg_interval_h', 'twd_interval_std', 'twd_min_interval_h', 'twd_interval_cv',
    'twd_peak_day_ratio', 'crypto_total_amt', 'crypto_tx_count', 'crypto_avg_amt',
    'crypto_std_amt', 'crypto_cv', 'crypto_out_delay_hours', 'max_shared_wallet',
    'avg_shared_wallet', 'suspicious_wallet_tx_count', 'trade_total_amt', 'trade_count',
    'trade_avg_amt', 'trade_std_amt', 'trade_cv', 'trade_days', 'trade_velocity',
    'wash_time_hours', 'min_twd_crypto_gap_hours', 'avg_twd_crypto_gap_hours',
    'median_twd_crypto_gap_h', 'gap_std_hours', 'rapid_conversion_count',
    'gap_under_24h', 'gap_under_6h', 'rapid_ratio_24h', 'amt_combined_cv',
    'total_tx_count', 'twd_vol_variability', 'crypto_leverage', 'conversion_intensity',
    'large_tx_crypto_signal', 'network_risk_score', 'timing_amt_risk',
    'twd_total_amt_pct', 'twd_std_amt_pct', 'twd_cv_pct', 'crypto_total_amt_pct',
    'trade_total_amt_pct', 'twd_velocity_pct', 'max_shared_wallet_pct', 'min_gap_risk_pct'
]

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
}

def build_response(status_code, body_dict):
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(body_dict, ensure_ascii=False),
    }

def generate_sar(user_id, risk_score, features_dict):
    """呼叫 Bedrock 生成 Markdown 格式報告"""
    prompt = f"""你是一名資深的虛擬資產洗錢防制審查官。
用戶 ID: {user_id} 被判定洗錢風險達 {risk_score * 100:.1f}%。
請針對以下特徵數據撰寫專業分析報告：
{json.dumps(features_dict, indent=2, ensure_ascii=False)}

【要求】：語氣嚴謹，條列關鍵紅旗警訊，並提供 Markdown 格式的處置建議。"""
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 800,
        "temperature": 0.2,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    })

    try:
        response = bedrock_client.invoke_model(modelId=CLAUDE_MODEL_ID, body=body)
        result = json.loads(response.get('body').read())
        return result.get('content', [{}])[0].get('text', '報告解析失敗')
    except Exception as e:
        print(f"Bedrock Error: {str(e)}")
        return f"報告生成失敗: {str(e)}"

def lambda_handler(event, context):
    # 1. CORS 預檢
    method = event.get('requestContext', {}).get('http', {}).get('method', event.get('httpMethod', ''))
    if method.upper() == 'OPTIONS':
        return build_response(200, {'message': 'OK'})

    try:
        # 2. 數據解碼與讀取 (加入 utf-8-sig 防止 BOM)
        raw_body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            raw_body = base64.b64decode(raw_body).decode('utf-8-sig')
        else:
            # 即使不是 base64 也嘗試處理可能的編碼問題
            if isinstance(raw_body, bytes):
                raw_body = raw_body.decode('utf-8-sig')
            else:
                raw_body = str(raw_body).encode().decode('utf-8-sig')

        if not raw_body.strip():
            return build_response(400, {'error': 'CSV is empty'})

        reader = csv.DictReader(io.StringIO(raw_body))
        user_ids, payload_rows, original_rows = [], [], []

        # 3. 按順序提取特徵
        for row in reader:
            uid = row.get('user_id', 'unknown')
            user_ids.append(uid)
            # 保留原始數據供 Bedrock 生成報告使用
            original_rows.append({k: v for k, v in row.items() if k != 'status'})

            vals = []
            for col in FEATURE_COLUMNS:
                val = row.get(col, 0.0)
                try:
                    vals.append(str(float(val)))
                except (ValueError, TypeError):
                    vals.append("0.0")
            payload_rows.append(','.join(vals))

        if not payload_rows:
            return build_response(400, {'error': 'No valid records found in CSV'})

        # 4. 呼叫 SageMaker 推論
        sm_response = sm_client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='text/csv',
            Body='\n'.join(payload_rows)
        )
        
        sm_result = sm_response['Body'].read().decode('utf-8').strip()
        
        # 修正：精確按行分割，確保索引與 user_ids 一致
        raw_lines = sm_result.splitlines()
        probs = []
        for line in raw_lines:
            if not line.strip(): continue
            # 處理可能回傳的 [p0, p1] 格式，取最後一個值作為正樣本機率
            val = line.split(',')[-1]
            probs.append(float(val))

        if len(probs) != len(user_ids):
            print(f"Mismatch: IDs={len(user_ids)}, Probs={len(probs)}")
            # 如果數量不符，嘗試根據返回行數截斷或報錯
            probs = probs[:len(user_ids)]

        # 5. 整理結果
        results = []
        for i, uid in enumerate(user_ids):
            prob = probs[i]
            is_high = prob >= RISK_THRESHOLD
            
            results.append({
                "user_id": uid,
                "ai_prediction": 1 if prob >= 0.5 else 0,
                "confidence": round(prob, 4),
                "is_extreme_risk": is_high,
                "reason": f"風險分數 {prob*100:.1f}%：{'疑似洗錢操蹤' if is_high else '交易模式正常'}",
                "sar_report": None,
                "_score": prob
            })

        # 6. 生成高風險報告 (Top-N)
        high_risk_indices = [i for i, r in enumerate(results) if r['is_extreme_risk']]
        high_risk_indices.sort(key=lambda i: results[i]['_score'], reverse=True)
        
        for idx in high_risk_indices[:MAX_SAR_COUNT]:
            # Lambda 剩餘時間檢查
            if context.get_remaining_time_in_millis() < TIME_BUFFER_MS:
                results[idx]['sar_report'] = "[Timeout] 時間不足，取消生成報告"
                continue
            
            r = results[idx]
            r['sar_report'] = generate_sar(r['user_id'], r['confidence'], original_rows[idx])

        # 移除內部使用的排序分數
        for r in results: r.pop('_score', None)
        
        return build_response(200, {"predictions": results})

    except Exception as e:
        print(f"General Error: {str(e)}")
        return build_response(500, {"error": str(e)})