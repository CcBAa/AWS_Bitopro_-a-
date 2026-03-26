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
        <div v-if="isProcessing" class="progress-section">
          <div class="progress-header">
            <span class="progress-label">{{ progressLabel }}</span>
            <span class="progress-pct">{{ Math.round(uploadProgress) }}%</span>
          </div>
          <div class="progress-bar-track">
            <div
              class="progress-bar-fill progress-bar-fill--pulse"
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
            <span v-if="isProcessing" class="live-badge">LIVE</span>
          </h2>
          <div ref="logContainer" class="log-window">
            <div v-for="(entry, idx) in logs" :key="idx" class="log-entry" :class="'log-entry--' + entry.level">
              <span class="log-time">{{ entry.time }}</span>
              <span class="log-level-tag">{{ entry.level.toUpperCase() }}</span>
              <span class="log-msg">{{ entry.message }}</span>
            </div>
            <div v-if="isProcessing" class="log-cursor">▌</div>
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
            <div class="stat-card stat-card--critical">
              <p class="stat-value">{{ riskCounts.CRITICAL }}</p>
              <p class="stat-label">極高風險 🔴</p>
            </div>
            <div class="stat-card stat-card--suspicious">
              <p class="stat-value">{{ riskCounts.SUSPICIOUS }}</p>
              <p class="stat-label">可疑交易 🟠</p>
            </div>
            <div class="stat-card stat-card--normal">
              <p class="stat-value">{{ riskCounts.NORMAL }}</p>
              <p class="stat-label">正常 🔵</p>
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
              <option value="CRITICAL">極高風險 🔴</option>
              <option value="SUSPICIOUS">可疑交易 🟠</option>
              <option value="NORMAL">正常 🔵</option>
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
                <th class="th-report">AI 報告</th>
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
                <td class="td-report">
                  <button
                    v-if="row.sar_report"
                    class="btn-report"
                    :class="{ 'btn-report--critical': row.is_extreme_risk }"
                    @click="openModal(row)"
                  >
                    🔍 查看報告
                  </button>
                  <span v-else class="no-report">—</span>
                </td>
              </tr>
              <tr v-if="filteredResults.length === 0">
                <td :colspan="tableColumns.length + 3" class="td-empty">無符合條件的結果</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="results-count">顯示 {{ filteredResults.length }} / {{ results.length }} 筆</p>
      </section>
    </main>

    <!-- SAR Report Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modalRow" class="modal-overlay" @click.self="closeModal">
          <div class="modal-box">
            <!-- Blinking extreme risk warning -->
            <div v-if="modalRow.is_extreme_risk" class="modal-extreme-warning">
              <span class="warning-blink">⚠</span>
              系統判定：極高洗錢/操縱風險
              <span class="warning-blink">⚠</span>
            </div>

            <div class="modal-header">
              <div class="modal-title-group">
                <h3 class="modal-title">AI 偵查報告</h3>
                <span class="modal-badge" :class="'modal-badge--' + (modalRow.risk_level || '').toLowerCase()">
                  {{ riskLabel(modalRow.risk_level) }}
                </span>
              </div>
              <button class="modal-close" @click="closeModal">✕</button>
            </div>

            <div class="modal-body">
              <div class="markdown-content" v-html="renderedReport"></div>
            </div>

            <div class="modal-footer">
              <button class="btn-modal-close" @click="closeModal">關閉報告</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Toast Stack -->
    <div class="toast-stack">
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="toast-item"
          :class="'toast-item--' + t.type"
        >
          <span class="toast-icon">{{ t.type === 'warning' ? '🚨' : '⚠️' }}</span>
          <span class="toast-msg">{{ t.message }}</span>
          <button class="toast-close" @click="dismissToast(t.id)">✕</button>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

// ── Configuration ──────────────────────────────────────────────
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000'

// ── Reactive State ─────────────────────────────────────────────
const fileInput    = ref(null)
const logContainer = ref(null)

const selectedFile   = ref(null)
const isDragging     = ref(false)
const isProcessing   = ref(false)
const uploadProgress = ref(0)
const progressLabel  = ref('分析中…')
const results        = ref([])
const logs           = ref([])
const filterText     = ref('')
const filterRisk     = ref('')
const sortKey        = ref('')
const sortDir        = ref('asc')

// Modal
const modalRow = ref(null)

// Toast system
const toasts = ref([])
let toastIdCounter = 0

let progressTimer = null

