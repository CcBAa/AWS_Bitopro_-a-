<template>
  <div class="min-h-screen bg-gray-950 text-gray-100 pb-16 font-sans">

    <!-- ══════════════════════════════════════════════════
         HEADER
    ══════════════════════════════════════════════════ -->
    <header class="sticky top-0 z-50 bg-gray-950/90 backdrop-blur border-b border-gray-800 px-8 py-4">
      <div class="max-w-6xl mx-auto flex items-center justify-between">

        <div class="flex items-center gap-4">
          <span class="text-3xl">🔍</span>
          <div>
            <h1 class="text-xl font-bold text-blue-400 tracking-tight">去偽存真 · DisInfo Shield</h1>
            <p class="text-xs text-gray-500">AI-Powered Disinformation Detection System</p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- ENV 狀態指示 -->
          <span
            class="text-xs font-bold px-3 py-1 rounded-full border"
            :class="apiUrlOk
              ? 'text-green-400 border-green-500/40 bg-green-500/10'
              : 'text-red-400  border-red-500/40  bg-red-500/10 animate-pulse'"
          >
            {{ apiUrlOk ? 'ENV OK' : 'ENV MISSING' }}
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
      <section class="bg-gray-900 border border-gray-800 rounded-2xl p-6">
        <h2 class="flex items-center gap-2 text-base font-semibold mb-4">
          <span>📁</span> 上傳數據集
        </h2>

        <!-- Drop Zone -->
        <div
          class="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors duration-200 mb-4"
          :class="dropZoneCls"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop"
          @click="!isProcessing && $refs.fileInput.click()"
        >
          <input ref="fileInput" type="file" accept=".csv" class="hidden"
                 :disabled="isProcessing" @change="onFileChange" />

          <template v-if="!selectedFile">
            <p class="text-4xl mb-2">📂</p>
            <p class="text-gray-300">拖曳 <code>.csv</code> 至此，或 <span class="text-blue-400 underline">點擊選擇</span></p>
            <p class="text-xs text-gray-600 mt-1">UTF-8 編碼，支援任意欄位結構</p>
          </template>
          <template v-else>
            <div class="flex items-center justify-center gap-3">
              <span class="text-3xl">📄</span>
              <div class="text-left">
                <p class="font-semibold text-gray-100">{{ selectedFile.name }}</p>
                <p class="text-xs text-gray-500 mt-0.5">{{ fmtSize(selectedFile.size) }}</p>
              </div>
              <button v-if="!isProcessing"
                      class="ml-4 text-xs text-red-400 border border-red-500/40 px-2 py-1 rounded hover:bg-red-500/10 transition"
                      @click.stop="removeFile">✕ 移除</button>
            </div>
          </template>
        </div>

        <!-- Progress Bar -->
        <div v-if="isProcessing || progress > 0" class="mb-4">
          <div class="flex justify-between text-xs text-gray-500 mb-1">
            <span>{{ progressLabel }}</span>
            <span class="text-blue-400 font-semibold">{{ Math.round(progress) }}%</span>
          </div>
          <div class="h-2 bg-gray-800 rounded-full overflow-hidden">
            <div
              class="h-full rounded-full bg-gradient-to-r from-blue-600 to-blue-400 transition-all duration-500"
              :class="{ 'shimmer': isProcessing }"
              :style="{ width: progress + '%' }"
            ></div>
          </div>
        </div>

        <!-- Submit Button -->
        <button
          class="w-full py-3 rounded-xl font-semibold text-sm transition-all duration-200 flex items-center justify-center gap-2"
          :class="isProcessing || !selectedFile || !apiUrlOk
            ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20 hover:-translate-y-0.5'"
          :disabled="isProcessing || !selectedFile || !apiUrlOk"
          @click="startAnalysis"
        >
          <template v-if="!isProcessing">
            🚀 送出分析
          </template>
          <template v-else>
            <!-- AI 偵辦中 動畫 -->
            <span class="flex items-center gap-2">
              <span class="ai-spinner"></span>
              AI 偵辦中…
            </span>
          </template>
        </button>

        <!-- ENV 缺失提示 -->
        <p v-if="!apiUrlOk" class="mt-3 text-xs text-red-400 text-center">
          ⚠️ <code>VITE_API_URL</code> 未設定，請建立 <code>.env</code> 或至 Amplify 設定環境變數
        </p>
      </section>

      <!-- ══════════════════════════════════════════════
           LOG + STATS ROW
      ══════════════════════════════════════════════ -->
      <div v-if="isProcessing || results.length > 0" class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- 偵查日誌 -->
        <section class="lg:col-span-2 bg-gray-900 border border-gray-800 rounded-2xl p-6 flex flex-col">
          <h2 class="flex items-center gap-2 text-base font-semibold mb-3">
            <span>🖥️</span> 偵查日誌
            <span v-if="isProcessing"
                  class="ml-1 text-xs font-black px-2 py-0.5 rounded bg-red-500 text-white animate-pulse tracking-widest">
              LIVE
            </span>
          </h2>
          <div ref="logEl" class="log-window flex-1">
            <div v-for="(e, i) in logs" :key="i" class="log-line">
              <span class="log-time">[{{ e.time }}]</span>
              <span :class="logTagCls(e.level)">{{ e.level.toUpperCase() }}</span>
              <span class="log-msg">{{ e.message }}</span>
            </div>
            <div v-if="isProcessing" class="log-time animate-pulse mt-1">▌</div>
          </div>
        </section>

        <!-- 風險統計 -->
        <section v-if="results.length > 0" class="bg-gray-900 border border-gray-800 rounded-2xl p-6">
          <h2 class="flex items-center gap-2 text-base font-semibold mb-4">
            <span>📊</span> 風險統計
          </h2>
          <div class="grid grid-cols-2 gap-3">
            <div v-for="s in stats" :key="s.label" class="bg-gray-800 rounded-xl p-4 text-center">
              <p class="text-3xl font-black" :class="s.color">{{ s.value }}</p>
              <p class="text-xs text-gray-500 mt-1">{{ s.label }}</p>
            </div>
          </div>
        </section>
      </div>

      <!-- ══════════════════════════════════════════════
           RESULTS TABLE
      ══════════════════════════════════════════════ -->
      <section v-if="results.length > 0" class="bg-gray-900 border border-gray-800 rounded-2xl p-6">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h2 class="flex items-center gap-2 text-base font-semibold">
            <span>📋</span> 分析結果
          </h2>
          <div class="flex gap-2">
            <input v-model="filterText" type="text" placeholder="搜尋…"
                   class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-200
                          placeholder-gray-600 outline-none focus:border-blue-500 w-40" />
            <select v-model="filterRisk"
                    class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-200 outline-none focus:border-blue-500 cursor-pointer">
              <option value="">全部</option>
              <option value="RED">🔴 高風險</option>
              <option value="YELLOW">🟡 中風險</option>
              <option value="BLUE">🔵 低風險</option>
            </select>
          </div>
        </div>

        <!-- 白底表格（讓 Tailwind 的 bg-red-50 等顯色正確） -->
        <div class="rounded-xl overflow-hidden border border-gray-700 overflow-x-auto">
          <table class="w-full text-sm border-collapse">
            <thead>
              <tr class="bg-gray-800 text-gray-400 text-xs uppercase tracking-wide">
                <th class="px-3 py-2.5 text-left border-b border-gray-700 w-8">#</th>
                <th v-for="col in tableColumns" :key="col.key"
                    class="px-3 py-2.5 text-left border-b border-gray-700 cursor-pointer hover:text-blue-400 select-none whitespace-nowrap"
                    @click="sortBy(col.key)">
                  {{ col.label }}
                  <span class="ml-1 opacity-50 text-xs">{{ sortIcon(col.key) }}</span>
                </th>
                <th class="px-3 py-2.5 text-left border-b border-gray-700 whitespace-nowrap">風險等級</th>
              </tr>
            </thead>
            <tbody class="bg-white text-gray-800">
              <tr
                v-for="(row, i) in filteredResults"
                :key="i"
                class="border-b border-gray-100 transition-colors"
                :class="riskRowCls(row)"
              >
                <td class="px-3 py-2.5 text-gray-400 text-xs">{{ i + 1 }}</td>
                <td v-for="col in tableColumns" :key="col.key"
                    class="px-3 py-2.5 max-w-xs">
                  <span class="block truncate" :title="str(row[col.key])">
                    {{ trunc(str(row[col.key]), 80) }}
                  </span>
                </td>
                <td class="px-3 py-2.5 whitespace-nowrap">
                  <span class="risk-badge" :class="riskBadgeCls(row.risk_level)">
                    {{ riskLabel(row.risk_level) }}
                  </span>
                </td>
              </tr>
              <tr v-if="!filteredResults.length">
                <td :colspan="tableColumns.length + 2"
                    class="px-3 py-8 text-center text-gray-400">無符合條件的資料</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="text-xs text-gray-500 text-right mt-2">
          顯示 {{ filteredResults.length }} / {{ results.length }} 筆
        </p>
      </section>

    </main>

    <!-- ══════════════════════════════════════════════════
         ERROR TOAST
    ══════════════════════════════════════════════════ -->
    <Transition name="toast">
      <div v-if="errorMsg" class="fixed bottom-7 right-7 z-50 max-w-md
                                   bg-gray-900 border border-red-500/60
                                   rounded-2xl p-5 shadow-2xl shadow-black/60
                                   flex gap-4 items-start">
        <span class="text-2xl mt-0.5 flex-shrink-0">⚠️</span>
        <div class="flex-1">
          <p class="font-bold text-red-400 text-sm mb-1">API 錯誤</p>
          <p class="text-gray-300 text-sm leading-relaxed">{{ errorMsg }}</p>
        </div>
        <button class="text-gray-500 hover:text-gray-300 flex-shrink-0 mt-0.5"
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
  if (isProcessing.value) return 'border-gray-700 bg-gray-800/40 cursor-not-allowed opacity-60'
  if (isDragging.value)   return 'border-blue-400 bg-blue-500/10'
  if (selectedFile.value) return 'border-green-500/50 bg-green-500/5'
  return 'border-gray-700 hover:border-blue-500/60 hover:bg-blue-500/5'
})

