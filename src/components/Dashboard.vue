<template>
  <div class="page-bg min-h-screen text-gray-100 pb-16 font-sans">

    <!-- ══════════════════════════════════════════════════
         HEADER
    ══════════════════════════════════════════════════ -->
    <header class="sticky top-0 z-50 header-glass px-8 py-4">
      <div class="max-w-6xl mx-auto flex items-center justify-between">

        <div class="flex items-center gap-4">
          <div class="logo-icon-wrap">
            <span class="text-xl">🔍</span>
          </div>
          <div>
            <h1 class="text-xl font-bold gradient-text tracking-tight">去偽存真 · DisInfo Shield</h1>
            <p class="text-xs text-gray-500 mt-0.5">AI-Powered Disinformation Detection System</p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- ENV 狀態指示 -->
          <span
            class="text-xs font-bold px-3 py-1 rounded-full border"
            :class="apiUrlOk
              ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/8'
              : 'text-red-400 border-red-500/30 bg-red-500/8 animate-pulse'"
          >
            {{ apiUrlOk ? '● ENV OK' : '● ENV MISSING' }}
          </span>

          <!-- 系統狀態 -->
          <div
            class="flex items-center gap-2 px-4 py-1.5 rounded-full border text-xs font-bold tracking-widest"
            :class="statusStyle.cls"
          >
            <span class="w-2 h-2 rounded-full bg-current" :class="{ 'animate-pulse': isProcessing }"></span>
            {{ statusStyle.text }}
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 pt-8 flex flex-col gap-6">

      <!-- ══════════════════════════════════════════════
           UPLOAD CARD
      ══════════════════════════════════════════════ -->
      <section class="card p-6">
        <h2 class="section-title mb-5">
          <span class="section-icon">📁</span> 上傳數據集
        </h2>

        <!-- Drop Zone -->
        <div
          class="drop-zone border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-300 mb-5"
          :class="dropZoneCls"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop"
          @click="!isProcessing && $refs.fileInput.click()"
        >
          <input ref="fileInput" type="file" accept=".csv" class="hidden"
                 :disabled="isProcessing" @change="onFileChange" />

          <template v-if="!selectedFile">
            <p class="text-5xl mb-3 opacity-40">📂</p>
            <p class="text-gray-300 text-sm">
              拖曳 <code class="inline-code">.csv</code> 至此，或
              <span class="text-blue-400 underline underline-offset-2">點擊選擇</span>
            </p>
            <p class="text-xs text-gray-600 mt-2">UTF-8 編碼，支援任意欄位結構</p>
          </template>
          <template v-else>
            <div class="flex items-center justify-center gap-4">
              <span class="text-4xl">📄</span>
              <div class="text-left">
                <p class="font-semibold text-gray-100">{{ selectedFile.name }}</p>
                <p class="text-xs text-gray-500 mt-0.5">{{ fmtSize(selectedFile.size) }}</p>
              </div>
              <button v-if="!isProcessing"
                      class="ml-2 text-xs text-red-400 border border-red-500/30 px-3 py-1 rounded-lg hover:bg-red-500/10 transition-colors"
                      @click.stop="removeFile">✕ 移除</button>
            </div>
          </template>
        </div>

        <!-- Progress Bar -->
        <div v-if="isProcessing || progress > 0" class="mb-5">
          <div class="flex justify-between text-xs mb-2">
            <span class="text-gray-400">{{ progressLabel }}</span>
            <span class="text-blue-400 font-bold tabular-nums">{{ Math.round(progress) }}%</span>
          </div>
          <div class="h-2 bg-gray-800/80 rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-500"
              :class="isProcessing ? 'shimmer' : 'bg-gradient-to-r from-blue-600 to-cyan-400'"
              :style="{ width: progress + '%' }"
            ></div>
          </div>
        </div>

        <!-- Submit Button -->
        <button
          class="w-full py-3 rounded-xl font-semibold text-sm transition-all duration-200 flex items-center justify-center gap-2"
          :class="isProcessing || !selectedFile || !apiUrlOk
            ? 'bg-gray-800/60 text-gray-500 cursor-not-allowed border border-gray-700/50'
            : 'btn-primary'"
          :disabled="isProcessing || !selectedFile || !apiUrlOk"
          @click="startAnalysis"
        >
          <template v-if="!isProcessing">
            🚀 送出分析
          </template>
          <template v-else>
            <span class="flex items-center gap-2">
              <span class="ai-spinner"></span>
              AI 偵辦中…
            </span>
          </template>
        </button>

        <!-- ENV 缺失提示 -->
        <p v-if="!apiUrlOk" class="mt-3 text-xs text-red-400/80 text-center">
          ⚠️ <code class="font-mono text-xs">VITE_API_URL</code> 未設定，請建立 <code class="font-mono text-xs">.env</code> 或至 Amplify 設定環境變數
        </p>
      </section>

      <!-- ══════════════════════════════════════════════
           LOG + STATS ROW
      ══════════════════════════════════════════════ -->
      <div v-if="isProcessing || results.length > 0" class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- 偵查日誌 -->
        <section class="lg:col-span-2 card p-6 flex flex-col">
          <h2 class="section-title mb-3">
            <span class="section-icon">🖥️</span> 偵查日誌
            <span v-if="isProcessing"
                  class="ml-2 text-xs font-black px-2 py-0.5 rounded-md bg-red-500/90 text-white animate-pulse tracking-widest">
              ● LIVE
            </span>
          </h2>
          <div ref="logEl" class="log-window flex-1">
            <div v-for="(e, i) in logs" :key="i" class="log-line">
              <span class="log-time">[{{ e.time }}]</span>
              <span class="log-tag" :class="logTagCls(e.level)">{{ e.level.toUpperCase() }}</span>
              <span class="log-msg">{{ e.message }}</span>
            </div>
            <div v-if="isProcessing" class="log-time animate-pulse mt-1">▌</div>
          </div>
        </section>

        <!-- 風險統計 -->
        <section v-if="results.length > 0" class="card p-6">
          <h2 class="section-title mb-4">
            <span class="section-icon">📊</span> 風險統計
          </h2>
          <div class="grid grid-cols-2 gap-3">
            <div v-for="s in stats" :key="s.label" class="stat-card" :class="s.cardCls">
              <p class="text-3xl font-black leading-none" :class="s.color">{{ s.value }}</p>
              <p class="text-xs mt-2 text-gray-500">{{ s.label }}</p>
            </div>
          </div>
        </section>
      </div>

      <!-- ══════════════════════════════════════════════
           RESULTS TABLE
      ══════════════════════════════════════════════ -->
      <section v-if="results.length > 0" class="card p-6">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-5">
          <h2 class="section-title">
            <span class="section-icon">📋</span> 分析結果
          </h2>
          <div class="flex gap-2">
            <input v-model="filterText" type="text" placeholder="搜尋…"
                   class="filter-control w-40" />
            <select v-model="filterRisk" class="filter-control cursor-pointer">
              <option value="">全部</option>
              <option value="RED">🔴 高風險</option>
              <option value="YELLOW">🟡 中風險</option>
              <option value="BLUE">🔵 低風險</option>
            </select>
          </div>
        </div>

        <div class="rounded-xl overflow-hidden border border-white/[0.06] overflow-x-auto">
          <table class="w-full text-sm border-collapse">
            <thead>
              <tr class="bg-gray-800/60 text-gray-400 text-xs uppercase tracking-wider">
                <th class="px-4 py-3 text-left border-b border-white/[0.06] w-8 font-semibold">#</th>
                <th v-for="col in tableColumns" :key="col.key"
                    class="px-4 py-3 text-left border-b border-white/[0.06] cursor-pointer hover:text-blue-400 select-none whitespace-nowrap font-semibold transition-colors"
                    @click="sortBy(col.key)">
                  {{ col.label }}
                  <span class="ml-1 opacity-40 text-xs">{{ sortIcon(col.key) }}</span>
                </th>
                <th class="px-4 py-3 text-left border-b border-white/[0.06] whitespace-nowrap font-semibold">風險等級</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, i) in filteredResults"
                :key="i"
                class="border-b border-white/[0.04] transition-all"
                :class="riskRowCls(row)"
              >
                <td class="px-4 py-2.5 text-gray-600 text-xs">{{ i + 1 }}</td>
                <td v-for="col in tableColumns" :key="col.key"
                    class="px-4 py-2.5 max-w-xs">
                  <span class="block truncate" :title="str(row[col.key])">
                    {{ trunc(str(row[col.key]), 80) }}
                  </span>
                </td>
                <td class="px-4 py-2.5 whitespace-nowrap">
                  <span class="risk-badge" :class="riskBadgeCls(row.risk_level)">
                    {{ riskLabel(row.risk_level) }}
                  </span>
                </td>
              </tr>
              <tr v-if="!filteredResults.length">
                <td :colspan="tableColumns.length + 2"
                    class="px-4 py-10 text-center text-gray-500">無符合條件的資料</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="text-xs text-gray-600 text-right mt-3">
          顯示 {{ filteredResults.length }} / {{ results.length }} 筆
        </p>
      </section>

    </main>

    <!-- ══════════════════════════════════════════════════
         ERROR TOAST
    ══════════════════════════════════════════════════ -->
    <Transition name="toast">
      <div v-if="errorMsg" class="fixed bottom-7 right-7 z-50 max-w-md
                                   bg-gray-900/95 border border-red-500/40 backdrop-blur-xl
                                   rounded-2xl p-5 shadow-2xl shadow-black/60
                                   flex gap-4 items-start">
        <span class="text-2xl mt-0.5 flex-shrink-0">⚠️</span>
        <div class="flex-1">
          <p class="font-bold text-red-400 text-sm mb-1">API 錯誤</p>
          <p class="text-gray-300 text-sm leading-relaxed">{{ errorMsg }}</p>
        </div>
        <button class="text-gray-600 hover:text-gray-300 flex-shrink-0 mt-0.5 transition-colors"
                @click="errorMsg = ''">✕</button>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'
