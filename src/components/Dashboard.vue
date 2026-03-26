<template>
  <div class="page-root">

    <!-- ══════════════════════════════════════════════════
         HEADER — HUD style
    ══════════════════════════════════════════════════ -->
    <header class="hud-header">
      <div class="header-inner">

        <!-- Logo + Title -->
        <div class="flex items-center gap-4">
          <div class="shield-icon" aria-hidden="true">
            <!-- Shield SVG (Heroicons) -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
              <path fill-rule="evenodd" d="M12.516 2.17a.75.75 0 0 0-1.032 0 11.209 11.209 0 0 1-7.877 3.08.75.75 0 0 0-.722.515A12.74 12.74 0 0 0 2.25 9.75c0 5.942 4.064 10.933 9.563 12.348a.749.749 0 0 0 .374 0c5.499-1.415 9.563-6.406 9.563-12.348 0-1.39-.223-2.73-.635-3.985a.75.75 0 0 0-.722-.516l-.143.001c-2.996 0-5.717-1.17-7.734-3.08Z" clip-rule="evenodd" />
            </svg>
          </div>
          <div>
            <h1 class="site-title">去偽存真 · DisInfo Shield</h1>
            <p class="site-sub">AI-Powered Disinformation Detection System</p>
          </div>
        </div>

        <!-- Status Badges -->
        <div class="flex items-center gap-3">
          <!-- ENV -->
          <div
            class="status-chip"
            :class="apiUrlOk ? 'chip-ok' : 'chip-err'"
            :aria-label="apiUrlOk ? 'Environment configured' : 'Environment missing'"
          >
            <span class="chip-dot"></span>
            {{ apiUrlOk ? 'ENV OK' : 'ENV MISSING' }}
          </div>

          <!-- System State -->
          <div class="status-chip" :class="statusStyle.cls" :aria-live="isProcessing ? 'polite' : 'off'">
            <span class="chip-dot" :class="{ 'animate-pulse': isProcessing }"></span>
            {{ statusStyle.text }}
          </div>
        </div>
      </div>
      <!-- neon accent line -->
      <div class="header-accent-line" aria-hidden="true"></div>
    </header>

    <!-- ══════════════════════════════════════════════════
         MAIN CONTENT
    ══════════════════════════════════════════════════ -->
    <main class="main-content" role="main">

      <!-- ── UPLOAD CARD ───────────────────────────────── -->
      <section class="hud-card" aria-labelledby="upload-heading">
        <h2 id="upload-heading" class="card-heading">
          <!-- Upload icon (Heroicons) -->
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-4 h-4 flex-shrink-0" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.338-2.32 5.75 5.75 0 0 1 1.023 11.095" />
          </svg>
          上傳數據集
        </h2>

        <!-- Drop Zone -->
        <div
          class="drop-zone"
          :class="dropZoneCls"
          role="button"
          tabindex="0"
          :aria-disabled="isProcessing"
          aria-label="拖曳 CSV 文件至此，或按下 Enter 選擇文件"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="onDrop"
          @click="!isProcessing && $refs.fileInput.click()"
          @keydown.enter.prevent="!isProcessing && $refs.fileInput.click()"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".csv"
            class="sr-only"
            :disabled="isProcessing"
            aria-label="選擇 CSV 文件"
            @change="onFileChange"
          />

          <template v-if="!selectedFile">
            <div class="drop-icon" aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" class="w-12 h-12">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m6.75 12-3-3m0 0-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
            </div>
            <p class="drop-text">
              拖曳 <code class="inline-code">.csv</code> 至此，或
              <span class="drop-link">點擊選擇</span>
            </p>
            <p class="drop-hint">UTF-8 編碼，支援任意欄位結構</p>
          </template>

          <template v-else>
            <div class="file-info">
              <div class="file-icon" aria-hidden="true">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-8 h-8">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                </svg>
              </div>
              <div>
                <p class="file-name">{{ selectedFile.name }}</p>
                <p class="file-size">{{ fmtSize(selectedFile.size) }}</p>
              </div>
              <button
                v-if="!isProcessing"
                class="btn-remove"
                aria-label="移除已選擇的文件"
                @click.stop="removeFile"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
                </svg>
                移除
              </button>
            </div>
          </template>
        </div>

        <!-- Progress Bar -->
        <div v-if="isProcessing || progress > 0" class="progress-wrap" role="progressbar" :aria-valuenow="Math.round(progress)" aria-valuemin="0" aria-valuemax="100">
          <div class="progress-meta">
            <span class="progress-label">{{ progressLabel }}</span>
            <span class="progress-pct">{{ Math.round(progress) }}%</span>
          </div>
          <div class="progress-track">
            <div
              class="progress-fill"
              :class="{ 'progress-shimmer': isProcessing }"
              :style="{ width: progress + '%' }"
            ></div>
          </div>
        </div>

        <!-- Submit Button -->
        <button
          class="btn-analyze"
          :class="isProcessing || !selectedFile || !apiUrlOk ? 'btn-disabled' : 'btn-active'"
          :disabled="isProcessing || !selectedFile || !apiUrlOk"
          :aria-busy="isProcessing"
          @click="startAnalysis"
        >
          <template v-if="!isProcessing">
            <!-- Rocket icon -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4" aria-hidden="true">
              <path fill-rule="evenodd" d="M9.315 7.584C12.195 3.883 16.695 1.5 21.75 1.5a.75.75 0 0 1 .75.75c0 5.056-2.383 9.555-6.084 12.436A6.75 6.75 0 0 1 9.75 22.5a.75.75 0 0 1-.75-.75v-4.131A15.838 15.838 0 0 1 6.382 15H2.25a.75.75 0 0 1-.75-.75 6.75 6.75 0 0 1 7.815-6.666ZM15 6.75a2.25 2.25 0 1 0 0 4.5 2.25 2.25 0 0 0 0-4.5Z" clip-rule="evenodd" />
              <path d="M5.26 17.242a.75.75 0 1 0-.897-1.203 5.243 5.243 0 0 0-2.05 5.022.75.75 0 0 0 .625.627 5.243 5.243 0 0 0 5.022-2.051.75.75 0 1 0-1.202-.897 3.744 3.744 0 0 1-3.008 1.51c0-1.23.592-2.323 1.51-3.008Z" />
            </svg>
            啟動分析
          </template>
          <template v-else>
            <span class="ai-spinner" aria-hidden="true"></span>
            AI 偵辦中…
          </template>
        </button>

        <!-- ENV missing warning -->
        <p v-if="!apiUrlOk" class="env-warn" role="alert">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 flex-shrink-0" aria-hidden="true">
            <path fill-rule="evenodd" d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003ZM12 8.25a.75.75 0 0 1 .75.75v3.75a.75.75 0 0 1-1.5 0V9a.75.75 0 0 1 .75-.75Zm0 8.25a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z" clip-rule="evenodd" />
          </svg>
          <code class="font-mono text-xs">VITE_API_URL</code> 未設定，請建立 <code class="font-mono text-xs">.env</code> 或至 Amplify 設定環境變數
        </p>
      </section>

      <!-- ── LOG + STATS ROW ──────────────────────────── -->
      <div v-if="isProcessing || results.length > 0" class="info-grid">

        <!-- 偵查日誌 -->
        <section class="hud-card lg:col-span-2" aria-labelledby="log-heading">
          <h2 id="log-heading" class="card-heading">
            <!-- Terminal icon -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-4 h-4 flex-shrink-0" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="m6.75 7.5 3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0 0 21 18V6a2.25 2.25 0 0 0-2.25-2.25H5.25A2.25 2.25 0 0 0 3 6v12a2.25 2.25 0 0 0 2.25 2.25Z" />
            </svg>
            偵查日誌
            <span v-if="isProcessing" class="live-badge" role="status" aria-label="即時更新中">LIVE</span>
          </h2>
          <div
            ref="logEl"
            class="log-window"
            role="log"
            aria-live="polite"
            aria-label="偵查日誌輸出"
          >
            <div v-for="(e, i) in logs" :key="i" class="log-line">
              <span class="log-ts">[{{ e.time }}]</span>
              <span class="log-tag" :class="logTagCls(e.level)">{{ e.level.toUpperCase().padEnd(7) }}</span>
              <span class="log-msg">{{ e.message }}</span>
            </div>
            <div v-if="isProcessing" class="log-cursor animate-pulse" aria-hidden="true">▌</div>
          </div>
        </section>

        <!-- 風險統計 -->
        <section v-if="results.length > 0" class="hud-card" aria-labelledby="stats-heading">
          <h2 id="stats-heading" class="card-heading">
            <!-- Chart icon -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-4 h-4 flex-shrink-0" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
            </svg>
            風險矩陣
          </h2>
          <div class="stats-grid">
            <div v-for="s in stats" :key="s.label" class="stat-tile" :class="s.tileCls">
              <p class="stat-num" :class="s.numCls">{{ s.value }}</p>
              <p class="stat-lbl">{{ s.label }}</p>
            </div>
          </div>
        </section>
      </div>

      <!-- ── RESULTS TABLE ─────────────────────────────── -->
      <section v-if="results.length > 0" class="hud-card" aria-labelledby="results-heading">
        <div class="results-bar">
          <h2 id="results-heading" class="card-heading">
            <!-- Table icon -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-4 h-4 flex-shrink-0" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 0 1-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0 1 12 19.5m9.75-9.75c0 .621-.504 1.125-1.125 1.125H12m8.625-9H12A1.125 1.125 0 0 0 10.875 3v9.75m8.625 0H12" />
            </svg>
            分析結果
          </h2>
          <div class="results-controls">
            <div class="search-wrap">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-icon w-4 h-4" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 15.803 7.5 7.5 0 0 0 15.803 15.803Z" />
              </svg>
              <input
                v-model="filterText"
                type="search"
                placeholder="搜尋…"
                class="search-input"
                aria-label="搜尋分析結果"
              />
            </div>
            <select
              v-model="filterRisk"
              class="filter-select"
              aria-label="依風險等級過濾"
            >
              <option value="">全部風險</option>
              <option value="RED">高風險</option>
              <option value="YELLOW">中風險</option>
              <option value="BLUE">低風險</option>
            </select>

            <!-- Download CSV Button -->
            <button
              class="btn-download"
              :class="{ 'btn-download--flash': downloadFlash }"
              aria-label="下載 CSV 結果"
              @click="downloadCsv"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
              </svg>
              匯出 CSV
            </button>
          </div>
        </div>

        <div class="table-scroll">
          <table class="data-table" aria-label="分析結果表格">
            <thead>
              <tr>
                <th scope="col" class="th-index">#</th>
                <th
                  v-for="col in tableColumns"
                  :key="col.key"
                  scope="col"
                  class="th-col"
                  :aria-sort="sortKey === col.key ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none'"
                  @click="sortBy(col.key)"
                >
                  {{ col.label }}
                  <span class="sort-icon" aria-hidden="true">{{ sortIcon(col.key) }}</span>
                </th>
                <th scope="col" class="th-risk">風險等級</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, i) in filteredResults"
                :key="i"
                class="data-row"
                :class="riskRowCls(row)"
              >
                <td class="td-index">{{ i + 1 }}</td>
                <td
                  v-for="col in tableColumns"
                  :key="col.key"
                  class="td-cell"
                >
                  <span class="cell-text" :title="str(row[col.key])">
                    {{ trunc(str(row[col.key]), 80) }}
                  </span>
                </td>
                <td class="td-risk">
                  <span class="risk-badge" :class="riskBadgeCls(row.risk_level)">
                    {{ riskLabel(row.risk_level) }}
                  </span>
                </td>
              </tr>
              <tr v-if="!filteredResults.length">
                <td :colspan="tableColumns.length + 2" class="td-empty">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-8 h-8 mx-auto mb-2 opacity-30" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 5.25h.008v.008H12v-.008Z" />
                  </svg>
                  無符合條件的資料
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="results-count" aria-live="polite">
          顯示 <strong>{{ filteredResults.length }}</strong> / {{ results.length }} 筆
        </p>
      </section>

    </main>

    <!-- ══════════════════════════════════════════════════
         ERROR TOAST
    ══════════════════════════════════════════════════ -->
    <Transition name="toast">
      <div
        v-if="errorMsg"
        class="error-toast"
        role="alert"
        aria-live="assertive"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5 flex-shrink-0 mt-0.5" aria-hidden="true">
          <path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12ZM12 8.25a.75.75 0 0 1 .75.75v3.75a.75.75 0 0 1-1.5 0V9a.75.75 0 0 1 .75-.75Zm0 8.25a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z" clip-rule="evenodd" />
        </svg>
        <div class="flex-1">
          <p class="toast-title">系統錯誤</p>
          <p class="toast-msg">{{ errorMsg }}</p>
        </div>
        <button class="toast-close" aria-label="關閉錯誤提示" @click="errorMsg = ''">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
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
const fileInput = ref(null)
const logEl     = ref(null)

