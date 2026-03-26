/**
 * src/services/api.js
 *
 * ⚠️  資安規範：API URL 從環境變數讀取，絕不硬編碼
 *     本地開發 → .env 檔案 (已加入 .gitignore)
 *     AWS Amplify → Console > App settings > Environment variables
 */
import axios from 'axios'
import Papa from 'papaparse'

// ── 環境變數驗證 ────────────────────────────────────────────────
const API_URL = import.meta.env.VITE_API_URL

if (!API_URL) {
  console.error(
    '[api] ❌ VITE_API_URL 未設定！\n' +
    '  本地：請建立 .env 並加入 VITE_API_URL=https://...\n' +
    '  Amplify：請至 App settings > Environment variables 設定'
  )
}

// ── 常數 ────────────────────────────────────────────────────────
const TIMEOUT_MS = 180_000   // 3 分鐘，容許 Bedrock 長時間推論

// ─────────────────────────────────────────────────────────────────
// CSV 解析（PapaParse）
// 回傳 { fields: string[], data: object[] }
// ─────────────────────────────────────────────────────────────────
export function parseCsvFile(file) {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,          // 第一行為欄位名稱
      skipEmptyLines: true,
      encoding: 'UTF-8',
      complete: (result) => {
        if (result.errors.length) {
          console.warn('[api] PapaParse warnings:', result.errors)
        }
        console.log('[api] CSV fields:', result.meta.fields)
        console.log(`[api] CSV rows: ${result.data.length}，first row:`, result.data[0])
        resolve({ fields: result.meta.fields ?? [], data: result.data })
      },
      error: (err) => reject(new Error(`CSV 解析失敗：${err.message}`)),
    })
  })
}

// ─────────────────────────────────────────────────────────────────
// 回應格式標準化
// 後端可能回傳多種 schema，統一映射到 { risk_level, reason, ...原始欄位 }
// ─────────────────────────────────────────────────────────────────
function normalizeItem(item, idx) {
  console.log(`[api] raw[${idx}]:`, item)

  let risk_level = 'BLUE'
  const reason = item.reason ?? item.explanation ?? item.message ?? ''

  if (item.risk_level) {
    // 後端直接給字串：RED / YELLOW / BLUE / GREEN
    risk_level = String(item.risk_level).toUpperCase()
  } else if (item.label !== undefined) {
    // XGBoost 數值 label
    const label      = Number(item.label)
    const confidence = Number(item.confidence ?? item.score ?? item.probability ?? 0)
    if (label === 1)         risk_level = 'RED'
    else if (confidence >= 0.4) risk_level = 'YELLOW'
    else                     risk_level = 'BLUE'
  } else if (item.prediction) {
    const p = String(item.prediction).toLowerCase()
    if (p.includes('fake') || p.includes('disinfo')) risk_level = 'RED'
    else if (p.includes('uncertain') || p.includes('suspicious')) risk_level = 'YELLOW'
    else risk_level = 'BLUE'
  }

  return { ...item, risk_level, reason: reason || '—' }
}

// ─────────────────────────────────────────────────────────────────
// 主要匯出：解析 CSV → POST → 標準化結果
// ─────────────────────────────────────────────────────────────────

/**
 * @param {File}     file       使用者上傳的 .csv 文件
 * @param {Function} onProgress 進度回呼 (0–100)
 * @param {Function} onLog      日誌回呼 ({ level: 'info'|'warn'|'error'|'success', message: string })
 * @returns {Promise<Array>}    標準化後的分析結果
 */
export async function analyzeFile(file, onProgress, onLog) {
  const log = (level, msg) => {
    console.log(`[api][${level}] ${msg}`)
    onLog?.({ level, message: msg })
  }

  if (!API_URL) throw new Error('VITE_API_URL 未設定，請確認 .env 或 Amplify 環境變數')

  // ── Step 1: PapaParse 解析 CSV ───────────────────────────────
  log('info', `讀取文件：${file.name}`)
  onProgress?.(5)

  const { fields, data: records } = await parseCsvFile(file)
  log('info', `CSV 解析完成：${records.length} 筆 × ${fields.length} 欄`)
  onProgress?.(15)

  // ── Step 2: 封裝 Payload ─────────────────────────────────────
  const payload = {
    session_id: crypto.randomUUID(),
    timestamp:  new Date().toISOString(),
    records,
  }
  console.log('[api] POST payload (preview):', {
    session_id: payload.session_id,
    timestamp:  payload.timestamp,
    record_count: records.length,
    first_record: records[0],
  })
  log('info', `Session ID：${payload.session_id}`)
  onProgress?.(25)

  // ── Step 3: POST 至 Lambda ───────────────────────────────────
  log('info', `資料上傳成功，送往 ${API_URL}`)

  // ── CORS 預檢：先送 OPTIONS，確認後端有正確回應 ────────────────
  try {
    await axios.options(API_URL, {
      headers: {
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type',
      },
      timeout: 10_000,
    })
    log('info', 'CORS 預檢通過 ✅')
  } catch (preflightErr) {
    // OPTIONS 失敗通常就是 CORS 未設定
    console.warn('[api] OPTIONS preflight failed:', preflightErr.message)
    log('warn', 'CORS 預檢失敗，嘗試直接 POST（若失敗請修後端 CORS 設定）')
  }

  let response
  try {
    response = await axios.post(API_URL, payload, {
      headers: { 'Content-Type': 'application/json' },
      timeout: TIMEOUT_MS,
    })
  } catch (err) {
    const status = err.response?.status
    console.error('[api] HTTP error:', status, err.response?.data ?? err.message)

    if (status === 403)
      throw new Error('存取被拒 (403)：請確認 Lambda Function URL 的 CORS 與授權設定')
    if (status === 429)
      throw new Error('請求頻率超限 (429)：Bedrock 1 RPS 限制，請等待 30 秒後再試')
    if (status === 504 || err.code === 'ECONNABORTED')
      throw new Error(
        '偵辦超時，這可能是因為數據量較大或 AI 思考較久，' +
        '請確認 S3 是否已產出結果。'
      )
    // Network Error 在 CORS 失敗時觸發（瀏覽器不讓請求送出）
    if (!err.response && err.message?.includes('Network Error'))
      throw new Error(
        'CORS 錯誤：瀏覽器封鎖了此請求。\n' +
        '請至 Lambda Console → Configuration → Function URL → Edit → 啟用 CORS，\n' +
        '並確認 Allow origins 設為 * 或你的網站網址。'
      )

    throw new Error(err.response?.data?.message ?? err.message ?? '未知 API 錯誤')
  }

  // ── Step 4: 標準化回應 ───────────────────────────────────────
  onProgress?.(90)
  const raw = response.data
  console.log('[api] === RAW RESPONSE ===', raw)

  let rawList
  if (Array.isArray(raw))               rawList = raw
  else if (Array.isArray(raw?.results)) rawList = raw.results
  else if (Array.isArray(raw?.data))    rawList = raw.data
  else {
    console.warn('[api] Unexpected shape:', raw)
    throw new Error('後端回傳格式無法識別，請開啟 DevTools > Console 查看 RAW RESPONSE')
  }

  log('info', `收到 ${rawList.length} 筆原始結果，標準化中…`)
  const normalized = rawList.map(normalizeItem)
  onProgress?.(100)

  console.log('[api] === NORMALIZED RESULTS ===', normalized)
  return normalized
}