import { analyzeFile } from '../services/api.js'

// ── ENV 狀態 ───────────────────────────────────────────────────
const apiUrlOk = Boolean(import.meta.env.VITE_API_URL)

// ── Refs ───────────────────────────────────────────────────────
const fileInput    = ref(null)
const logEl        = ref(null)

const selectedFile = ref(null)
const isDragging   = ref(false)
const isProcessing = ref(false)
const progress     = ref(0)
const progressLabel = ref('準備中…')
const results      = ref([])
const logs         = ref([])
const errorMsg     = ref('')
const filterText   = ref('')
const filterRisk   = ref('')
const sortKey      = ref('')
const sortDir      = ref('asc')

let logTimers = []

// ── System Status Style ────────────────────────────────────────
const statusStyle = computed(() => {
  if (isProcessing.value)        return { text: 'ANALYZING',  cls: 'text-yellow-400 border-yellow-500/40 bg-yellow-500/10' }
  if (results.value.length > 0)  return { text: 'COMPLETE',   cls: 'text-green-400  border-green-500/40  bg-green-500/10' }
  return { text: 'READY', cls: 'text-gray-400 border-gray-700 bg-gray-800/60' }
})

// ── Drop Zone Classes ──────────────────────────────────────────
const dropZoneCls = computed(() => {
  if (isProcessing.value) return 'border-gray-700/50 bg-gray-800/20 cursor-not-allowed opacity-50'
  if (isDragging.value)   return 'border-blue-400/60 bg-blue-500/8 drop-glow'
  if (selectedFile.value) return 'border-emerald-500/40 bg-emerald-500/5'
  return 'border-gray-700/60 hover:border-blue-500/50 hover:bg-blue-500/5'
})

