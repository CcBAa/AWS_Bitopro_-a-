import json
import boto3
import csv
import io
import os

# ── 初始化 AWS 服務客戶端 ──────────────────────────────────────────
sm_client = boto3.client('sagemaker-runtime')
bedrock_client = boto3.client('bedrock-runtime', region_name='us-west-2')

# ── 設定（從 Lambda 環境變數讀取，避免硬編碼機密） ─────────────────
ENDPOINT_NAME = os.environ.get('SAGEMAKER_ENDPOINT', 'BitoGuard-Endpoint-REPLACE_ME')
CLAUDE_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
RISK_THRESHOLD = float(os.environ.get('RISK_THRESHOLD', '0.77'))
MAX_SAR_COUNT = int(os.environ.get('MAX_SAR_COUNT', '3'))
TIME_BUFFER_MS = 5000       # 🔒 至少保留 5 秒給回傳

# ── 通用 CORS Headers ─────────────────────────────────────────────
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
}


def build_response(status_code, body_dict):
    """統一回傳格式，確保所有路徑都帶 CORS headers"""
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(body_dict, ensure_ascii=False),
    }


def generate_sar(user_id, risk_score, features_dict):
    """呼叫 Bedrock Claude 生成洗錢防制報告（Markdown 格式）"""
    prompt = f"""你是一名資深的金融洗錢防制 (AML) 審查官。
我們的風控系統標記了一名極高風險的用戶（User ID: {user_id}），洗錢風險高達 {risk_score * 100:.1f}%。
請根據以下特徵，撰寫一份簡短且專業的「可疑交易分析報告 (SAR)」。

【用戶特徵數據】：
{json.dumps(features_dict, indent=2, ensure_ascii=False)}

【報告要求】：
1. 語氣嚴謹冷靜，適合法遵部門審閱。
2. 解釋異常特徵背後的洗錢手法（如：資金快進快出、偽裝交易失真等）。
3. 條列 2-3 個最嚴重的紅旗警訊，並給出後續調查建議（如：凍結帳戶）。

⚠️ **請務必以 Markdown 格式輸出**（使用標題、粗體、條列等），以便前端渲染。
"""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 800,
        "temperature": 0.2,
        "messages": [{"role": "user", "content": prompt}],
    })

    # generate_sar 自身的 try/except — 失敗不會炸掉整個 Lambda
    try:
        response = bedrock_client.invoke_model(modelId=CLAUDE_MODEL_ID, body=body)
        result = json.loads(response.get('body').read())
        return result.get('content', [{}])[0].get('text', '[Bedrock 錯誤] 回傳格式異常')
    except Exception as e:
        return f"[Bedrock 錯誤] 報告生成失敗: {str(e)}"