// ── System Status ──────────────────────────────────────────────
const systemStatus = computed(() => {
  if (isProcessing.value)        return { text: 'ANALYZING',  class: 'status--analyzing' }
  if (results.value.length > 0)  return { text: 'COMPLETE',   class: 'status--complete' }
  return { text: 'READY', class: 'status--ready' }
})

// ── Risk Counts ────────────────────────────────────────────────
const riskCounts = computed(() => ({
  CRITICAL:   results.value.filter(r => r.risk_level === 'CRITICAL').length,
  SUSPICIOUS: results.value.filter(r => r.risk_level === 'SUSPICIOUS').length,
  NORMAL:     results.value.filter(r => r.risk_level === 'NORMAL').length,
}))

// ── Table Columns ──────────────────────────────────────────────
const EXCLUDED_COLS = new Set(['risk_level', 'sar_report', 'ai_prediction', 'is_extreme_risk'])

const tableColumns = computed(() => {
  if (!results.value.length) return []
  return Object.keys(results.value[0])
    .filter(k => !EXCLUDED_COLS.has(k))
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

// ── Modal ──────────────────────────────────────────────────────
const renderedReport = computed(() => {
  if (!modalRow.value?.sar_report) return ''
  return marked.parse(modalRow.value.sar_report)
})

function openModal(row) {
  modalRow.value = row
  document.body.style.overflow = 'hidden'
}

function closeModal() {
  modalRow.value = null
  document.body.style.overflow = ''
}

// ── Toast System ───────────────────────────────────────────────
function pushToast(message, type = 'error', duration = 6000) {
  const id = ++toastIdCounter
  toasts.value.push({ id, message, type })
  setTimeout(() => dismissToast(id), duration)
}

function dismissToast(id) {
  toasts.value = toasts.value.filter(t => t.id !== id)
}

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
  uploadProgress.value = 5
  results.value = []
  progressLabel.value = '上傳至 AI 分析引擎…'
  addLog('info', '讀取 CSV 文件內容…')

  // Simulate progress animation while awaiting response
  progressTimer = setInterval(() => {
    if (uploadProgress.value < 85) {
      uploadProgress.value = Math.min(85, uploadProgress.value + Math.random() * 4)
    }
  }, 400)

  try {
    const csvText = await selectedFile.value.text()
    addLog('info', `POST → ${API_URL}  (Content-Type: text/csv)`)

    const res = await axios.post(API_URL, csvText, {
      headers: { 'Content-Type': 'text/csv' },
      timeout: 120_000,
    })

    const predictions = res.data?.predictions
    if (!Array.isArray(predictions)) {
      throw new Error(`後端回傳格式異常：缺少 predictions 陣列`)
    }

    // Map predictions → enrich with risk_level
    results.value = predictions.map(p => ({
      ...p,
      risk_level: classifyRisk(p),
    }))

    uploadProgress.value = 100
    progressLabel.value = '分析完成！'
    addLog('success', `分析完成，共 ${results.value.length} 筆結果`)
    addLog('success',
      `CRITICAL：${riskCounts.value.CRITICAL} ／ SUSPICIOUS：${riskCounts.value.SUSPICIOUS} ／ NORMAL：${riskCounts.value.NORMAL}`)

    // Trigger extreme risk toast if any
    const extremeCount = riskCounts.value.CRITICAL
    if (extremeCount > 0) {
      pushToast(`偵測到 ${extremeCount} 筆極高風險交易，請立即查核`, 'warning', 10000)
      addLog('warn', `[!] 偵測到 ${extremeCount} 筆極高風險交易`)
    }

  } catch (err) {
    handleError(err)
  } finally {
    clearInterval(progressTimer)
    isProcessing.value = false
  }
}

// ── Risk Classification ────────────────────────────────────────
function classifyRisk(p) {
  if (p.ai_prediction === 1 && p.is_extreme_risk === true) return 'CRITICAL'
  if (p.ai_prediction === 1) return 'SUSPICIOUS'
  return 'NORMAL'
}

// ── Helpers ────────────────────────────────────────────────────
function addLog(level, message) {
  const time = new Date().toTimeString().slice(0, 8)
  logs.value.push({ time, level, message })
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}

function handleError(err) {
  let msg = err.response?.data?.message || err.message || '未知錯誤'

  if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
    msg = 'API 請求逾時（120s），請確認後端服務狀態'
  } else if (err.code === 'ERR_NETWORK' || err.message?.includes('Network Error')) {
    msg = '網路錯誤 / CORS 阻擋：請確認 API 端點與 CORS 設定'
  }

  addLog('error', `錯誤：${msg}`)
  pushToast(msg, 'error')
  uploadProgress.value = 0
}