// ── Risk Counts / Stats ────────────────────────────────────────
const riskCounts = computed(() => ({
  RED:    results.value.filter(r => r.risk_level === 'RED').length,
  YELLOW: results.value.filter(r => r.risk_level === 'YELLOW').length,
  BLUE:   results.value.filter(r => !['RED','YELLOW'].includes(r.risk_level)).length,
}))

const stats = computed(() => [
  { label: '總筆數',    value: results.value.length,   color: 'text-gray-100',   cardCls: 'stat-total'  },
  { label: '高風險 🔴', value: riskCounts.value.RED,    color: 'text-red-400',    cardCls: 'stat-red'    },
  { label: '中風險 🟡', value: riskCounts.value.YELLOW, color: 'text-yellow-400', cardCls: 'stat-yellow' },
  { label: '低風險 🔵', value: riskCounts.value.BLUE,   color: 'text-blue-400',   cardCls: 'stat-blue'   },
])

// ── Table Columns ──────────────────────────────────────────────
const tableColumns = computed(() => {
  if (!results.value.length) return []
  return Object.keys(results.value[0])
    .filter(k => k !== 'risk_level')
    .map(k => ({ key: k, label: k.replace(/_/g, ' ').toUpperCase() }))
})

// ── Filtered + Sorted ─────────────────────────────────────────
const filteredResults = computed(() => {
  let list = results.value
  if (filterRisk.value)
    list = list.filter(r => r.risk_level === filterRisk.value)
  if (filterText.value.trim()) {
    const q = filterText.value.toLowerCase()
    list = list.filter(r => Object.values(r).some(v => String(v).toLowerCase().includes(q)))
  }
  if (sortKey.value) {
    list = [...list].sort((a, b) => {
      const va = String(a[sortKey.value] ?? ''), vb = String(b[sortKey.value] ?? '')
      return sortDir.value === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va)
    })
  }
  return list
})

