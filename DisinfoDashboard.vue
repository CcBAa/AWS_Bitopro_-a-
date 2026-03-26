<template>
  <div class="dashboard-container">
    <!-- Header -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="header-logo">
          <span class="logo-icon">🔍</span>
          <div>
            <h1 class="header-title">去偽存真 · DisInfo Shield</h1>
            <p class="header-subtitle">AI-Powered Disinformation Detection System</p>
          </div>
        </div>
        <div class="status-badge" :class="systemStatus.class">
          <span class="status-dot"></span>
          {{ systemStatus.text }}
        </div>
      </div>
    </header>

    <main class="dashboard-main">
      <!-- Upload Section -->
      <section class="upload-section card">
        <h2 class="section-title">
          <span class="section-icon">📁</span> 上傳數據集
        </h2>

        <div
          class="upload-zone"
          :class="{ 'upload-zone--dragging': isDragging, 'upload-zone--disabled': isProcessing }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop"
          @click="!isProcessing && $refs.fileInput.click()"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".csv"
            class="file-input-hidden"
            @change="onFileChange"
            :disabled="isProcessing"
          />
          <div v-if="!selectedFile" class="upload-placeholder">
            <span class="upload-icon">📂</span>
            <p class="upload-text">拖曳 CSV 文件至此，或 <span class="upload-link">點擊選擇</span></p>
            <p class="upload-hint">僅支援 .csv 格式</p>
          </div>
          <div v-else class="upload-file-info">
            <span class="file-icon">📄</span>
            <div>
              <p class="file-name">{{ selectedFile.name }}</p>
              <p class="file-size">{{ formatFileSize(selectedFile.size) }}</p>
            </div>
            <button v-if="!isProcessing" class="btn-remove" @click.stop="removeFile">✕</button>
          </div>
        </div>

        <!-- Progress Bar -->
        <div v-if="isProcessing || uploadProgress > 0" class="progress-section">
          <div class="progress-header">
            <span class="progress-label">{{ progressLabel }}</span>
            <span class="progress-pct">{{ Math.round(uploadProgress) }}%</span>
          </div>
          <div class="progress-bar-track">
            <div
              class="progress-bar-fill"
              :class="{ 'progress-bar-fill--pulse': isPolling }"
              :style="{ width: uploadProgress + '%' }"
            ></div>
          </div>
        </div>

        <button
          class="btn-analyze"
          :disabled="!selectedFile || isProcessing"
          @click="startAnalysis"
        >
          <span v-if="!isProcessing">🚀 開始分析</span>
          <span v-else class="btn-loading">
            <svg class="spin-icon" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="60" stroke-dashoffset="20"/>
            </svg>
            分析中…
          </span>
        </button>
      </section>

      <!-- Two-column layout: Log + Stats -->
      <div v-if="isProcessing || results.length > 0" class="info-row">
        <!-- Detection Log -->
        <section class="log-section card">
          <h2 class="section-title">
            <span class="section-icon">🖥️</span> 偵查日誌
            <span v-if="isPolling" class="live-badge">LIVE</span>
          </h2>
          <div ref="logContainer" class="log-window">
            <div v-for="(entry, idx) in logs" :key="idx" class="log-entry" :class="'log-entry--' + entry.level">
              <span class="log-time">{{ entry.time }}</span>
              <span class="log-level-tag">{{ entry.level.toUpperCase() }}</span>
              <span class="log-msg">{{ entry.message }}</span>
            </div>
            <div v-if="isPolling" class="log-cursor">▌</div>
          </div>
        </section>

        <!-- Summary Stats -->
        <section v-if="results.length > 0" class="stats-section card">
          <h2 class="section-title">
            <span class="section-icon">📊</span> 風險統計
          </h2>
          <div class="stats-grid">
            <div class="stat-card stat-card--total">
              <p class="stat-value">{{ results.length }}</p>
              <p class="stat-label">總筆數</p>
            </div>
            <div class="stat-card stat-card--red">
              <p class="stat-value">{{ riskCounts.RED }}</p>
              <p class="stat-label">高風險 🔴</p>
            </div>
            <div class="stat-card stat-card--yellow">
              <p class="stat-value">{{ riskCounts.YELLOW }}</p>
              <p class="stat-label">中風險 🟡</p>
            </div>
            <div class="stat-card stat-card--blue">
              <p class="stat-value">{{ riskCounts.BLUE }}</p>
              <p class="stat-label">低風險 🔵</p>
            </div>
          </div>
        </section>
      </div>

      <!-- Results Table -->
      <section v-if="results.length > 0" class="results-section card">
        <div class="results-header">
          <h2 class="section-title">
            <span class="section-icon">📋</span> 分析結果
          </h2>
          <div class="results-controls">
            <input
              v-model="filterText"
              type="text"
              class="filter-input"
              placeholder="搜尋內容…"
            />
            <select v-model="filterRisk" class="filter-select">
              <option value="">全部風險</option>
              <option value="RED">高風險 🔴</option>
              <option value="YELLOW">中風險 🟡</option>
              <option value="BLUE">低風險 🔵</option>
            </select>
          </div>
        </div>

        <div class="table-wrapper">
          <table class="results-table">
            <thead>
              <tr>
                <th class="th-index">#</th>
                <th
                  v-for="col in tableColumns"
                  :key="col.key"
                  class="th-col"
                  @click="sortBy(col.key)"
                >
                  {{ col.label }}
                  <span class="sort-icon">
                    {{ sortKey === col.key ? (sortDir === 'asc' ? '▲' : '▼') : '⇅' }}
                  </span>
                </th>
                <th class="th-risk">風險等級</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, idx) in filteredResults"
                :key="idx"
                class="result-row"
                :class="riskRowClass(row.risk_level)"
              >
                <td class="td-index">{{ idx + 1 }}</td>
                <td v-for="col in tableColumns" :key="col.key" class="td-cell">
                  <span class="cell-content" :title="String(row[col.key] ?? '')">
                    {{ truncate(String(row[col.key] ?? '—'), 80) }}
                  </span>
                </td>
                <td class="td-risk">
                  <span class="risk-badge" :class="'risk-badge--' + (row.risk_level || '').toLowerCase()">
                    {{ riskLabel(row.risk_level) }}
                  </span>
                </td>
              </tr>
              <tr v-if="filteredResults.length === 0">
                <td :colspan="tableColumns.length + 2" class="td-empty">無符合條件的結果</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="results-count">顯示 {{ filteredResults.length }} / {{ results.length }} 筆</p>
      </section>
    </main>

    <!-- Error Toast -->
    <Transition name="toast">
      <div v-if="errorMessage" class="error-toast">
        <span>⚠️ {{ errorMessage }}</span>
        <button class="toast-close" @click="errorMessage = ''">✕</button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'