const selectedFile  = ref(null)
const isDragging    = ref(false)
const isProcessing  = ref(false)
const progress      = ref(0)
const progressLabel = ref('準備中…')
const results       = ref([])
const logs          = ref([])
const errorMsg      = ref('')
const filterText    = ref('')
const filterRisk    = ref('')
const sortKey       = ref('')
const sortDir       = ref('asc')

let logTimers = []

// ── System Status Style ────────────────────────────────────────
const statusStyle = computed(() => {
  if (isProcessing.value)       return { text: 'ANALYZING', cls: 'chip-warn' }
  if (results.value.length > 0) return { text: 'COMPLETE',  cls: 'chip-ok'   }
  return { text: 'READY', cls: 'chip-idle' }
})

// ── Drop Zone Classes ──────────────────────────────────────────
const dropZoneCls = computed(() => {
  if (isProcessing.value) return 'drop-disabled'
  if (isDragging.value)   return 'drop-dragging'
  if (selectedFile.value) return 'drop-selected'
  return 'drop-idle'
})

// ── Risk Counts / Stats ────────────────────────────────────────
const riskCounts = computed(() => ({
  RED:    results.value.filter(r => r.risk_level === 'RED').length,
  YELLOW: results.value.filter(r => r.risk_level === 'YELLOW').length,
  BLUE:   results.value.filter(r => !['RED', 'YELLOW'].includes(r.risk_level)).length,
}))

