import axios from 'axios'

// ── 後端 Lambda URL（組員完成後填入）──────────────────────────────
// const LAMBDA_URL = 'https://YOUR_API_GATEWAY_ID.execute-api.ap-northeast-1.amazonaws.com/prod'

// ── Mock Data（後端尚未完成時使用）────────────────────────────────
const mockResults = [
  {
    id: 'msg-001',
    timestamp: '2026-03-26 09:01:23',
    text: '政府秘密在疫苗中植入追蹤晶片，WHO 已承認此事',
    risk_level: 'RED',
    reason: '典型陰謀論句型，無可信來源佐證，與 WHO 官方聲明矛盾',
  },
  {
    id: 'msg-002',
    timestamp: '2026-03-26 09:03:47',
    text: '研究顯示氣候變遷可能加速某些地區的極端降雨事件',
    risk_level: 'BLUE',
    reason: '符合 IPCC 第六次評估報告內容，措辭保守且有學術依據',
  },
  {
    id: 'msg-003',
    timestamp: '2026-03-26 09:07:12',
    text: '本市長選舉投票所被爆出大量廢票疑雲，選委會拒絕說明',
    risk_level: 'YELLOW',
    reason: '存在煽動性語言，事件尚未經官方確認，需進一步核實',
  },
  {
    id: 'msg-004',
    timestamp: '2026-03-26 09:11:55',
    text: '外星人已與美國政府簽署秘密協議，五角大廈文件外洩',
    risk_level: 'RED',
    reason: '無可信文件來源，關鍵字符合陰謀論散播模式',
  },
  {
    id: 'msg-005',
    timestamp: '2026-03-26 09:15:30',
    text: '台灣中央銀行宣布調升利率半碼，以抑制通膨壓力',
    risk_level: 'BLUE',
    reason: '可於央行官網查證，為正規財經新聞，無扭曲事實',
  },
  {
    id: 'msg-006',
    timestamp: '2026-03-26 09:18:44',
    text: '某知名廠牌飲料驗出致癌物，衛生局尚未回應',
    risk_level: 'YELLOW',
    reason: '缺乏具名機構或報告，可能為誇大不實，待官方聲明',
  },
  {
    id: 'msg-007',
    timestamp: '2026-03-26 09:22:01',
    text: '5G 基地台會釋放致命輻射，已有多起死亡案例被掩蓋',
    risk_level: 'RED',
    reason: '違反電磁輻射科學共識，死亡案例無任何可查來源',
  },
  {
    id: 'msg-008',
    timestamp: '2026-03-26 09:25:19',
    text: '新北市政府開放線上申請長照補助，受理至月底',
    risk_level: 'BLUE',
    reason: '政府公告訊息，可於官網核實，無誇大或歪曲',
  },
]

/**
 * 分析 CSV 文件並回傳結果
 *
 * Mock 模式：直接回傳 mockResults，模擬非同步延遲
 *
 * 後端就緒後，取消下方 POST 區塊的註解，並刪除 mock 回傳即可
 *
 * @param {File} file - 使用者上傳的 CSV 文件
 * @param {Function} onProgress - 上傳進度回呼 (0~100)
 * @returns {Promise<Array>} 分析結果陣列
 */
export async function analyzeFile(file, onProgress) {
  // ── MOCK MODE ──────────────────────────────────────────────────
  // 模擬 1.5 秒的「上傳 + 分析」延遲
  await new Promise(resolve => {
    let progress = 0
    const interval = setInterval(() => {
      progress += 10
      onProgress?.(Math.min(progress, 95))
      if (progress >= 95) clearInterval(interval)
    }, 150)
    setTimeout(() => {
      clearInterval(interval)
      onProgress?.(100)
      resolve()
    }, 1500)
  })
  return mockResults

  // ── REAL MODE（後端完成後啟用）────────────────────────────────
  // const formData = new FormData()
  // formData.append('file', file)
  //
  // // Step 1: 上傳 CSV，取得 job_id
  // const uploadRes = await axios.post(`${LAMBDA_URL}/upload`, formData, {
  //   headers: { 'Content-Type': 'multipart/form-data' },
  //   onUploadProgress(e) {
  //     onProgress?.(Math.round((e.loaded / e.total) * 50))
  //   },
  // })
  // const jobId = uploadRes.data?.job_id
  // if (!jobId) throw new Error('後端未回傳 job_id')
  //
  // // Step 2: Polling 等待分析完成
  // return await pollJobStatus(jobId, onProgress)
}

/**
 * 輪詢 Job 狀態直到完成（配合後端使用）
 *
 * @param {string} jobId
 * @param {Function} onProgress
 * @returns {Promise<Array>}
 */
// async function pollJobStatus(jobId, onProgress) {
//   const MAX_RETRIES = 150   // 最多 5 分鐘
//   const INTERVAL_MS = 2000  // 每 2 秒查一次（符合 Bedrock 1 RPS 限制）
//   let retries = 0
//
//   while (retries < MAX_RETRIES) {
//     await new Promise(r => setTimeout(r, INTERVAL_MS))
//     const res = await axios.get(`${LAMBDA_URL}/status/${jobId}`)
//     const { status, results } = res.data
//
//     onProgress?.(Math.min(99, 50 + Math.round((retries / MAX_RETRIES) * 49)))
//
//     if (status === 'completed') return Array.isArray(results) ? results : []
//     if (status === 'failed') throw new Error(res.data.message || '後端分析失敗')
//     retries++
//   }
//   throw new Error('分析逾時，請稍後再試')
// }