def lambda_handler(event, context):
    # ══════════════════════════════════════════════════════════════
    # 1️⃣  CORS 預檢攔截 — OPTIONS 直接放行
    # ══════════════════════════════════════════════════════════════
    http_method = event.get('requestContext', {}).get('http', {}).get('method', '')
    if not http_method:
        http_method = event.get('httpMethod', '')

    if http_method.upper() == 'OPTIONS':
        return build_response(200, {'message': 'CORS preflight OK'})

    try:
        # ══════════════════════════════════════════════════════════
        # 2️⃣  讀取 Body — 空值防禦 + Base64 解碼（Function URL 可能編碼）
        # ══════════════════════════════════════════════════════════
        csv_data = event.get('body', '')

        # Lambda Function URL 可能對 body 做 Base64 編碼
        if event.get('isBase64Encoded', False) and csv_data:
            import base64
            csv_data = base64.b64decode(csv_data).decode('utf-8')

        if not csv_data or not csv_data.strip():
            return build_response(400, {
                'error': 'Request body 為空，請上傳有效的 CSV 資料。'
            })

        # 🔍 偵錯：印出收到的 CSV 前 200 字元到 CloudWatch
        print(f"[DEBUG] CSV 前 200 字元: {csv_data[:200]}")
        print(f"[DEBUG] CSV 總長度: {len(csv_data)}")

        reader = csv.DictReader(io.StringIO(csv_data))

        user_ids = []
        features_list = []
        original_rows = []

        for row in reader:
            # ══════════════════════════════════════════════════════
            # 3️⃣  安全取值 — pop 時提供預設值，避免 KeyError
            # ══════════════════════════════════════════════════════
            uid_raw = row.pop('user_id', None)
            if uid_raw is None:
                continue  # 跳過缺少 user_id 的列
            try:
                user_ids.append(int(uid_raw))
            except (ValueError, TypeError):
                user_ids.append(str(uid_raw))

            # 保留一份完整 row 供 Bedrock 寫報告
            clean_row = dict(row)
            clean_row.pop('status', None)
            original_rows.append(clean_row)

            # 剔除不需要的欄位供 SageMaker 預測
            row.pop('status', None)
            row.pop('std_time', None)

            # 將剩下的數值轉為逗號分隔的字串
            features = ','.join([str(val) for val in row.values()])
            features_list.append(features)

        if not features_list:
            return build_response(400, {
                'error': 'CSV 中沒有有效的資料列（缺少 user_id 或格式錯誤）。'
            })

        payload = '\n'.join(features_list)

        # ══════════════════════════════════════════════════════════
        # 呼叫 SageMaker 雲端大腦
        # ══════════════════════════════════════════════════════════
        response = sm_client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='text/csv',
            Body=payload,
        )

        result_body = response['Body'].read().decode('utf-8')
        probs = [float(p) for p in result_body.replace('\n', ',').split(',') if p.strip()]

        # ══════════════════════════════════════════════════════════
        # 4️⃣  整理結果 + Bedrock 報告（Top-3 + 時間檢查）
        # ══════════════════════════════════════════════════════════
        results = []
        for i, uid in enumerate(user_ids):
            prob = probs[i] if i < len(probs) else 0.0
            is_high_risk = prob >= RISK_THRESHOLD

            # 根據風險等級產生 reason 說明
            if is_high_risk:
                reason = f"風險分數 {prob*100:.1f}% 超過門檻 {RISK_THRESHOLD*100:.0f}%，疑似洗錢或操縱行為"
            elif prob >= 0.5:
                reason = f"風險分數 {prob*100:.1f}%，存在可疑交易模式，建議持續監控"
            else:
                reason = f"風險分數 {prob*100:.1f}%，交易模式正常"

            results.append({
                "user_id": uid,
                "ai_prediction": 1 if prob >= 0.5 else 0,
                "confidence": round(prob, 4),
                "is_extreme_risk": is_high_risk,
                "reason": reason,
                "risk_score": round(prob, 4),      # 用於排序取 Top-3
                "sar_report": None,
            })

        # ── 篩選極高風險 → 按 risk_score 降序 → 僅取前 MAX_SAR_COUNT 筆 ──
        extreme_indices = [
            i for i, r in enumerate(results) if r['is_extreme_risk']
        ]
        extreme_indices.sort(key=lambda i: results[i]['risk_score'], reverse=True)
        top_indices = extreme_indices[:MAX_SAR_COUNT]

        sar_generated = 0
        sar_skipped_timeout = 0

        for idx in top_indices:
            # 🔒 時間檢查：剩餘時間不足就停止呼叫 Bedrock
            remaining_ms = context.get_remaining_time_in_millis()
            if remaining_ms < TIME_BUFFER_MS:
                # 標註剩餘的極高風險為「超時跳過」
                for remaining_idx in top_indices[top_indices.index(idx):]:
                    results[remaining_idx]['sar_report'] = (
                        "[超時跳過] Lambda 剩餘時間不足，未生成報告。"
                        "請稍後單獨查詢此用戶，或降低單次上傳筆數。"
                    )
                    sar_skipped_timeout += 1
                break

            # 5️⃣ 呼叫 Bedrock — 即使失敗也不影響整體回傳
            r = results[idx]
            r['sar_report'] = generate_sar(
                r['user_id'],
                r['risk_score'],
                original_rows[idx],
            )
            sar_generated += 1

        # 未被選中的極高風險交易（排名第 4 及之後）標註原因
        for idx in extreme_indices[MAX_SAR_COUNT:]:
            results[idx]['sar_report'] = (
                f"[未生成] 本次僅針對風險最高的前 {MAX_SAR_COUNT} 名生成報告。"
            )

        # 清除內部排序用欄位
        for r in results:
            r.pop('risk_score', None)

        return build_response(200, {
            "predictions": results,
            "meta": {
                "total": len(results),
                "extreme_risk_count": len(extreme_indices),
                "sar_generated": sar_generated,
                "sar_skipped_timeout": sar_skipped_timeout,
                "sar_skipped_limit": max(0, len(extreme_indices) - MAX_SAR_COUNT),
            },
        })

    except Exception as e:
        return build_response(500, {"error": str(e)})