// ── File Handling ──────────────────────────────────────────────
function onFileChange(e) { const f = e.target.files[0]; if (f) setFile(f) }
function onDrop(e) {
  isDragging.value = false
  const f = e.dataTransfer.files[0]
  if (f?.name.endsWith('.csv')) setFile(f)
  else addLog('warn', '請拖入 .csv 格式文件')
}
function setFile(f) {
  selectedFile.value = f
  progress.value = 0
  results.value = []
  logs.value = []
  addLog('info', `已選擇：${f.name}（${fmtSize(f.size)}）`)
}
function removeFile() {
  selectedFile.value = null
  progress.value = 0
  if (fileInput.value) fileInput.value.value = ''
}

// ── 擬真日誌腳本（因應 Bedrock 1 RPS 長等待）─────────────────
const LOG_SCRIPT = [
  [1500,  'info',    '資料上傳成功'],
  [4000,  'info',    '正在進行 XGBoost 特徵比對…'],
  [8000,  'info',    'Bedrock AI 正在審查語意邏輯…'],
  [14000, 'warn',    '注意：Bedrock 1 RPS 限制，依序逐筆分析中…'],
  [22000, 'info',    '[系統] AI 深度推論中，請耐心等候…'],
  [38000, 'info',    '[系統] 仍在處理，大批量資料預計需要 1–2 分鐘'],
  [60000, 'warn',    '[系統] 已超過 1 分鐘，若資料量大屬正常現象'],
  [90000, 'info',    '[系統] 接近完成，感謝您的耐心…'],
  [120000,'warn',    '[系統] 超過 2 分鐘，若仍無回應請確認 S3 是否已產出結果'],
]

function startLogScript() {
  clearLogTimers()
  logTimers = LOG_SCRIPT.map(([ms, lvl, msg]) =>
    setTimeout(() => { if (isProcessing.value) addLog(lvl, msg) }, ms)
  )
}
function clearLogTimers() { logTimers.forEach(clearTimeout); logTimers = [] }

// ── Main Flow ──────────────────────────────────────────────────
async function startAnalysis() {
  if (!selectedFile.value || isProcessing.value || !apiUrlOk) return

  isProcessing.value = true
  progress.value     = 0
  results.value      = []
  errorMsg.value     = ''
  progressLabel.value = 'Lambda 分析中…'

  addLog('info', '─── 開始偵辦任務 ───')
  startLogScript()

  try {
    const data = await analyzeFile(
      selectedFile.value,
      pct  => { progress.value = pct },
      ({ level, message }) => addLog(level, message),
    )
    results.value       = data
    progressLabel.value = '分析完成！'
    addLog('success', `✅ 偵辦完畢，共 ${data.length} 筆`)
    addLog('success', `🔴 ${riskCounts.value.RED}　🟡 ${riskCounts.value.YELLOW}　🔵 ${riskCounts.value.BLUE}`)
  } catch (err) {
    errorMsg.value = err.message
    addLog('error', `❌ ${err.message}`)
    progress.value = 0
  } finally {
    isProcessing.value = false
    clearLogTimers()
  }
}