const stats = computed(() => [
  { label: '總筆數',  value: results.value.length,   numCls: 'num-total',  tileCls: 'tile-total'  },
  { label: '高風險',  value: riskCounts.value.RED,    numCls: 'num-red',    tileCls: 'tile-red'    },
  { label: '中風險',  value: riskCounts.value.YELLOW, numCls: 'num-yellow', tileCls: 'tile-yellow' },
  { label: '低風險',  value: riskCounts.value.BLUE,   numCls: 'num-blue',   tileCls: 'tile-blue'   },
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

// ── 擬真日誌腳本 ──────────────────────────────────────────────
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

  isProcessing.value  = true
  progress.value      = 0
  results.value       = []
  errorMsg.value      = ''
  progressLabel.value = 'Lambda 分析中…'

  addLog('info', '─── 開始偵辦任務 ───')
  startLogScript()

  try {
    const data = await analyzeFile(
      selectedFile.value,
      pct => { progress.value = pct },
      ({ level, message }) => addLog(level, message),
    )
    results.value       = data
    progressLabel.value = '分析完成！'
    addLog('success', `✔ 偵辦完畢，共 ${data.length} 筆`)
    addLog('success', `RED:${riskCounts.value.RED}  YELLOW:${riskCounts.value.YELLOW}  BLUE:${riskCounts.value.BLUE}`)
  } catch (err) {
    errorMsg.value = err.message
    addLog('error', `✘ ${err.message}`)
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
    info:    'tag-info',
    warn:    'tag-warn',
    error:   'tag-error',
    success: 'tag-success',
  }[level] ?? 'tag-info'
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
  return { RED: '高風險', YELLOW: '中風險', BLUE: '低風險', GREEN: '正常' }[lvl] ?? lvl
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

// ── Download CSV ───────────────────────────────────────────────
const downloadFlash = ref(false)

function downloadCsv() {
  const lines = ['user_id,status']
  for (const row of results.value) {
    const userId = row.user_id ?? ''
    const status = row.risk_level === 'RED' ? 1 : 0
    lines.push(`${userId},${status}`)
  }
  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = `disinfo_result_${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)

  // flash feedback
  downloadFlash.value = true
  setTimeout(() => { downloadFlash.value = false }, 600)
}
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════
   DESIGN TOKENS — Cyberpunk UI (ui-ux-pro-max / Fira Code)
═══════════════════════════════════════════════════════════ */
:root {
  --bg:          #020617;
  --surface:     #0F172A;
  --surface2:    #1E293B;
  --border:      rgba(56, 189, 248, 0.12);
  --border-dim:  rgba(255, 255, 255, 0.06);
  --text:        #F8FAFC;
  --muted:       #64748B;
  --green:       #22C55E;
  --cyan:        #38BDF8;
  --red:         #EF4444;
  --yellow:      #FBBF24;
  --purple:      #A78BFA;
  --radius:      12px;
}

/* ── Page Root ──────────────────────────────────────────── */
.page-root {
  min-height: 100vh;
  background-color: var(--bg);
  background-image:
    radial-gradient(ellipse 80% 50% at 50% 0%, rgba(56, 189, 248, 0.06) 0%, transparent 65%),
    linear-gradient(rgba(56, 189, 248, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(56, 189, 248, 0.03) 1px, transparent 1px);
  background-size: 100% 100%, 40px 40px, 40px 40px;
  font-family: 'Fira Sans', system-ui, sans-serif;
  color: var(--text);
  padding-bottom: 60px;
}

/* ── Header ─────────────────────────────────────────────── */
.hud-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(2, 6, 23, 0.9);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 16px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-accent-line {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, var(--cyan) 30%, var(--green) 70%, transparent 100%);
  opacity: 0.4;
}

/* ── Logo Icon ──────────────────────────────────────────── */
.shield-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: rgba(56, 189, 248, 0.08);
  border: 1px solid rgba(56, 189, 248, 0.2);
  color: var(--cyan);
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.15);
  flex-shrink: 0;
}

/* ── Title ──────────────────────────────────────────────── */
.site-title {
  font-family: 'Fira Code', monospace;
  font-size: 1.15rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--cyan) 0%, var(--green) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
}
.site-sub {
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 2px;
  letter-spacing: 0.04em;
}

/* ── Status Chips ───────────────────────────────────────── */
.status-chip {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 5px 12px;
  border-radius: 99px;
  font-family: 'Fira Code', monospace;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  border: 1px solid;
}
.chip-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}
.chip-idle { color: var(--muted);  border-color: rgba(100,116,139,0.3); background: rgba(100,116,139,0.06); }
.chip-ok   { color: var(--green);  border-color: rgba(34,197,94,0.35);  background: rgba(34,197,94,0.08);
             box-shadow: 0 0 10px rgba(34,197,94,0.15); }
.chip-warn { color: var(--yellow); border-color: rgba(251,191,36,0.35); background: rgba(251,191,36,0.08);
             animation: pulse-chip 1.4s ease-in-out infinite; }
.chip-err  { color: var(--red);    border-color: rgba(239,68,68,0.35);  background: rgba(239,68,68,0.08);
             animation: pulse-chip 1.4s ease-in-out infinite; }
@keyframes pulse-chip { 0%,100% { opacity:1; } 50% { opacity:.55; } }

/* ── Main & Cards ───────────────────────────────────────── */
.main-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hud-card {
  background: linear-gradient(160deg, rgba(15,23,42,0.95) 0%, rgba(10,15,32,0.9) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  box-shadow:
    0 0 0 1px rgba(0,0,0,0.4),
    0 4px 32px rgba(0,0,0,0.5),
    inset 0 1px 0 rgba(56,189,248,0.06);
  position: relative;
}
/* Corner accent (HUD decorative element) */
.hud-card::before,
.hud-card::after {
  content: '';
  position: absolute;
  width: 10px;
  height: 10px;
  border-color: var(--cyan);
  border-style: solid;
  opacity: 0.4;
}
.hud-card::before { top: -1px; left: -1px; border-width: 2px 0 0 2px; border-radius: 3px 0 0 0; }
.hud-card::after  { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; border-radius: 0 0 3px 0; }

/* ── Card Heading ───────────────────────────────────────── */
.card-heading {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Fira Code', monospace;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--cyan);
  margin-bottom: 18px;
}
.card-heading svg { opacity: 0.7; }

/* ── LIVE badge ─────────────────────────────────────────── */
.live-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--red);
  color: #fff;
  font-size: 0.6rem;
  font-weight: 900;
  padding: 2px 7px;
  border-radius: 4px;
  letter-spacing: 0.12em;
  box-shadow: 0 0 10px rgba(239,68,68,0.5);
  animation: pulse-chip 1s ease-in-out infinite;
}

/* ── Drop Zone ──────────────────────────────────────────── */
.drop-zone {
  border: 2px dashed;
  border-radius: 10px;
  padding: 44px 24px;
  text-align: center;
  margin-bottom: 18px;
  transition: border-color .2s, background .2s, box-shadow .2s;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 140px;
}
.drop-zone:focus-visible { outline: 2px solid var(--cyan); outline-offset: 3px; }

.drop-idle     { border-color: rgba(56,189,248,0.2); background: rgba(56,189,248,0.02); }
.drop-idle:hover { border-color: rgba(56,189,248,0.45); background: rgba(56,189,248,0.05); box-shadow: 0 0 24px rgba(56,189,248,0.08); }
.drop-dragging { border-color: var(--cyan); background: rgba(56,189,248,0.08); box-shadow: 0 0 32px rgba(56,189,248,0.2); }
.drop-selected { border-color: rgba(34,197,94,0.4); background: rgba(34,197,94,0.04); border-style: solid; }
.drop-disabled { border-color: rgba(255,255,255,0.06); background: transparent; opacity: 0.4; cursor: not-allowed; }

.drop-icon { color: var(--cyan); opacity: 0.35; margin-bottom: 12px; }
.drop-text { color: #CBD5E1; font-size: 0.88rem; margin-bottom: 4px; }
.drop-link { color: var(--cyan); text-decoration: underline; text-underline-offset: 3px; cursor: pointer; }
.drop-hint { font-size: 0.73rem; color: var(--muted); margin-top: 4px; }

/* ── Inline code ────────────────────────────────────────── */
.inline-code {
  font-family: 'Fira Code', monospace;
  background: rgba(56,189,248,0.1);
  border: 1px solid rgba(56,189,248,0.2);
  border-radius: 4px;
  padding: 1px 6px;
  font-size: 0.82em;
  color: var(--cyan);
}

/* ── File info ──────────────────────────────────────────── */
.file-info { display: flex; align-items: center; gap: 14px; }
.file-icon { color: var(--green); opacity: 0.8; }
.file-name { font-weight: 600; color: var(--text); font-size: 0.9rem; }
.file-size { font-size: 0.75rem; color: var(--muted); margin-top: 2px; font-family: 'Fira Code', monospace; }

.btn-remove {
  display: flex;
  align-items: center;
  gap: 5px;
  background: none;
  border: 1px solid rgba(239,68,68,0.3);
  color: var(--red);
  border-radius: 6px;
  padding: 5px 10px;
  font-size: 0.78rem;
  cursor: pointer;
  transition: background .15s, box-shadow .15s;
  margin-left: auto;
}
.btn-remove:hover { background: rgba(239,68,68,0.1); box-shadow: 0 0 10px rgba(239,68,68,0.15); }
.btn-remove:focus-visible { outline: 2px solid var(--red); outline-offset: 2px; }

/* ── Progress ───────────────────────────────────────────── */
.progress-wrap { margin-bottom: 18px; }
.progress-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
  color: var(--muted);
  margin-bottom: 7px;
  font-family: 'Fira Code', monospace;
}
.progress-pct { color: var(--cyan); font-weight: 700; }
.progress-track {
  height: 6px;
  background: rgba(255,255,255,0.06);
  border-radius: 99px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--cyan) 0%, var(--green) 100%);
  border-radius: 99px;
  transition: width .4s ease;
  box-shadow: 0 0 10px rgba(34,197,94,0.4);
}
.progress-shimmer {
  background-size: 200% 100%;
  background-image: linear-gradient(90deg, #0ea5e9 0%, #22c55e 40%, #38bdf8 60%, #0ea5e9 100%);
  animation: shimmer 1.5s linear infinite;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* ── Analyze Button ─────────────────────────────────────── */
.btn-analyze {
  width: 100%;
  padding: 13px;
  border-radius: 8px;
  border: 1px solid;
  font-family: 'Fira Code', monospace;
  font-size: 0.88rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform .15s, box-shadow .15s, opacity .15s;
}
.btn-active {
  background: linear-gradient(135deg, rgba(34,197,94,0.15) 0%, rgba(56,189,248,0.1) 100%);
  border-color: rgba(34,197,94,0.5);
  color: var(--green);
  box-shadow: 0 0 20px rgba(34,197,94,0.2), inset 0 1px 0 rgba(34,197,94,0.1);
}
.btn-active:hover { transform: translateY(-1px); box-shadow: 0 0 32px rgba(34,197,94,0.3); }
.btn-active:active { transform: translateY(0); }
.btn-active:focus-visible { outline: 2px solid var(--green); outline-offset: 3px; }
.btn-disabled {
  background: rgba(255,255,255,0.03);
  border-color: rgba(255,255,255,0.07);
  color: var(--muted);
  cursor: not-allowed;
}

/* ── AI Spinner ─────────────────────────────────────────── */
.ai-spinner {
  width: 15px; height: 15px;
  border: 2px solid rgba(34,197,94,0.25);
  border-top-color: var(--green);
  border-radius: 50%;
  animation: spin .7s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── ENV Warning ────────────────────────────────────────── */
.env-warn {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 12px;
  font-size: 0.77rem;
  color: rgba(239,68,68,0.8);
  text-align: center;
  justify-content: center;
}

/* ── Info Grid ──────────────────────────────────────────── */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
}
@media (max-width: 1024px) { .info-grid { grid-template-columns: 1fr; } }

/* ── Log Window ─────────────────────────────────────────── */
.log-window {
  background: #010208;
  border: 1px solid rgba(56,189,248,0.08);
  border-radius: 8px;
  padding: 14px 16px;
  height: 290px;
  overflow-y: auto;
  font-family: 'Fira Code', monospace;
  font-size: 0.73rem;
  scroll-behavior: smooth;
  box-shadow: inset 0 2px 20px rgba(0,0,0,0.8);
  /* subtle scanline effect */
  background-image: repeating-linear-gradient(
    0deg,
    transparent 0px,
    transparent 3px,
    rgba(0,0,0,0.08) 3px,
    rgba(0,0,0,0.08) 4px
  );
}
.log-window::-webkit-scrollbar { width: 3px; }
.log-window::-webkit-scrollbar-track { background: transparent; }
.log-window::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.15); border-radius: 2px; }

.log-line { display: flex; gap: 8px; margin-bottom: 3px; line-height: 1.65; flex-wrap: wrap; }
.log-ts    { color: rgba(34,197,94,0.6); flex-shrink: 0; }
.log-tag   { flex-shrink: 0; font-weight: 700; min-width: 60px; }
.log-msg   { color: #94A3B8; word-break: break-all; }
.log-cursor{ color: var(--cyan); }

.tag-info    { color: var(--cyan); }
.tag-warn    { color: var(--yellow); }
.tag-error   { color: var(--red); }
.tag-success { color: var(--green); }

/* ── Stats ──────────────────────────────────────────────── */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.stat-tile {
  border-radius: 8px;
  padding: 16px 12px;
  text-align: center;
  border: 1px solid;
  position: relative;
  overflow: hidden;
}
.stat-tile::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.04;
  background: currentColor;
}
.stat-num {
  font-family: 'Fira Code', monospace;
  font-size: 2.2rem;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.02em;
}
.stat-lbl { font-size: 0.7rem; color: var(--muted); margin-top: 6px; letter-spacing: 0.06em; text-transform: uppercase; }

.tile-total  { background: rgba(30,41,59,0.6);   border-color: rgba(148,163,184,0.15); }
.tile-red    { background: rgba(127,29,29,0.25);  border-color: rgba(239,68,68,0.25);  }
.tile-yellow { background: rgba(120,53,15,0.25);  border-color: rgba(251,191,36,0.25); }
.tile-blue   { background: rgba(23,37,84,0.35);   border-color: rgba(56,189,248,0.25); }

.num-total  { color: #E2E8F0; }
.num-red    { color: #FCA5A5; text-shadow: 0 0 20px rgba(239,68,68,0.5); }
.num-yellow { color: #FDE68A; text-shadow: 0 0 20px rgba(251,191,36,0.5); }
.num-blue   { color: #7DD3FC; text-shadow: 0 0 20px rgba(56,189,248,0.5); }

/* ── Results Bar ────────────────────────────────────────── */
.results-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}
.results-controls { display: flex; gap: 8px; flex-wrap: wrap; }

/* ── Search ─────────────────────────────────────────────── */
.search-wrap { position: relative; }
.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted);
  pointer-events: none;
}
.search-input {
  background: rgba(15,23,42,0.8);
  border: 1px solid rgba(56,189,248,0.12);
  border-radius: 7px;
  padding: 7px 12px 7px 34px;
  font-size: 0.83rem;
  color: var(--text);
  outline: none;
  width: 160px;
  transition: border-color .15s, box-shadow .15s;
  font-family: 'Fira Sans', system-ui, sans-serif;
}
.search-input::placeholder { color: var(--muted); }
.search-input:focus { border-color: rgba(56,189,248,0.4); box-shadow: 0 0 0 3px rgba(56,189,248,0.08); }

.filter-select {
  background: rgba(15,23,42,0.8);
  border: 1px solid rgba(56,189,248,0.12);
  border-radius: 7px;
  padding: 7px 12px;
  font-size: 0.83rem;
  color: var(--text);
  outline: none;
  cursor: pointer;
  transition: border-color .15s;
  font-family: 'Fira Sans', system-ui, sans-serif;
}
.filter-select:focus { border-color: rgba(56,189,248,0.4); box-shadow: 0 0 0 3px rgba(56,189,248,0.08); }

/* ── Table ──────────────────────────────────────────────── */
.table-scroll {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid rgba(56,189,248,0.08);
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;
}
.data-table thead tr {
  background: rgba(15,23,42,0.9);
}
.th-index, .th-col, .th-risk {
  padding: 11px 14px;
  text-align: left;
  color: var(--muted);
  font-family: 'Fira Code', monospace;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  white-space: nowrap;
  border-bottom: 1px solid rgba(56,189,248,0.1);
}
.th-col { cursor: pointer; transition: color .15s; }
.th-col:hover { color: var(--cyan); }
.th-col:focus-visible { outline: 2px solid var(--cyan); outline-offset: -2px; }
.sort-icon { margin-left: 4px; font-size: 0.6rem; opacity: 0.5; }

.data-row {
  border-bottom: 1px solid rgba(255,255,255,0.04);
  transition: filter .15s;
}
.data-row:hover { filter: brightness(1.15); }

.row-red    { background: rgba(239,68,68,0.07);   box-shadow: inset 3px 0 0 rgba(239,68,68,0.6); }
.row-yellow { background: rgba(251,191,36,0.07);  box-shadow: inset 3px 0 0 rgba(251,191,36,0.6); }
.row-blue   { background: rgba(56,189,248,0.05);  box-shadow: inset 3px 0 0 rgba(56,189,248,0.5); }

.td-index { padding: 10px 14px; color: var(--muted); font-size: 0.72rem; font-family: 'Fira Code', monospace; white-space: nowrap; }
.td-cell  { padding: 10px 14px; color: #CBD5E1; max-width: 320px; }
.cell-text { display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.td-risk  { padding: 10px 14px; white-space: nowrap; }
.td-empty { padding: 48px 14px; text-align: center; color: var(--muted); font-size: 0.85rem; }

/* ── Risk Badges ────────────────────────────────────────── */
.risk-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 99px;
  font-size: 0.72rem;
  font-weight: 700;
  font-family: 'Fira Code', monospace;
  letter-spacing: 0.05em;
}
.badge-red    { background: rgba(239,68,68,0.12);  color: #FCA5A5; border: 1px solid rgba(239,68,68,0.4);  box-shadow: 0 0 8px rgba(239,68,68,0.2); }
.badge-yellow { background: rgba(251,191,36,0.12); color: #FDE68A; border: 1px solid rgba(251,191,36,0.4); box-shadow: 0 0 8px rgba(251,191,36,0.2); }
.badge-blue   { background: rgba(56,189,248,0.1);  color: #7DD3FC; border: 1px solid rgba(56,189,248,0.4); box-shadow: 0 0 8px rgba(56,189,248,0.2); }

/* ── Result Count ───────────────────────────────────────── */
.results-count {
  font-size: 0.75rem;
  color: var(--muted);
  text-align: right;
  margin-top: 10px;
  font-family: 'Fira Code', monospace;
}
.results-count strong { color: var(--cyan); }

/* ── Download Button ────────────────────────────────────── */
.btn-download {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 7px;
  border: 1px solid rgba(56, 189, 248, 0.35);
  background: rgba(56, 189, 248, 0.06);
  color: var(--cyan);
  font-family: 'Fira Code', monospace;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  cursor: pointer;
  transition: border-color .2s, background .2s, box-shadow .2s;
  white-space: nowrap;
}
.btn-download:hover {
  border-color: rgba(56, 189, 248, 0.65);
  background: rgba(56, 189, 248, 0.12);
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.2);
}
.btn-download:focus-visible {
  outline: 2px solid var(--cyan);
  outline-offset: 3px;
}
.btn-download--flash {
  border-color: var(--green);
  background: rgba(34, 197, 94, 0.12);
  color: var(--green);
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.25);
}

/* ── Error Toast ────────────────────────────────────────── */
.error-toast {
  position: fixed;
  bottom: 28px;
  right: 28px;
  z-index: 100;
  max-width: 440px;
  background: rgba(15,23,42,0.97);
  border: 1px solid rgba(239,68,68,0.45);
  border-radius: 12px;
  padding: 18px 20px;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.7), 0 0 24px rgba(239,68,68,0.15);
  backdrop-filter: blur(16px);
  color: #FCA5A5;
}
.toast-title { font-weight: 700; font-size: 0.85rem; margin-bottom: 3px; }
.toast-msg   { font-size: 0.83rem; color: #94A3B8; line-height: 1.5; }
.toast-close {
  background: none;
  border: none;
  color: var(--muted);
  cursor: pointer;
  padding: 2px;
  flex-shrink: 0;
  transition: color .15s;
  border-radius: 4px;
}
.toast-close:hover { color: var(--text); }
.toast-close:focus-visible { outline: 2px solid var(--cyan); }

/* ── Toast Transition ───────────────────────────────────── */
.toast-enter-active, .toast-leave-active { transition: opacity .25s, transform .25s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(16px); }

/* ── Reduced Motion (ui-ux-pro-max UX guideline) ────────── */
@media (prefers-reduced-motion: reduce) {
  .progress-shimmer,
  .ai-spinner,
  .chip-warn,
  .chip-err,
  .live-badge,
  .animate-pulse,
  .btn-active:hover,
  .btn-download:hover {
    animation: none !important;
    transition: none !important;
    transform: none !important;
  }
  .toast-enter-active,
  .toast-leave-active { transition: opacity .1s; }
}
</style>