import axios from 'axios'

// ── Configuration ──────────────────────────────────────────────
const API_URL = 'https://your-api-gateway-url.execute-api.ap-northeast-1.amazonaws.com/prod'
const POLL_INTERVAL_MS = 2000   // 2 s — respects Bedrock 1 RPS limit
const MAX_POLL_RETRIES = 150    // 5 minutes max

// ── Reactive State ─────────────────────────────────────────────
const fileInput    = ref(null)
const logContainer = ref(null)

const selectedFile   = ref(null)
const isDragging     = ref(false)
const isProcessing   = ref(false)
const isPolling      = ref(false)
const uploadProgress = ref(0)
const progressLabel  = ref('上傳中…')
const results        = ref([])
const logs           = ref([])
const errorMessage   = ref('')
const filterText     = ref('')
const filterRisk     = ref('')
const sortKey        = ref('')
const sortDir        = ref('asc')

let pollTimer  = null
let pollCount  = 0
let jobId      = null

// ── System Status ──────────────────────────────────────────────
const systemStatus = computed(() => {
  if (isPolling.value)   return { text: 'ANALYZING',  class: 'status--analyzing' }
  if (isProcessing.value) return { text: 'UPLOADING', class: 'status--uploading' }
  if (results.value.length > 0) return { text: 'COMPLETE', class: 'status--complete' }
  return { text: 'READY', class: 'status--ready' }
})