// ── Helpers ────────────────────────────────────────────────────
function addLog(level, message) {
  const time = new Date().toTimeString().slice(0, 8)
  logs.value.push({ time, level, message })
  nextTick(() => { if (logEl.value) logEl.value.scrollTop = logEl.value.scrollHeight })
}

function logTagCls(level) {
  return {
    info:    'text-blue-400',
    warn:    'text-yellow-400',
    error:   'text-red-400',
    success: 'text-emerald-400',
  }[level] ?? 'text-gray-400'
}

function riskRowCls(row) {
  const lvl = row.risk_level
  if (lvl === 'RED'    || Number(row.label) === 1) return 'row-red'
  if (lvl === 'YELLOW')                            return 'row-yellow'
  return 'row-blue'
}

function riskBadgeCls(lvl) {
  if (lvl === 'RED')    return 'badge-red'
  if (lvl === 'YELLOW') return 'badge-yellow'
  return 'badge-blue'
}

function riskLabel(lvl) {
  return { RED: '🔴 高風險', YELLOW: '🟡 中風險', BLUE: '🔵 低風險', GREEN: '🟢 正常' }[lvl] ?? lvl
}

function sortBy(key) {
  sortDir.value = sortKey.value === key && sortDir.value === 'asc' ? 'desc' : 'asc'
  sortKey.value = key
}
function sortIcon(key) {
  if (sortKey.value !== key) return '⇅'
  return sortDir.value === 'asc' ? '▲' : '▼'
}
function fmtSize(b) {
  if (b < 1024) return b + ' B'
  if (b < 1048576) return (b / 1024).toFixed(1) + ' KB'
  return (b / 1048576).toFixed(2) + ' MB'
}
function str(v) { return v == null ? '—' : String(v) }
function trunc(s, n) { return s.length > n ? s.slice(0, n) + '…' : s }

watch(errorMsg, v => { if (v) setTimeout(() => { errorMsg.value = '' }, 10000) })
</script>

<style scoped>
/* ── Page Background ──────────────────────────────────────── */
.page-bg {
  background-color: #07091a;
  background-image:
    radial-gradient(ellipse 100% 60% at 50% -10%, rgba(59, 130, 246, 0.07) 0%, transparent 70%),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(99, 102, 241, 0.04) 0%, transparent 60%);
}

/* ── Header ──────────────────────────────────────────────── */
.header-glass {
  background: rgba(7, 9, 26, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 1px 32px rgba(0, 0, 0, 0.4);
}

/* ── Logo Icon ───────────────────────────────────────────── */
.logo-icon-wrap {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(59,130,246,0.15) 0%, rgba(99,102,241,0.1) 100%);
  border: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 16px rgba(59, 130, 246, 0.1);
}

/* ── Gradient Title ──────────────────────────────────────── */
.gradient-text {
  background: linear-gradient(135deg, #60a5fa 0%, #a5b4fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ── Cards ───────────────────────────────────────────────── */
.card {
  background: linear-gradient(180deg, rgba(15, 21, 50, 0.8) 0%, rgba(10, 14, 35, 0.6) 100%);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 18px;
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.05) inset,
    0 4px 40px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(12px);
}

/* ── Section Titles ──────────────────────────────────────── */
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #94a3b8;
}
.section-icon { font-size: 0.9rem; }

/* ── Inline Code ─────────────────────────────────────────── */
.inline-code {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 1px 6px;
  font-size: 0.8em;
  font-family: 'Fira Code', 'Cascadia Code', monospace;
  color: #93c5fd;
}

