import json
import boto3
import csv
import io
import os
import base64
import urllib3

# ── 初始化 AWS 服務客戶端 ──────────────────────────────────────────
sm_client = boto3.client('sagemaker-runtime')
bedrock_client = boto3.client('bedrock-runtime', region_name='us-west-2')
http = urllib3.PoolManager()

# ── 設定（從 Lambda 環境變數讀取） ─────────────────────────────────
# 🚀 已經將預設 Endpoint 更新為你的 BitoGuard-Final-1774575590
ENDPOINT_NAME = os.environ.get('SAGEMAKER_ENDPOINT', 'BitoGuard-Final-1774575590')
CLAUDE_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
API_BASE_URL = "https://aws-event-api.bitopro.com/predict_label"
RISK_THRESHOLD = float(os.environ.get('RISK_THRESHOLD', '0.65'))
MAX_SAR_COUNT = int(os.environ.get('MAX_SAR_COUNT', '3'))
TIME_BUFFER_MS = 6000 

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
    return {'statusCode': status_code, 'headers': CORS_HEADERS, 'body': json.dumps(body_dict, ensure_ascii=False)}

def fetch_user_features(user_id):
    """從 BitoPro API 獲取特徵資料"""
    try:
        url = f"{API_BASE_URL}?user_id={user_id}"
        r = http.request('GET', url, timeout=4.0)
        if r.status == 200:
            data = json.loads(r.data.decode('utf-8'))
            if isinstance(data, list) and len(data) > 0: return data[0]
            return data if isinstance(data, dict) else {}
        return {}
    except Exception as e:
        print(f"API Error ({user_id}): {str(e)}")
        return {}

def generate_sar(user_id, risk_score, features_dict):
    """呼叫 Bedrock 生成 Markdown 格式報告"""
    prompt = f"你是一名資深的虛擬資產洗錢防制審查官。用戶 ID: {user_id} 洗錢風險 {risk_score * 100:.1f}%。請針對以下特徵撰寫專業分析報告：\n{json.dumps(features_dict, ensure_ascii=False)}"
    
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
        return f"報告生成失敗: {str(e)}"

def lambda_handler(event, context):
    method = event.get('requestContext', {}).get('http', {}).get('method', event.get('httpMethod', ''))
    if method.upper() == 'OPTIONS': return build_response(200, {'message': 'OK'})

    try:
        # 1. 數據讀取與解碼
        raw_body = event.get('body', '')
        if event.get('isBase64Encoded', False):
            raw_body = base64.b64decode(raw_body).decode('utf-8-sig')
        else:
            raw_body = raw_body.encode().decode('utf-8-sig') if isinstance(raw_body, bytes) else str(raw_body)

        reader = csv.DictReader(io.StringIO(raw_body))
        user_ids, payload_rows, original_rows = [], [], []

        for row in reader:
            uid = row.get('user_id')
            if not uid: continue
            
            user_ids.append(uid)
            user_features = fetch_user_features(uid)
            original_rows.append(user_features)

            vals = []
            for col in FEATURE_COLUMNS:
                val = user_features.get(col, 0.0)
                try:
                    vals.append(str(float(val)))
                except:
                    vals.append("0.0")
            payload_rows.append(','.join(vals))

        if not payload_rows: return build_response(400, {'error': 'No user_id found in CSV'})

        # 🚀 2. 核心修正：強制補齊 Header，確保 SageMaker 解析器認得出來
        csv_header = ','.join(FEATURE_COLUMNS)
        csv_body = csv_header + '\n' + '\n'.join(payload_rows) + '\n'
            
        encoded_body = csv_body.encode('utf-8')

        # 🚨 終極排查日誌
        print("========== 🚨 DEBUG: PAYLOAD TO SAGEMAKER 🚨 ==========")
        print(f"Payload Type: {type(encoded_body)}")
        print(f"Payload Preview:\n{csv_body[:500]}")
        print("=====================================================")

        # 3. 呼叫 SageMaker 推論
        sm_response = sm_client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='text/csv',
            Body=encoded_body
        )
        
        sm_result = sm_response['Body'].read().decode('utf-8').strip()
        raw_lines = sm_result.splitlines()
        
        print("========== 🚨 DEBUG: SAGEMAKER RESPONSE 🚨 ==========")
        print(sm_result)
        print("=====================================================")

        # 4. 解析結果 (略過標題列)
        probs = []
        for line in raw_lines:
            # 略過空行或包含英文字母的標題列
            if not line.strip() or any(char.isalpha() for char in line): continue
            try:
                probs.append(float(line.split(',')[-1]))
            except: continue

        # 5. 整理結果與生成報告
        results = []
        for i, uid in enumerate(user_ids):
            if i >= len(probs): break
            prob = probs[i]
            is_high = prob >= RISK_THRESHOLD
            results.append({
                "user_id": uid,
                "ai_prediction": 1 if prob >= 0.5 else 0,
                "confidence": round(prob, 4),
                "is_extreme_risk": is_high,
                "reason": f"風險分數 {prob*100:.1f}%：數據偏離正常範圍，建議由法遵進行二審" if is_high else "交易模式正常",
                "sar_report": None,
                "_score": prob
            })

        high_risk_indices = sorted([i for i, r in enumerate(results) if r['is_extreme_risk']], 
                                   key=lambda i: results[i]['_score'], reverse=True)
        
        for idx in high_risk_indices[:MAX_SAR_COUNT]:
            if context.get_remaining_time_in_millis() < TIME_BUFFER_MS:
                results[idx]['sar_report'] = "[Timeout] 時間不足，無法生成 AI 報告"
                continue
            r = results[idx]
            r['sar_report'] = generate_sar(r['user_id'], r['confidence'], original_rows[idx])

        for r in results: r.pop('_score', None)
        return build_response(200, {"predictions": results})

    except Exception as e:
        print(f"General Error: {str(e)}")
        return build_response(500, {"error": str(e)})