// ── Risk Counts ────────────────────────────────────────────────
const riskCounts = computed(() => ({
  RED:    results.value.filter(r => r.risk_level === 'RED').length,
  YELLOW: results.value.filter(r => r.risk_level === 'YELLOW').length,
  BLUE:   results.value.filter(r => r.risk_level === 'BLUE').length,
}))

// ── Table Columns (derived from first result row, excluding risk_level) ──
const tableColumns = computed(() => {
  if (!results.value.length) return []
  return Object.keys(results.value[0])
    .filter(k => k !== 'risk_level')
    .map(k => ({ key: k, label: k.replace(/_/g, ' ').toUpperCase() }))
})

// ── Filtered + Sorted Results ──────────────────────────────────
const filteredResults = computed(() => {
  let list = results.value
  if (filterRisk.value) {
    list = list.filter(r => r.risk_level === filterRisk.value)
  }
  if (filterText.value.trim()) {
    const q = filterText.value.toLowerCase()
    list = list.filter(r =>
      Object.values(r).some(v => String(v).toLowerCase().includes(q))
    )
  }
  if (sortKey.value) {
    list = [...list].sort((a, b) => {
      const va = String(a[sortKey.value] ?? '')
      const vb = String(b[sortKey.value] ?? '')
      return sortDir.value === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va)
    })
  }
  return list
})

// ── File Handling ──────────────────────────────────────────────
function onFileChange(e) {
  const file = e.target.files[0]
  if (file) setFile(file)
}

function onDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.name.endsWith('.csv')) setFile(file)
  else addLog('warn', '僅支援 .csv 格式')
}

function setFile(file) {
  selectedFile.value = file
  uploadProgress.value = 0
  results.value = []
  logs.value = []
  addLog('info', `已選擇文件：${file.name}（${formatFileSize(file.size)}）`)
}

function removeFile() {
  selectedFile.value = null
  uploadProgress.value = 0
  if (fileInput.value) fileInput.value.value = ''
}