/* ── Drop Zone ───────────────────────────────────────────── */
.drop-zone {
  min-height: 130px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.drop-glow {
  box-shadow: 0 0 24px rgba(59, 130, 246, 0.15);
}

/* ── Primary Button ──────────────────────────────────────── */
.btn-primary {
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 60%, #60a5fa 100%);
  color: white;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.35), 0 0 0 1px rgba(99, 170, 255, 0.2) inset;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}
.btn-primary:hover {
  background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
  transform: translateY(-1px);
  box-shadow: 0 8px 28px rgba(59, 130, 246, 0.45);
}
.btn-primary:active {
  transform: translateY(0);
}

/* ── Progress Shimmer ────────────────────────────────────── */
.shimmer {
  background-size: 200% 100%;
  background-image: linear-gradient(90deg, #1d4ed8 0%, #60a5fa 40%, #a5b4fc 60%, #1d4ed8 100%);
  animation: shimmer 1.6s linear infinite;
}
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ── AI Spinner ──────────────────────────────────────────── */
.ai-spinner {
  display: inline-block;
  width: 15px;
  height: 15px;
  border: 2px solid rgba(255,255,255,0.25);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Log Window ──────────────────────────────────────────── */
.log-window {
  background: #02040d;
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 10px;
  padding: 14px 16px;
  height: 280px;
  overflow-y: auto;
  font-family: 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
  font-size: 0.73rem;
  scroll-behavior: smooth;
  box-shadow: inset 0 2px 16px rgba(0,0,0,0.6);
}
.log-window::-webkit-scrollbar { width: 3px; }
.log-window::-webkit-scrollbar-track { background: transparent; }
.log-window::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }

.log-line { display: flex; gap: 8px; margin-bottom: 4px; line-height: 1.6; flex-wrap: wrap; }
.log-time { color: #34d399; flex-shrink: 0; opacity: 0.7; }
.log-tag  { flex-shrink: 0; font-weight: 700; min-width: 58px; }
.log-msg  { color: #94a3b8; word-break: break-all; }

/* ── Stat Cards ──────────────────────────────────────────── */
.stat-card {
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  border: 1px solid;
}
.stat-total  {
  background: rgba(30, 41, 70, 0.6);
  border-color: rgba(148, 163, 184, 0.12);
}
.stat-red {
  background: rgba(127, 29, 29, 0.25);
  border-color: rgba(248, 113, 113, 0.2);
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.06) inset;
}
.stat-yellow {
  background: rgba(120, 53, 15, 0.25);
  border-color: rgba(251, 191, 36, 0.2);
  box-shadow: 0 0 20px rgba(234, 179, 8, 0.06) inset;
}
.stat-blue {
  background: rgba(23, 37, 84, 0.4);
  border-color: rgba(96, 165, 250, 0.2);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.06) inset;
}

/* ── Filter Controls ─────────────────────────────────────── */
.filter-control {
  background: rgba(15, 23, 50, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 0.83rem;
  color: #e2e8f0;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.filter-control::placeholder { color: #374151; }
.filter-control:focus {
  border-color: rgba(96, 165, 250, 0.5);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* ── Table Row Colors (dark mode) ────────────────────────── */
.row-red    {
  background: rgba(127, 29, 29, 0.2);
  color: #fca5a5;
}
.row-red:hover    { background: rgba(127, 29, 29, 0.32); }

.row-yellow {
  background: rgba(120, 53, 15, 0.2);
  color: #fde68a;
}
.row-yellow:hover { background: rgba(120, 53, 15, 0.32); }

.row-blue {
  background: rgba(23, 37, 84, 0.25);
  color: #bfdbfe;
}
.row-blue:hover   { background: rgba(23, 37, 84, 0.38); }

/* ── Risk Badges ─────────────────────────────────────────── */
.risk-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 99px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.badge-red    { background: rgba(239, 68, 68, 0.15);   color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }
.badge-yellow { background: rgba(234, 179, 8, 0.15);   color: #fde047; border: 1px solid rgba(234, 179, 8, 0.3); }
.badge-blue   { background: rgba(59, 130, 246, 0.15);  color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.3); }

/* ── Toast Transition ────────────────────────────────────── */
.toast-enter-active, .toast-leave-active { transition: opacity .3s, transform .3s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(16px); }
</style>