// ── Risk Counts / Stats ────────────────────────────────────────
const riskCounts = computed(() => ({
  RED:    results.value.filter(r => r.risk_level === 'RED').length,
  YELLOW: results.value.filter(r => r.risk_level === 'YELLOW').length,
  BLUE:   results.value.filter(r => !['RED','YELLOW'].includes(r.risk_level)).length,
}))

const stats = computed(() => [
  { label: '總筆數',    value: results.value.length, color: 'text-gray-100' },
  { label: '高風險 🔴', value: riskCounts.value.RED,    color: 'text-red-400'    },
  { label: '中風險 🟡', value: riskCounts.value.YELLOW, color: 'text-yellow-400' },
  { label: '低風險 🔵', value: riskCounts.value.BLUE,   color: 'text-blue-400'   },
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
    success: 'text-green-400',
  }[level] ?? 'text-gray-400'
}

/**
 * 表格行背景
 * RED / label=1  → bg-red-50    text-red-700
 * YELLOW         → bg-yellow-50 text-yellow-900
 * BLUE / GREEN   → bg-blue-50   text-blue-900
 */
function riskRowCls(row) {
  const lvl = row.risk_level
  if (lvl === 'RED'    || Number(row.label) === 1) return 'bg-red-50    text-red-700'
  if (lvl === 'YELLOW')                            return 'bg-yellow-50 text-yellow-900'
  return 'bg-blue-50 text-blue-900'
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
/* ── Log Window ──────────────────────────────────────────── */
.log-window {
  background: #010409;
  border: 1px solid #21262d;
  border-radius: 10px;
  padding: 14px;
  height: 280px;
  overflow-y: auto;
  font-family: 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
  font-size: 0.76rem;
  scroll-behavior: smooth;
}
.log-window::-webkit-scrollbar { width: 4px; }
.log-window::-webkit-scrollbar-thumb { background: #30363d; border-radius: 2px; }

.log-line { display: flex; gap: 8px; margin-bottom: 4px; line-height: 1.6; flex-wrap: wrap; }
.log-time { color: #3fb950; flex-shrink: 0; }
.log-tag  { flex-shrink: 0; font-weight: 700; min-width: 58px; }
.log-msg  { color: #adbac7; word-break: break-all; }

/* ── Progress Shimmer ───────────────────────────────────── */
.shimmer {
  background-size: 200% 100%;
  background-image: linear-gradient(90deg, #1d4ed8 0%, #60a5fa 50%, #1d4ed8 100%);
  animation: shimmer 1.8s linear infinite;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* ── AI Spinner ─────────────────────────────────────────── */
.ai-spinner {
  display: inline-block;
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin .7s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Risk Badges ────────────────────────────────────────── */
.risk-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 99px;
  font-size: 0.75rem;
  font-weight: 700;
}
.badge-red    { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
.badge-yellow { background: #fef9c3; color: #92400e; border: 1px solid #fde68a; }
.badge-blue   { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }

/* ── Toast Transition ───────────────────────────────────── */
.toast-enter-active, .toast-leave-active { transition: opacity .3s, transform .3s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(14px); }
</style>
