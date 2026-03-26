/**
 * src/services/api.js
 *
 * ⚠️  資安規範：API URL 從環境變數讀取，絕不硬編碼
 *     本地開發 → .env 檔案 (已加入 .gitignore)
 *     AWS Amplify → Console > App settings > Environment variables
 */
import axios from 'axios'

// ── 環境變數驗證 ────────────────────────────────────────────────
const API_URL = import.meta.env.VITE_API_URL

if (!API_URL) {
  console.error(
    '[api] ❌ VITE_API_URL 未設定！\n' +
    '  本地：請建立 .env 並加入 VITE_API_URL=https://...\n' +
    '  Amplify：請至 App settings > Environment variables 設定'
  )
}

const TIMEOUT_MS = 180_000  // 3 分鐘，容許 SageMaker/Bedrock 長時間推論

// ─────────────────────────────────────────────────────────────────
// 工具：讀取 File 為純文字（用於 text/csv 傳送）
// ─────────────────────────────────────────────────────────────────
function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload  = e => resolve(e.target.result)
    reader.onerror = () => reject(new Error('FileReader 讀取失敗'))
    reader.readAsText(file, 'UTF-8')
  })
}

// ─────────────────────────────────────────────────────────────────
// 工具：Retry 包裝器（網路波動時重試一次，HTTP 錯誤不重試）
// ─────────────────────────────────────────────────────────────────
async function withRetry(fn, log, maxRetries = 1) {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (err) {
      // 有 HTTP 回應的錯誤（4xx / 5xx）直接拋出，不重試
      if (err.response) throw err

      // 網路層錯誤（斷線、CORS、timeout）才重試
      if (attempt < maxRetries) {
        log('warn', `網路錯誤，60 秒後自動重試（第 ${attempt + 1} 次）…`)
        await new Promise(r => setTimeout(r, 60_000))
      } else {
        throw err
      }
    }
  }
}

// ─────────────────────────────────────────────────────────────────
// 回應標準化
// 後端格式：{ "predictions": [{ user_id, ai_prediction, confidence }] }
// ai_prediction: 1 → RED（高風險），0 → BLUE（低風險）
// ─────────────────────────────────────────────────────────────────
function normalizeItem(item, idx) {
  console.log(`[api] raw[${idx}]:`, item)

  let risk_level

  // ── 優先使用 ai_prediction（本次後端格式）────────────────────
  if (item.ai_prediction !== undefined) {
    risk_level = Number(item.ai_prediction) === 1 ? 'RED' : 'BLUE'
  }
  // ── 相容舊格式 risk_level 字串 ────────────────────────────────
  else if (item.risk_level) {
    risk_level = String(item.risk_level).toUpperCase()
  }
  // ── 相容 label 數值（XGBoost 慣例） ──────────────────────────
  else if (item.label !== undefined) {
    risk_level = Number(item.label) === 1 ? 'RED' : 'BLUE'
  }
  else {
    risk_level = 'BLUE'
  }

  const reason = item.reason ?? item.explanation ?? '—'

  return { ...item, risk_level, reason }
}

// ─────────────────────────────────────────────────────────────────
// 主要匯出：讀取 CSV → POST（text/csv）→ 標準化結果
// ─────────────────────────────────────────────────────────────────

/**
 * @param {File}     file       使用者上傳的 .csv 文件
 * @param {Function} onProgress 進度回呼 (0–100)
 * @param {Function} onLog      日誌回呼 ({ level, message })
 * @returns {Promise<Array>}    標準化後的分析結果
 */
export async function analyzeFile(file, onProgress, onLog) {
  const log = (level, msg) => {
    console.log(`[api][${level}] ${msg}`)
    onLog?.({ level, message: msg })
  }

  if (!API_URL) throw new Error('VITE_API_URL 未設定，請確認 .env 或 Amplify 環境變數')

  // ── Step 1: 讀取原始 CSV 文字 ─────────────────────────────────
  log('info', `讀取文件：${file.name}`)
  onProgress?.(5)

  const csvText = await readFileAsText(file)

  // 計算行數（預覽用，不解析）
  const rowCount = csvText.trim().split('\n').length - 1  // 扣掉 header
  const firstLine = csvText.split('\n')[0]
  console.log('[api] CSV header:', firstLine)
  console.log(`[api] CSV rows: ${rowCount}`)

  log('info', `CSV 讀取完成：${rowCount} 筆資料`)
  onProgress?.(20)

  // ── Step 2: POST（Content-Type: text/csv）─────────────────────
  // 後端以 csv.DictReader 讀取，需要接收純 CSV 文字
  log('info', '正在送出 CSV 至 Lambda（text/csv）…')

  let response
  try {
    response = await withRetry(
      () => axios.post(API_URL, csvText, {
        headers: { 'Content-Type': 'text/csv' },
        timeout: TIMEOUT_MS,
      }),
      log,
    )
  } catch (err) {
    const status  = err.response?.status
    const detail  = err.response?.data?.error   // Lambda 拋出的具體錯誤
    const message = err.response?.data?.message

    // ── 500：印出後端拋出的 error 欄位（SageMaker 崩潰 / CSV 格式問題）
    if (status === 500) {
      console.error('[api] 500 error.response.data:', err.response.data)
      const backendError = detail ?? message ?? JSON.stringify(err.response.data)
      log('error', `後端錯誤 (500)：${backendError}`)
      throw new Error(`Lambda 內部錯誤 (500)：${backendError}`)
    }

    if (status === 403)
      throw new Error('存取被拒 (403)：請確認 Lambda Function URL 的 CORS 與授權設定')
    if (status === 429)
      throw new Error('請求頻率超限 (429)：請等待 30 秒後再試')
    if (status === 504 || err.code === 'ECONNABORTED')
      throw new Error('偵辦超時，這可能是因為數據量較大或 AI 思考較久，請確認 S3 是否已產出結果。')
    if (!err.response && err.message?.includes('Network Error'))
      throw new Error(
        'CORS 錯誤：瀏覽器封鎖了此請求。\n' +
        '請至 Lambda Console → Configuration → Function URL → Edit → 啟用 CORS，\n' +
        '並確認 Allow origins 設為 * 或你的網站網址。'
      )

    throw new Error(message ?? err.message ?? '未知 API 錯誤')
  }

  // ── Step 3: 解析回應 ──────────────────────────────────────────
  onProgress?.(90)
  const raw = response.data
  console.log('[api] === RAW RESPONSE ===', raw)

  // 支援 { predictions: [...] }（本次後端格式）及其他常見格式
  let rawList
  if (Array.isArray(raw?.predictions))  rawList = raw.predictions
  else if (Array.isArray(raw))          rawList = raw
  else if (Array.isArray(raw?.results)) rawList = raw.results
  else if (Array.isArray(raw?.data))    rawList = raw.data
  else {
    console.warn('[api] Unexpected response shape:', raw)
    throw new Error('後端回傳格式無法識別，請開啟 DevTools > Console 查看 RAW RESPONSE')
  }

  log('info', `收到 ${rawList.length} 筆結果，標準化中…`)
  const normalized = rawList.map(normalizeItem)
  onProgress?.(100)

  console.log('[api] === NORMALIZED RESULTS ===', normalized)
  return normalized
}