function riskRowClass(level) {
  const map = { CRITICAL: 'row--critical', SUSPICIOUS: 'row--suspicious', NORMAL: 'row--normal' }
  return map[level] || ''
}

function riskLabel(level) {
  const map = { CRITICAL: '🔴 CRITICAL', SUSPICIOUS: '🟠 SUSPICIOUS', NORMAL: '🔵 NORMAL' }
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
  --c-orange:    #e07b39;
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
  border: 1px solid rgba(248,81,73,.4);
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
.log-entry--info    .log-level-tag { color: #58a6ff; }
.log-entry--warn    .log-level-tag { color: #d29922; }
.log-entry--error   .log-level-tag { color: #f85149; }
.log-entry--success .log-level-tag { color: #3fb950; }
.log-msg { color: #adbac7; word-break: break-all; }
.log-cursor { color: #58a6ff; animation: blink .8s step-end infinite; }
@keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0; } }

/* ── Stats (three tiers) ───────────────────────────────── */
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
.stat-card--total      .stat-value { color: #e6edf3; }
.stat-card--critical   .stat-value { color: #f85149; }
.stat-card--suspicious .stat-value { color: #e07b39; }
.stat-card--normal     .stat-value { color: #58a6ff; }

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
.th-index, .th-col, .th-risk, .th-report {
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

/* Row color coding — three tiers */
.result-row { border-bottom: 1px solid #21262d; transition: filter .15s; }
.result-row:hover { filter: brightness(1.12); }

.row--critical   { background: rgba(248, 81,  73, 0.12); }
.row--suspicious { background: rgba(224, 123, 57, 0.10); }
.row--normal     { background: rgba(88,  166, 255, 0.06); }

.td-index  { padding: 10px 14px; color: #8b949e; font-size: 0.75rem; white-space: nowrap; }
.td-cell   { padding: 10px 14px; color: #e6edf3; max-width: 320px; }
.cell-content { display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.td-empty  { padding: 24px; text-align: center; color: #8b949e; }
.td-risk   { padding: 10px 14px; white-space: nowrap; }
.td-report { padding: 10px 14px; white-space: nowrap; }

.risk-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
}
.risk-badge--critical   { background: rgba(248,81,73,.2);   color: #f85149; border: 1px solid rgba(248,81,73,.4); }
.risk-badge--suspicious { background: rgba(224,123,57,.2);  color: #e07b39; border: 1px solid rgba(224,123,57,.4); }
.risk-badge--normal     { background: rgba(88,166,255,.15); color: #58a6ff; border: 1px solid rgba(88,166,255,.35); }

/* ── Report Button ─────────────────────────────────────── */
.btn-report {
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid rgba(88,166,255,.4);
  background: rgba(88,166,255,.08);
  color: #58a6ff;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: background .15s, border-color .15s;
  white-space: nowrap;
}
.btn-report:hover { background: rgba(88,166,255,.18); }
.btn-report--critical {
  border-color: rgba(248,81,73,.5);
  background: rgba(248,81,73,.1);
  color: #f85149;
}
.btn-report--critical:hover { background: rgba(248,81,73,.2); }
.no-report { color: #30363d; font-size: 0.78rem; }

.results-count { font-size: 0.78rem; color: #8b949e; margin-top: 10px; text-align: right; }

/* ── Modal ─────────────────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(1, 4, 9, 0.80);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 500;
  padding: 20px;
}

.modal-box {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 16px;
  width: 100%;
  max-width: 720px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 64px rgba(0,0,0,.7);
  overflow: hidden;
}

/* Extreme risk warning banner */
.modal-extreme-warning {
  background: linear-gradient(90deg, #450a0a, #7f1d1d, #450a0a);
  background-size: 200% 100%;
  animation: warning-sweep 2s linear infinite;
  color: #fca5a5;
  font-weight: 700;
  font-size: 0.9rem;
  text-align: center;
  padding: 10px 20px;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(248,81,73,.4);
}
@keyframes warning-sweep {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.warning-blink {
  display: inline-block;
  animation: blink .6s step-end infinite;
  margin: 0 6px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid #21262d;
  flex-shrink: 0;
}
.modal-title-group { display: flex; align-items: center; gap: 12px; }
.modal-title { font-size: 1.05rem; font-weight: 700; color: #e6edf3; }

.modal-badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}
.modal-badge--critical   { background: rgba(248,81,73,.2);   color: #f85149; border: 1px solid rgba(248,81,73,.4); }
.modal-badge--suspicious { background: rgba(224,123,57,.2);  color: #e07b39; border: 1px solid rgba(224,123,57,.4); }
.modal-badge--normal     { background: rgba(88,166,255,.15); color: #58a6ff; border: 1px solid rgba(88,166,255,.35); }

.modal-close {
  background: none;
  border: 1px solid #30363d;
  color: #8b949e;
  border-radius: 6px;
  width: 32px; height: 32px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background .15s, color .15s;
  flex-shrink: 0;
}
.modal-close:hover { background: rgba(248,81,73,.1); color: #f85149; border-color: rgba(248,81,73,.4); }

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
}
.modal-body::-webkit-scrollbar { width: 4px; }
.modal-body::-webkit-scrollbar-thumb { background: #30363d; border-radius: 2px; }

/* Markdown content styles */
.markdown-content {
  color: #c9d1d9;
  line-height: 1.75;
  font-size: 0.9rem;
}
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  color: #e6edf3;
  font-weight: 700;
  margin: 20px 0 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid #21262d;
}
.markdown-content :deep(h1) { font-size: 1.2rem; }
.markdown-content :deep(h2) { font-size: 1.05rem; }
.markdown-content :deep(h3) { font-size: 0.95rem; border-bottom: none; }
.markdown-content :deep(p)  { margin-bottom: 12px; }
.markdown-content :deep(strong) { color: #f0f6fc; font-weight: 700; }
.markdown-content :deep(em) { color: #d2a679; font-style: italic; }
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 20px;
  margin-bottom: 12px;
}
.markdown-content :deep(li) { margin-bottom: 4px; }
.markdown-content :deep(blockquote) {
  border-left: 3px solid #58a6ff;
  padding: 8px 16px;
  margin: 12px 0;
  background: rgba(88,166,255,.06);
  border-radius: 0 6px 6px 0;
  color: #8b949e;
}
.markdown-content :deep(code) {
  background: #010409;
  border: 1px solid #30363d;
  border-radius: 4px;
  padding: 1px 6px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.85em;
  color: #79c0ff;
}
.markdown-content :deep(pre) {
  background: #010409;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 14px;
  overflow-x: auto;
  margin-bottom: 12px;
}
.markdown-content :deep(pre code) {
  background: none;
  border: none;
  padding: 0;
}
.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid #21262d;
  margin: 20px 0;
}
.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 12px;
  font-size: 0.85rem;
}
.markdown-content :deep(th) {
  background: #21262d;
  padding: 8px 12px;
  text-align: left;
  color: #8b949e;
  font-weight: 600;
  border-bottom: 1px solid #30363d;
}
.markdown-content :deep(td) {
  padding: 8px 12px;
  border-bottom: 1px solid #21262d;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #21262d;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}
.btn-modal-close {
  padding: 8px 20px;
  border-radius: 8px;
  border: 1px solid #30363d;
  background: #21262d;
  color: #e6edf3;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background .15s;
}
.btn-modal-close:hover { background: #30363d; }

/* Modal transition */
.modal-enter-active, .modal-leave-active {
  transition: opacity .2s ease, transform .2s ease;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
  transform: scale(0.96);
}

/* ── Toast Stack ───────────────────────────────────────── */
.toast-stack {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 600;
  pointer-events: none;
}

.toast-item {
  pointer-events: all;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 500;
  max-width: 400px;
  box-shadow: 0 8px 24px rgba(0,0,0,.5);
  border: 1px solid;
}
.toast-item--error {
  background: #161b22;
  border-color: rgba(248,81,73,.5);
  color: #f85149;
}
.toast-item--warning {
  background: #1c1710;
  border-color: rgba(224,123,57,.5);
  color: #e07b39;
}
.toast-icon { flex-shrink: 0; }
.toast-msg  { flex: 1; line-height: 1.4; }
.toast-close {
  background: none;
  border: none;
  color: currentColor;
  cursor: pointer;
  font-size: 0.9rem;
  flex-shrink: 0;
  opacity: .7;
  padding: 2px;
}
.toast-close:hover { opacity: 1; }

/* TransitionGroup for toast stack */
.toast-enter-active { transition: opacity .3s ease, transform .3s ease; }
.toast-leave-active { transition: opacity .25s ease, transform .25s ease; }
.toast-enter-from   { opacity: 0; transform: translateX(20px); }
.toast-leave-to     { opacity: 0; transform: translateX(20px); }
.toast-move         { transition: transform .3s ease; }
</style>