// ── Main Analysis Flow ─────────────────────────────────────────
async function startAnalysis() {
  if (!selectedFile.value || isProcessing.value) return

  isProcessing.value = true
  uploadProgress.value = 0
  results.value = []
  errorMessage.value = ''
  addLog('info', '開始上傳文件至後端…')

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    // Step 1 — Upload CSV
    progressLabel.value = '上傳中…'
    const uploadRes = await axios.post(`${API_URL}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress(e) {
        uploadProgress.value = Math.round((e.loaded / e.total) * 50) // 0–50 %
      },
    })

    jobId = uploadRes.data?.job_id
    if (!jobId) throw new Error('後端未回傳 job_id')

    addLog('info', `上傳成功，任務 ID：${jobId}`)
    addLog('info', 'Bedrock 分析引擎啟動，輪詢狀態中…')

    // Step 2 — Poll for completion
    progressLabel.value = 'AI 分析中…'
    await pollForResult(jobId)

  } catch (err) {
    handleError(err)
  } finally {
    isProcessing.value = false
    isPolling.value = false
  }
}

// ── Polling Mechanism ──────────────────────────────────────────
function pollForResult(id) {
  pollCount = 0
  return new Promise((resolve, reject) => {
    isPolling.value = true

    const tick = async () => {
      if (pollCount >= MAX_POLL_RETRIES) {
        reject(new Error('分析逾時，請稍後再試'))
        return
      }
      pollCount++

      try {
        const res = await axios.get(`${API_URL}/status/${id}`)
        const { status, progress, current_item, results: data } = res.data

        // Update fake progress (50 % → 99 % during polling)
        uploadProgress.value = Math.min(99, 50 + Math.round((pollCount / MAX_POLL_RETRIES) * 49))

        if (current_item) {
          addLog('info', `[${pollCount}] 正在分析：「${truncate(current_item, 60)}」`)
        }

        if (status === 'completed') {
          uploadProgress.value = 100
          progressLabel.value = '分析完成！'
          results.value = Array.isArray(data) ? data : []
          addLog('success', `分析完成，共 ${results.value.length} 筆結果`)
          addLog('success', `高風險：${riskCounts.value.RED} ／ 中風險：${riskCounts.value.YELLOW} ／ 低風險：${riskCounts.value.BLUE}`)
          isPolling.value = false
          resolve()
        } else if (status === 'failed') {
          reject(new Error(res.data.message || '後端分析失敗'))
        } else {
          // Still processing — schedule next poll
          pollTimer = setTimeout(tick, POLL_INTERVAL_MS)
        }
      } catch (err) {
        // Network errors during polling — retry up to limit
        addLog('warn', `輪詢失敗（第 ${pollCount} 次），重試中…`)
        pollTimer = setTimeout(tick, POLL_INTERVAL_MS)
      }
    }

    pollTimer = setTimeout(tick, POLL_INTERVAL_MS)
  })
}

// ── Helpers ────────────────────────────────────────────────────
function addLog(level, message) {
  const now = new Date()
  const time = now.toTimeString().slice(0, 8)
  logs.value.push({ time, level, message })
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}

function handleError(err) {
  const msg = err.response?.data?.message || err.message || '未知錯誤'
  errorMessage.value = msg
  addLog('error', `錯誤：${msg}`)
  uploadProgress.value = 0
  clearTimeout(pollTimer)
  isPolling.value = false
  setTimeout(() => { errorMessage.value = '' }, 6000)
}

function riskRowClass(level) {
  const map = { RED: 'row--red', YELLOW: 'row--yellow', BLUE: 'row--blue' }
  return map[level] || ''
}

function riskLabel(level) {
  const map = { RED: '🔴 高風險', YELLOW: '🟡 中風險', BLUE: '🔵 低風險' }
  return map[level] || level || '—'
}

function sortBy(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

function truncate(str, len) {
  return str.length > len ? str.slice(0, len) + '…' : str
}

// Auto-dismiss error
watch(errorMessage, val => {
  if (val) setTimeout(() => { errorMessage.value = '' }, 6000)
})
</script>

<style scoped>
/* ── Design Tokens ─────────────────────────────────────── */
:root {
  --c-bg:        #0d1117;
  --c-surface:   #161b22;
  --c-border:    #30363d;
  --c-text:      #e6edf3;
  --c-muted:     #8b949e;
  --c-accent:    #58a6ff;
  --c-green:     #3fb950;
  --c-red:       #f85149;
  --c-yellow:    #d29922;
  --radius:      12px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Layout ────────────────────────────────────────────── */
.dashboard-container {
  min-height: 100vh;
  background: #0d1117;
  color: #e6edf3;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  padding-bottom: 40px;
}

.dashboard-main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 12px;
  padding: 24px;
}

/* ── Header ────────────────────────────────────────────── */
.dashboard-header {
  background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
  border-bottom: 1px solid #30363d;
  padding: 20px 32px;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
}
.header-content {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-logo { display: flex; align-items: center; gap: 14px; }
.logo-icon { font-size: 2rem; }
.header-title { font-size: 1.4rem; font-weight: 700; color: #58a6ff; letter-spacing: -0.5px; }
.header-subtitle { font-size: 0.78rem; color: #8b949e; margin-top: 2px; }

/* ── Status Badge ──────────────────────────────────────── */
.status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 1px;
  border: 1px solid;
}
.status-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: currentColor;
}
.status--ready     { color: #8b949e;  border-color: #30363d;  background: rgba(139,148,158,.1); }
.status--uploading { color: #58a6ff;  border-color: #58a6ff4d; background: rgba(88,166,255,.08); }
.status--analyzing { color: #d29922;  border-color: #d2992244; background: rgba(210,153,34,.08);
  animation: pulse-badge 1.4s ease-in-out infinite; }
.status--complete  { color: #3fb950;  border-color: #3fb95044; background: rgba(63,185,80,.08); }

@keyframes pulse-badge {
  0%, 100% { opacity: 1; }
  50%       { opacity: .6; }
}

/* ── Section titles ────────────────────────────────────── */
.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #e6edf3;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.section-icon { font-size: 1.1rem; }
.live-badge {
  margin-left: 6px;
  background: #f85149;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 6px;
  letter-spacing: 1px;
  animation: pulse-badge 1s ease-in-out infinite;
}

/* ── Upload Zone ───────────────────────────────────────── */
.upload-zone {
  border: 2px dashed #30363d;
  border-radius: 10px;
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: border-color .2s, background .2s;
  background: rgba(255,255,255,.01);
  margin-bottom: 16px;
}
.upload-zone:hover:not(.upload-zone--disabled) {
  border-color: #58a6ff;
  background: rgba(88,166,255,.04);
}
.upload-zone--dragging {
  border-color: #58a6ff;
  background: rgba(88,166,255,.08);
}
.upload-zone--disabled { opacity: .5; cursor: not-allowed; }
.file-input-hidden { display: none; }

.upload-icon { font-size: 2.4rem; display: block; margin-bottom: 8px; }
.upload-text { color: #e6edf3; margin-bottom: 4px; }
.upload-link { color: #58a6ff; text-decoration: underline; }
.upload-hint { font-size: 0.78rem; color: #8b949e; }

.upload-file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
}
.file-icon { font-size: 1.8rem; }
.file-name { font-weight: 600; color: #e6edf3; }
.file-size { font-size: 0.78rem; color: #8b949e; margin-top: 2px; }
.btn-remove {
  background: none;
  border: 1px solid #f8514944;
  color: #f85149;
  border-radius: 6px;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background .15s;
}
.btn-remove:hover { background: rgba(248,81,73,.15); }

/* ── Progress Bar ──────────────────────────────────────── */
.progress-section { margin-bottom: 16px; }
.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
  color: #8b949e;
  margin-bottom: 8px;
}
.progress-pct { font-weight: 600; color: #58a6ff; }
.progress-bar-track {
  height: 8px;
  background: #21262d;
  border-radius: 99px;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, #1f6feb, #58a6ff);
  transition: width .4s ease;
}
.progress-bar-fill--pulse {
  animation: bar-shimmer 2s linear infinite;
  background-size: 200% 100%;
  background-image: linear-gradient(90deg, #1f6feb 0%, #58a6ff 50%, #1f6feb 100%);
}
@keyframes bar-shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ── Analyze Button ────────────────────────────────────── */
.btn-analyze {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #1f6feb, #388bfd);
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity .2s, transform .1s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-analyze:hover:not(:disabled) { opacity: .88; transform: translateY(-1px); }
.btn-analyze:disabled { opacity: .35; cursor: not-allowed; }
.btn-loading { display: flex; align-items: center; gap: 8px; }
.spin-icon {
  width: 18px; height: 18px;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Info Row ──────────────────────────────────────────── */
.info-row {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
}
@media (max-width: 900px) {
  .info-row { grid-template-columns: 1fr; }
}

/* ── Log Window ────────────────────────────────────────── */
.log-section { display: flex; flex-direction: column; }
.log-window {
  flex: 1;
  background: #010409;
  border: 1px solid #21262d;
  border-radius: 8px;
  padding: 14px;
  height: 260px;
  overflow-y: auto;
  font-family: 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
  font-size: 0.78rem;
  scroll-behavior: smooth;
}
.log-window::-webkit-scrollbar { width: 4px; }
.log-window::-webkit-scrollbar-thumb { background: #30363d; border-radius: 2px; }

.log-entry {
  display: flex;
  gap: 8px;
  margin-bottom: 5px;
  line-height: 1.5;
}
.log-time { color: #3fb950; flex-shrink: 0; }
.log-level-tag {
  flex-shrink: 0;
  font-weight: 700;
  min-width: 52px;
}
.log-entry--info  .log-level-tag { color: #58a6ff; }
.log-entry--warn  .log-level-tag { color: #d29922; }
.log-entry--error .log-level-tag { color: #f85149; }
.log-entry--success .log-level-tag { color: #3fb950; }
.log-msg { color: #adbac7; word-break: break-all; }
.log-cursor { color: #58a6ff; animation: blink .8s step-end infinite; }
@keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0; } }

/* ── Stats ─────────────────────────────────────────────── */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.stat-card {
  background: #21262d;
  border-radius: 10px;
  padding: 16px;
  text-align: center;
  border: 1px solid #30363d;
}
.stat-value { font-size: 2rem; font-weight: 800; line-height: 1.1; }
.stat-label { font-size: 0.75rem; color: #8b949e; margin-top: 4px; }
.stat-card--total  .stat-value { color: #e6edf3; }
.stat-card--red    .stat-value { color: #f85149; }
.stat-card--yellow .stat-value { color: #d29922; }
.stat-card--blue   .stat-value { color: #58a6ff; }

/* ── Results Table ─────────────────────────────────────── */
.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}
.results-controls { display: flex; gap: 10px; }
.filter-input, .filter-select {
  background: #21262d;
  border: 1px solid #30363d;
  border-radius: 6px;
  color: #e6edf3;
  padding: 6px 12px;
  font-size: 0.85rem;
  outline: none;
  transition: border-color .15s;
}
.filter-input:focus, .filter-select:focus { border-color: #58a6ff; }
.filter-select { cursor: pointer; }

.table-wrapper { overflow-x: auto; border-radius: 8px; border: 1px solid #21262d; }
.results-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.83rem;
}
.results-table thead { background: #21262d; }
.th-index, .th-col, .th-risk {
  padding: 10px 14px;
  text-align: left;
  color: #8b949e;
  font-weight: 600;
  font-size: 0.75rem;
  letter-spacing: .5px;
  text-transform: uppercase;
  white-space: nowrap;
  border-bottom: 1px solid #30363d;
}
.th-col { cursor: pointer; user-select: none; }
.th-col:hover { color: #58a6ff; }
.sort-icon { margin-left: 4px; font-size: 0.65rem; }

/* Row color coding — core requirement */
.result-row { border-bottom: 1px solid #21262d; transition: filter .15s; }
.result-row:hover { filter: brightness(1.12); }

.row--red    { background: rgba(248, 81, 73, 0.10); }
.row--yellow { background: rgba(210, 153, 34, 0.10); }
.row--blue   { background: rgba(88, 166, 255, 0.08); }

.td-index { padding: 10px 14px; color: #8b949e; font-size: 0.75rem; white-space: nowrap; }
.td-cell  { padding: 10px 14px; color: #e6edf3; max-width: 320px; }
.cell-content { display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.td-empty { padding: 24px; text-align: center; color: #8b949e; }

.td-risk { padding: 10px 14px; white-space: nowrap; }
.risk-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
}
.risk-badge--red    { background: rgba(248,81,73,.2);   color: #f85149; border: 1px solid rgba(248,81,73,.4); }
.risk-badge--yellow { background: rgba(210,153,34,.2);  color: #d29922; border: 1px solid rgba(210,153,34,.4); }
.risk-badge--blue   { background: rgba(88,166,255,.15); color: #58a6ff; border: 1px solid rgba(88,166,255,.35); }

.results-count { font-size: 0.78rem; color: #8b949e; margin-top: 10px; text-align: right; }

/* ── Error Toast ───────────────────────────────────────── */
.error-toast {
  position: fixed;
  bottom: 28px;
  right: 28px;
  background: #161b22;
  border: 1px solid #f85149;
  color: #f85149;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.88rem;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,.5);
  z-index: 999;
  max-width: 420px;
}
.toast-close {
  background: none;
  border: none;
  color: #f85149;
  cursor: pointer;
  font-size: 0.9rem;
  flex-shrink: 0;
}
.toast-enter-active, .toast-leave-active { transition: opacity .3s, transform .3s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(12px); }
</style>
