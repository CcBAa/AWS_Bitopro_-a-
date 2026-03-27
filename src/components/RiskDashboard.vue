<template>
  <div class="page-root">

    <!-- ═══════════════════════════════════════════════════════════
         HEADER
    ═══════════════════════════════════════════════════════════ -->
    <header class="hud-header">
      <div class="header-inner">
        <div class="flex items-center gap-3">
          <!-- Shield Icon -->
          <div class="shield-wrap" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6">
              <path fill-rule="evenodd" d="M12.516 2.17a.75.75 0 0 0-1.032 0 11.209 11.209 0 0 1-7.877 3.08.75.75 0 0 0-.722.515A12.74 12.74 0 0 0 2.25 9.75c0 5.942 4.064 10.933 9.563 12.348a.749.749 0 0 0 .374 0c5.499-1.415 9.563-6.406 9.563-12.348 0-1.39-.223-2.73-.635-3.985a.75.75 0 0 0-.722-.516l-.143.001c-2.996 0-5.717-1.17-7.734-3.08Z" clip-rule="evenodd" />
            </svg>
          </div>
          <div>
            <h1 class="site-title">BitoGuard AML</h1>
            <p class="site-sub">AI-Powered Money Laundering Risk Monitor</p>
          </div>
        </div>

        <!-- Status Chips -->
        <div class="flex items-center gap-3">
          <div class="status-chip chip-prod">
            <span class="chip-dot"></span>
            正式環境 PROD
          </div>
          <div class="status-chip chip-ok">
            <span class="chip-dot"></span>
            AWS SageMaker ONLINE
          </div>
          <div class="status-chip" :class="systemChip.cls" aria-live="polite">
            <span class="chip-dot" :class="{ 'animate-pulse': isProcessing }"></span>
            {{ systemChip.text }}
          </div>
        </div>
      </div>
      <div class="header-line" aria-hidden="true"></div>
    </header>

    <!-- ═══════════════════════════════════════════════════════════
         MAIN
    ═══════════════════════════════════════════════════════════ -->
    <main class="main-content">

      <!-- ── UPLOAD CARD ──────────────────────────────────────── -->
      <section class="hud-card" aria-labelledby="upload-heading">
        <h2 id="upload-heading" class="card-heading">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-4 h-4" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.338-2.32 5.75 5.75 0 0 1 1.023 11.095" />
          </svg>
          上傳交易數據集
        </h2>

        <!-- Drop Zone -->
        <div
          class="drop-zone"
          :class="dropZoneCls"
          role="button"
          tabindex="0"
          :aria-disabled="isProcessing"
          aria-label="拖曳 CSV 至此，或按 Enter 選擇"
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
            @change="onFileChange"
          />

          <!-- Empty state -->
          <template v-if="!selectedFile">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" class="w-12 h-12 text-slate-500 mx-auto mb-3" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m6.75 12-3-3m0 0-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
            <p class="drop-text">拖曳 <code class="inline-code">.csv</code> 至此，或<span class="drop-link">點擊選擇</span></p>
            <p class="drop-hint">需包含 user_id 及交易特徵欄位</p>
          </template>

          <!-- File selected state -->
          <template v-else>
            <div class="file-info">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-8 h-8 text-cyan-400 flex-shrink-0" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
              <div class="flex-1 min-w-0">
                <p class="file-name">{{ selectedFile.name }}</p>
                <p class="file-size">{{ fmtSize(selectedFile.size) }}</p>
              </div>
              <button v-if="!isProcessing" class="btn-remove" @click.stop="clearFile">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-3.5 h-3.5" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
                </svg>
                移除
              </button>
            </div>
          </template>
        </div>

        <!-- ── Progress Bar ── -->
        <div v-if="isProcessing || progress > 0" class="progress-wrap" role="progressbar" :aria-valuenow="Math.round(progress)" aria-valuemin="0" aria-valuemax="100">
          <div class="progress-meta">
            <span class="progress-label">{{ progressLabel }}</span>
            <span class="progress-pct">{{ Math.round(progress) }}%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :class="{ 'shimmer': isProcessing }" :style="{ width: progress + '%' }"></div>
          </div>
        </div>

        <!-- ── Submit Button ── -->
        <button
          class="btn-analyze"
          :class="canAnalyze ? 'btn-active' : 'btn-disabled'"
          :disabled="!canAnalyze"
          :aria-busy="isProcessing"
          @click="startAnalysis"
        >
          <template v-if="!isProcessing">
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4" aria-hidden="true">
              <path fill-rule="evenodd" d="M9.315 7.584C12.195 3.883 16.695 1.5 21.75 1.5a.75.75 0 0 1 .75.75c0 5.056-2.383 9.555-6.084 12.436A6.75 6.75 0 0 1 9.75 22.5a.75.75 0 0 1-.75-.75v-4.131A15.838 15.838 0 0 1 6.382 15H2.25a.75.75 0 0 1-.75-.75 6.75 6.75 0 0 1 7.815-6.666ZM15 6.75a2.25 2.25 0 1 0 0 4.5 2.25 2.25 0 0 0 0-4.5Z" clip-rule="evenodd" />
              <path d="M5.26 17.242a.75.75 0 1 0-.897-1.203 5.243 5.243 0 0 0-2.05 5.022.75.75 0 0 0 .625.627 5.243 5.243 0 0 0 5.022-2.051.75.75 0 1 0-1.202-.897 3.744 3.744 0 0 1-3.008 1.51c0-1.23.592-2.323 1.51-3.008Z" />
            </svg>
            啟動風險偵測
          </template>
          <template v-else>
            <span class="ai-spinner" aria-hidden="true"></span>
            AI 分析中…
          </template>
        </button>

        <!-- ENV missing warning -->
        <p v-if="!apiUrlOk" class="env-warn" role="alert">
          ⚠ <code class="font-mono text-xs">VITE_API_URL</code> 未設定，請建立 <code class="font-mono text-xs">.env</code> 檔案
        </p>

        <!-- Error Message -->
        <div v-if="errorMsg" class="error-banner" role="alert">
          <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 flex-shrink-0" aria-hidden="true">
            <path fill-rule="evenodd" d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003ZM12 8.25a.75.75 0 0 1 .75.75v3.75a.75.75 0 0 1-1.5 0V9a.75.75 0 0 1 .75-.75Zm0 8.25a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z" clip-rule="evenodd" />
          </svg>
          <span>{{ errorMsg }}</span>
        </div>
      </section>

      <!-- ── SKELETON SCREEN (loading) ─────────────────────────── -->
      <section v-if="isProcessing" class="hud-card" aria-label="分析中">
        <h2 class="card-heading">
          <span class="skeleton-inline w-4 h-4"></span>
          <span class="skeleton-inline w-32 h-4"></span>
        </h2>
        <div class="skeleton-table">
          <div class="skeleton-header">
            <span v-for="n in 5" :key="n" class="skeleton-cell"></span>
          </div>
          <div v-for="row in 4" :key="row" class="skeleton-row">
            <span v-for="n in 5" :key="n" class="skeleton-cell" :style="{ width: skeletonWidth(n) }"></span>
          </div>
        </div>
        <p class="skeleton-label animate-pulse">AI 模型推論中，Bedrock 報告生成需 30–120 秒…</p>
      </section>

      <!-- ── STATS + RESULTS ──────────────────────────────────── -->
      <template v-if="predictions.length > 0">

        <!-- Stats Row -->
        <div class="stats-grid" role="region" aria-label="風險統計摘要">
          <div v-for="s in statCards" :key="s.label" class="stat-tile" :class="s.tileCls">
            <p class="stat-value" :class="s.numCls">{{ s.value }}</p>
            <p class="stat-label">{{ s.label }}</p>
          </div>
        </div>

        <!-- Results Table Card -->
        <section class="hud-card" aria-labelledby="results-heading">
          <div class="table-topbar">
            <h2 id="results-heading" class="card-heading mb-0">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-4 h-4" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 0 1 0 3.75H5.625a1.875 1.875 0 0 1 0-3.75Z" />
              </svg>
              分析結果
              <span class="result-count">{{ filteredPredictions.length }} / {{ predictions.length }}</span>
            </h2>

            <!-- Filter Controls -->
            <div class="filter-row">
              <input
                v-model="filterText"
                type="search"
                class="filter-input"
                placeholder="搜尋 User ID / 原因…"
                aria-label="搜尋結果"
              />
              <select v-model="filterRisk" class="filter-select" aria-label="風險層級篩選">
                <option value="">全部風險</option>
                <option value="extreme">極端風險</option>
                <option value="high">高風險 ≥ 0.7</option>
                <option value="medium">中風險 0.5–0.7</option>
                <option value="low">低風險 &lt; 0.5</option>
              </select>
            </div>
          </div>

          <!-- Table -->
          <div class="table-scroll" role="region" aria-label="風險評估結果表格">
            <table class="risk-table" aria-live="polite">
              <thead>
                <tr>
                  <th scope="col" class="th-cell cursor-pointer" @click="sortBy('user_id')">
                    User ID <span class="sort-icon">{{ sortIndicator('user_id') }}</span>
                  </th>
                  <th scope="col" class="th-cell">模型判定</th>
                  <th scope="col" class="th-cell">風險等級</th>
                  <th scope="col" class="th-cell">原因摘要</th>
                  <th scope="col" class="th-cell">SAR 報告</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in filteredPredictions"
                  :key="item.user_id"
                  class="td-row"
                  :class="rowCls(item)"
                >
                  <!-- User ID -->
                  <td class="td-cell font-mono text-cyan-300">{{ item.user_id }}</td>

                  <!-- ── 模型判定結果 ── -->
                  <td class="td-cell text-center">
                    <span v-if="item.confidence === 0" class="pred-flag pred-unknown">查無資料</span>
                    <span v-else-if="item.is_extreme_risk" class="pred-flag pred-flagged">疑似洗錢</span>
                    <span v-else class="pred-flag pred-normal">交易正常</span>
                  </td>

                  <!-- ── 風險等級 Badge ── -->
                  <td class="td-cell">
                    <span class="risk-badge" :class="riskBadgeCls(item)">
                      {{ riskLabel(item) }}
                    </span>
                  </td>

                  <!-- Reason -->
                  <td class="td-cell reason-cell" :title="item.reason">{{ item.reason }}</td>

                  <!-- ── SAR Report 按鈕 ──
                       查表版：每筆都有 sar_report，全部顯示按鈕
                  ── -->
                  <td class="td-cell text-center">
                    <button
                      v-if="item.sar_report"
                      class="btn-report"
                      :class="item.is_extreme_risk ? '' : 'btn-report-normal'"
                      :aria-label="`開啟 ${item.user_id} 的判定記錄`"
                      @click="openDrawer(item)"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-3.5 h-3.5" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                      </svg>
                      查看記錄
                    </button>
                    <span v-else class="text-slate-600 text-xs">—</span>
                  </td>
                </tr>

                <!-- Empty filtered state -->
                <tr v-if="filteredPredictions.length === 0">
                  <td colspan="5" class="empty-row">無符合條件的記錄</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>

    </main>

    <!-- ═══════════════════════════════════════════════════════════
         SAR REPORT DRAWER (側邊抽屜)
         ─ 當 drawerItem 不為 null 時從右側滑入
    ═══════════════════════════════════════════════════════════ -->
    <Transition name="drawer">
      <div v-if="drawerItem" class="drawer-overlay" role="dialog" :aria-label="`SAR 報告 — ${drawerItem.user_id}`" aria-modal="true" @click.self="closeDrawer">
        <aside class="drawer-panel">

          <!-- Drawer Header -->
          <div class="drawer-header">
            <div>
              <p class="drawer-tag">{{ drawerItem.is_extreme_risk ? 'SUSPICIOUS ACTIVITY REPORT' : 'USER RECORD' }}</p>
              <h3 class="drawer-uid">User ID：{{ drawerItem.user_id }}</h3>
              <p class="drawer-meta">
                判定結果：
                <span v-if="drawerItem.is_extreme_risk" class="pred-flag pred-flagged" style="font-size:0.65rem">疑似洗錢</span>
                <span v-else-if="drawerItem.confidence === 0" class="pred-flag pred-unknown" style="font-size:0.65rem">查無資料</span>
                <span v-else class="pred-flag pred-normal" style="font-size:0.65rem">交易正常</span>
                ·
                <span class="risk-badge ml-1" :class="riskBadgeCls(drawerItem)">{{ riskLabel(drawerItem) }}</span>
              </p>
            </div>
            <button class="drawer-close" aria-label="關閉報告" @click="closeDrawer">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Action Buttons -->
          <div class="drawer-actions">
            <button class="action-btn" title="複製報告到剪貼板" @click="copyReport">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-3.5 h-3.5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0 0 13.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 0 1-.75.75H9a.75.75 0 0 1-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 0 1-2.25 2.25H6.75A2.25 2.25 0 0 1 4.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0 1 1.927-.184" />
              </svg>
              {{ copyLabel }}
            </button>
            <button class="action-btn action-btn-ghost" title="匯出 PDF（尚未實作）" @click="exportPdfNotice">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-3.5 h-3.5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
              </svg>
              Export PDF
            </button>
          </div>

          <!-- ── 判定記錄內容 ── -->
          <div class="drawer-body">
            <div class="sar-prose">
              <!-- 判定標籤 -->
              <div class="record-badge-row">
                <span v-if="drawerItem.is_extreme_risk" class="record-badge record-badge-risk">🚨 高風險洗錢嫌疑</span>
                <span v-else-if="drawerItem.confidence === 0" class="record-badge record-badge-unknown">⚠️ 查無資料</span>
                <span v-else class="record-badge record-badge-normal">✅ 正常交易用戶</span>
              </div>

              <!-- 原因 -->
              <div class="record-section">
                <p class="record-label">判定原因</p>
                <p class="record-value">{{ drawerItem.reason }}</p>
              </div>

              <!-- SAR 記錄 -->
              <div class="record-section">
                <p class="record-label">系統記錄</p>
                <p class="record-value">{{ drawerItem.sar_report }}</p>
              </div>

              <!-- 其他欄位 -->
              <div class="record-section">
                <p class="record-label">詳細資訊</p>
                <table class="record-table">
                  <tr>
                    <td class="record-key">User ID</td>
                    <td class="record-val">{{ drawerItem.user_id }}</td>
                  </tr>
                  <tr>
                    <td class="record-key">查表命中</td>
                    <td class="record-val">{{ drawerItem.confidence === 1 ? '是' : '否' }}</td>
                  </tr>
                  <tr>
                    <td class="record-key">AI 判定</td>
                    <td class="record-val">{{ drawerItem.is_extreme_risk ? '高風險 (1)' : '正常 (0)' }}</td>
                  </tr>
                </table>
              </div>
            </div>
          </div>

        </aside>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

// ── Marked 設定 ─────────────────────────────────────────────────
// 若改用 markdown-it，將 marked.parse(text) 替換為：
//   import MarkdownIt from 'markdown-it'
//   const md = new MarkdownIt()
//   md.render(text)
marked.setOptions({ breaks: true, gfm: true })

// ── 環境變數 ─────────────────────────────────────────────────────
const API_URL   = import.meta.env.VITE_API_URL
const apiUrlOk  = Boolean(API_URL)

// ── 核心 Refs ────────────────────────────────────────────────────
const fileInput     = ref(null)
const selectedFile  = ref(null)
const isDragging    = ref(false)
const isProcessing  = ref(false)
const progress      = ref(0)
const progressLabel = ref('準備中…')
const predictions   = ref([])   // ← Lambda { predictions: [...] } 解包後存放於此
const errorMsg      = ref('')
const drawerItem    = ref(null) // 當前開啟 SAR 抽屜的項目
const copyLabel     = ref('複製報告')

// ── 篩選 / 排序 ──────────────────────────────────────────────────
const filterText  = ref('')
const filterRisk  = ref('')
const sortKey     = ref('confidence')
const sortDir     = ref('desc')

// ════════════════════════════════════════════════════════════════
// CSV 轉換工具
// 將瀏覽器 File 物件讀成純文字字串，Lambda 以 csv.DictReader 解析
// ════════════════════════════════════════════════════════════════
function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload  = e => resolve(e.target.result)
    reader.onerror = () => reject(new Error('FileReader 讀取失敗'))
    reader.readAsText(file, 'UTF-8')
  })
}

/**
 * 清洗 CSV 字串：
 * 1. Windows CRLF → LF
 * 2. 移除末尾空行
 * 回傳淨化後的 csvText 與 rowCount
 */
function sanitizeCsv(raw) {
  const text = raw
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .replace(/\n+$/, '')

  const lines = text.split('\n').filter(l => l.trim() !== '')
  const rowCount = lines.length - 1 // 扣掉 header
  return { csvText: lines.join('\n'), rowCount }
}

// ════════════════════════════════════════════════════════════════
// 回應解析：從 Lambda 回傳中提取 predictions 陣列
// 支援格式：
//   { predictions: [...] }          ← 主要格式
//   { results: [...] } / [...] 等   ← 向下相容
// ════════════════════════════════════════════════════════════════
function extractPredictions(responseData) {
  if (Array.isArray(responseData?.predictions)) return responseData.predictions
  if (Array.isArray(responseData))              return responseData
  if (Array.isArray(responseData?.results))     return responseData.results
  if (Array.isArray(responseData?.data))        return responseData.data
  throw new Error('後端回傳格式無法識別，請開啟 DevTools > Network 查看原始回應')
}

// ════════════════════════════════════════════════════════════════
// 主分析流程
// ════════════════════════════════════════════════════════════════
async function startAnalysis() {
  if (!canAnalyze.value) return

  isProcessing.value  = true
  predictions.value   = []
  errorMsg.value      = ''
  progress.value      = 5
  progressLabel.value = '讀取 CSV 文件…'

  try {
    const raw = await readFileAsText(selectedFile.value)
    const { csvText, rowCount } = sanitizeCsv(raw)

    if (rowCount <= 0) throw new Error('CSV 檔案沒有資料列（僅含 Header 或完全為空）')

    progress.value      = 20
    progressLabel.value = `已讀取 ${rowCount} 筆，送出至 Lambda…`

    const response = await axios.post(API_URL, csvText, {
      headers: { 'Content-Type': 'text/csv' },
      timeout: 30_000,
    })

    progress.value      = 90
    progressLabel.value = '解析結果…'

    const rawList = extractPredictions(response.data)
    predictions.value   = rawList
    progress.value      = 100
    progressLabel.value = `完成！共 ${rawList.length} 筆`

  } catch (err) {
    progress.value = 0
    errorMsg.value = formatAxiosError(err)
  } finally {
    isProcessing.value = false
  }
}

/**
 * Axios 錯誤格式化：將常見 HTTP / 網路錯誤轉成可讀中文訊息
 */
function formatAxiosError(err) {
  const status  = err.response?.status
  const detail  = err.response?.data?.error ?? err.response?.data?.message

  if (err.code === 'ECONNABORTED' || err.message?.includes('timeout'))
    return `請求超時（30s）：後端仍在執行，請稍後重試或至 Lambda 主控台確認。`
  if (!err.response && err.message?.includes('Network Error'))
    return `CORS 錯誤：請至 Lambda Console 啟用 Function URL CORS，Allow-Origin 設為 *`
  if (status === 400) return `請求格式錯誤 (400)：${detail ?? 'CSV 格式可能有誤'}`
  if (status === 500) return `Lambda 內部錯誤 (500)：${detail ?? '請查看 CloudWatch Logs'}`
  if (status === 403) return `存取被拒 (403)：請確認 Lambda Function URL 授權設定`
  if (status === 504) return `閘道超時 (504)：SageMaker / Bedrock 推論時間過長`

  return err.message ?? '未知錯誤'
}

// ════════════════════════════════════════════════════════════════
// 風險等級判斷（查表版）
// is_extreme_risk = true            → 高風險（紅）
// is_extreme_risk = false, conf = 1 → 正常（綠）
// confidence = 0                    → 查無資料（灰）
// ════════════════════════════════════════════════════════════════
function riskLevel(item) {
  if (item.confidence === 0)   return 'unknown'
  if (item.is_extreme_risk)    return 'extreme'
  return 'low'
}
function riskLabel(item) {
  return { extreme: '高風險', low: '正常', unknown: '查無資料' }[riskLevel(item)]
}
function riskBadgeCls(item) {
  return { extreme: 'badge-extreme', low: 'badge-low', unknown: 'badge-unknown' }[riskLevel(item)]
}
function rowCls(item) {
  return { extreme: 'row-extreme', low: '', unknown: 'row-unknown' }[riskLevel(item)]
}

// ════════════════════════════════════════════════════════════════
// SAR 報告 Drawer
// ════════════════════════════════════════════════════════════════
function openDrawer(item) {
  drawerItem.value = item
  document.body.style.overflow = 'hidden'
}
function closeDrawer() {
  drawerItem.value = null
  document.body.style.overflow = ''
}

/**
 * 將 sar_report 字串轉為可渲染的 HTML
 * 新版 Lambda 回傳純文字，用 marked.parse 處理（含換行）
 * marked.parse 在 v17 為同步，直接呼叫即可
 */
const parsedSarHtml = computed(() => {
  const report = drawerItem.value?.sar_report
  if (!report) return '<p style="color:#64748b">無記錄內容</p>'
  try {
    return marked.parse(String(report))
  } catch {
    // fallback：純文字換行轉 <br>
    return String(report).replace(/\n/g, '<br>')
  }
})

async function copyReport() {
  if (!drawerItem.value?.sar_report) return
  try {
    await navigator.clipboard.writeText(drawerItem.value.sar_report)
    copyLabel.value = '已複製！'
    setTimeout(() => { copyLabel.value = '複製報告' }, 2000)
  } catch {
    copyLabel.value = '複製失敗'
    setTimeout(() => { copyLabel.value = '複製報告' }, 2000)
  }
}

function exportPdfNotice() {
  alert('PDF 匯出功能開發中，目前請使用「複製報告」後貼入文件工具。')
}

// ════════════════════════════════════════════════════════════════
// 篩選 + 排序
// ════════════════════════════════════════════════════════════════
const filteredPredictions = computed(() => {
  let list = predictions.value

  // 依風險層級篩選
  if (filterRisk.value) {
    list = list.filter(item => riskLevel(item) === filterRisk.value)
  }

  // 依關鍵字搜尋（user_id + reason）
  if (filterText.value.trim()) {
    const q = filterText.value.toLowerCase()
    list = list.filter(item =>
      String(item.user_id).toLowerCase().includes(q) ||
      String(item.reason  ?? '').toLowerCase().includes(q)
    )
  }

  // 排序
  if (sortKey.value) {
    list = [...list].sort((a, b) => {
      const va = a[sortKey.value] ?? 0
      const vb = b[sortKey.value] ?? 0
      if (typeof va === 'number') return sortDir.value === 'asc' ? va - vb : vb - va
      return sortDir.value === 'asc'
        ? String(va).localeCompare(String(vb))
        : String(vb).localeCompare(String(va))
    })
  }

  return list
})

function sortBy(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'desc'
  }
}
function sortIndicator(key) {
  if (sortKey.value !== key) return '↕'
  return sortDir.value === 'asc' ? '↑' : '↓'
}

// ════════════════════════════════════════════════════════════════
// Computed: Stats + System Chip
// ════════════════════════════════════════════════════════════════
const statCards = computed(() => {
  const list    = predictions.value
  const risk    = list.filter(i => i.is_extreme_risk).length
  const normal  = list.filter(i => !i.is_extreme_risk && i.confidence === 1).length
  const unknown = list.filter(i => i.confidence === 0).length
  return [
    { label: '查詢總筆數', value: list.length, numCls: 'num-total',   tileCls: 'tile-total'   },
    { label: '高風險',     value: risk,         numCls: 'num-extreme', tileCls: 'tile-extreme' },
    { label: '正常用戶',   value: normal,       numCls: 'num-low',     tileCls: 'tile-low'     },
    { label: '查無資料',   value: unknown,      numCls: 'num-medium',  tileCls: 'tile-medium'  },
  ]
})

const systemChip = computed(() => {
  if (isProcessing.value)         return { text: 'ANALYZING', cls: 'chip-warn' }
  if (predictions.value.length)   return { text: 'COMPLETE',  cls: 'chip-ok'   }
  return { text: 'READY', cls: 'chip-idle' }
})

const canAnalyze = computed(() => selectedFile.value && apiUrlOk && !isProcessing.value)

// ════════════════════════════════════════════════════════════════
// File Handling
// ════════════════════════════════════════════════════════════════
const dropZoneCls = computed(() => {
  if (isProcessing.value) return 'drop-disabled'
  if (isDragging.value)   return 'drop-dragging'
  if (selectedFile.value) return 'drop-selected'
  return 'drop-idle'
})

function onFileChange(e) {
  const f = e.target.files[0]
  if (f) setFile(f)
}
function onDrop(e) {
  isDragging.value = false
  const f = e.dataTransfer.files[0]
  if (f?.name.toLowerCase().endsWith('.csv')) setFile(f)
  else errorMsg.value = '請上傳 .csv 格式文件'
}
function setFile(f) {
  selectedFile.value = f
  predictions.value  = []
  errorMsg.value     = ''
  progress.value     = 0
}
function clearFile() {
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
}

// ════════════════════════════════════════════════════════════════
// Helpers
// ════════════════════════════════════════════════════════════════
function fmtSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 ** 2) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 ** 2).toFixed(2) + ' MB'
}

function skeletonWidth(n) {
  return ['60%', '30%', '20%', '55%', '40%'][n - 1] ?? '50%'
}
</script>

<style scoped>
/* ── Root ─────────────────────────────────────────────────────── */
.page-root {
  min-height: 100vh;
  background-color: #0F172A; /* slate-900 */
  color: #e2e8f0;            /* slate-200 */
  font-family: ui-monospace, 'Cascadia Code', 'Fira Code', monospace;
}

/* ── Header ─────────────────────────────────────────────────────── */
.hud-header {
  position: sticky; top: 0; z-index: 30;
  background: rgba(15, 23, 42, 0.92);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(51, 65, 85, 0.6);
}
.header-inner {
  max-width: 1400px; margin: 0 auto;
  padding: 0.875rem 1.5rem;
  display: flex; align-items: center; justify-content: space-between;
}
.shield-wrap {
  width: 2.25rem; height: 2.25rem;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #1e3a5f, #0f2040);
  border: 1px solid #2563eb44;
  border-radius: 8px; color: #60a5fa;
}
.site-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; letter-spacing: 0.05em; }
.site-sub   { font-size: 0.65rem; color: #64748b; margin-top: 1px; letter-spacing: 0.08em; }
.header-line { height: 1px; background: linear-gradient(90deg, transparent, #2563eb55, transparent); }

/* ── Status Chips ─────────────────────────────────────────────── */
.status-chip {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.25rem 0.65rem; border-radius: 9999px;
  font-size: 0.6rem; font-weight: 700; letter-spacing: 0.1em;
  border: 1px solid transparent;
}
.chip-dot { width: 6px; height: 6px; border-radius: 50%; }
.chip-ok   { background: #052e16; border-color: #15803d44; color: #4ade80; }
.chip-ok .chip-dot { background: #4ade80; }
.chip-err  { background: #450a0a; border-color: #b91c1c44; color: #f87171; }
.chip-err .chip-dot { background: #ef4444; }
.chip-warn { background: #1c1917; border-color: #d9770655; color: #fb923c; }
.chip-warn .chip-dot { background: #f97316; }
.chip-idle { background: #0f172a; border-color: #47556955; color: #64748b; }
.chip-idle .chip-dot { background: #475569; }
.chip-prod { background: #1e1b4b; border-color: #4f46e555; color: #a5b4fc; }
.chip-prod .chip-dot { background: #818cf8; animation: pulse 2s ease-in-out infinite; }

/* ── Main Layout ─────────────────────────────────────────────── */
.main-content {
  max-width: 1400px; margin: 0 auto;
  padding: 1.5rem;
  display: flex; flex-direction: column; gap: 1rem;
}

/* ── Card ─────────────────────────────────────────────────────── */
.hud-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 1.25rem;
}
.card-heading {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
  color: #94a3b8; text-transform: uppercase; margin-bottom: 1rem;
}

/* ── Drop Zone ────────────────────────────────────────────────── */
.drop-zone {
  border: 2px dashed #334155; border-radius: 8px;
  padding: 2rem 1rem; text-align: center;
  cursor: pointer; transition: all 0.2s ease;
}
.drop-idle     { }
.drop-dragging { border-color: #3b82f6; background: #1e3a5f22; }
.drop-selected { border-color: #22d3ee55; border-style: solid; background: #083344; }
.drop-disabled { opacity: 0.5; cursor: not-allowed; }
.drop-text  { font-size: 0.85rem; color: #94a3b8; margin-top: 0.25rem; }
.drop-link  { color: #38bdf8; text-decoration: underline; cursor: pointer; }
.drop-hint  { font-size: 0.7rem; color: #475569; margin-top: 0.4rem; }
.inline-code { background: #0f172a; padding: 0.1rem 0.35rem; border-radius: 4px; font-size: 0.8em; }

.file-info { display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem; text-align: left; }
.file-name { font-size: 0.85rem; color: #e2e8f0; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-size { font-size: 0.7rem; color: #64748b; margin-top: 1px; }

/* ── Progress ─────────────────────────────────────────────────── */
.progress-wrap { margin-top: 0.75rem; }
.progress-meta { display: flex; justify-content: space-between; font-size: 0.7rem; color: #64748b; margin-bottom: 0.3rem; }
.progress-track { height: 4px; background: #0f172a; border-radius: 9999px; overflow: hidden; }
.progress-fill  { height: 100%; background: linear-gradient(90deg, #2563eb, #38bdf8); border-radius: 9999px; transition: width 0.4s ease; }
.shimmer { background-size: 200% 100%; animation: shimmer 1.5s infinite; }
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ── Buttons ─────────────────────────────────────────────────── */
.btn-analyze {
  margin-top: 0.875rem; width: 100%;
  display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
  padding: 0.65rem 1.25rem; border-radius: 7px;
  font-size: 0.8rem; font-weight: 700; letter-spacing: 0.05em;
  border: 1px solid transparent; cursor: pointer;
  transition: all 0.2s;
}
.btn-active {
  background: linear-gradient(135deg, #1d4ed8, #2563eb);
  border-color: #3b82f688; color: #eff6ff;
  box-shadow: 0 0 16px rgba(37, 99, 235, 0.35);
}
.btn-active:hover { box-shadow: 0 0 24px rgba(59, 130, 246, 0.5); transform: translateY(-1px); }
.btn-disabled { background: #1e293b; border-color: #334155; color: #475569; cursor: not-allowed; }

.btn-remove {
  display: inline-flex; align-items: center; gap: 0.3rem;
  padding: 0.3rem 0.6rem; border-radius: 5px;
  font-size: 0.65rem; color: #f87171;
  background: #450a0a22; border: 1px solid #f8717130;
  cursor: pointer; flex-shrink: 0;
  transition: background 0.15s;
}
.btn-remove:hover { background: #450a0a55; }

.btn-report {
  display: inline-flex; align-items: center; gap: 0.3rem;
  padding: 0.3rem 0.6rem; border-radius: 5px;
  font-size: 0.65rem; font-weight: 600; letter-spacing: 0.05em;
  background: #1c1917; border: 1px solid #78350f66;
  color: #fb923c; cursor: pointer;
  transition: all 0.15s;
}
.btn-report:hover { background: #78350f33; border-color: #fb923c66; }
.btn-report-normal { background: #0f172a; border-color: #33415566; color: #64748b; }
.btn-report-normal:hover { background: #1e293b; border-color: #94a3b855; color: #94a3b8; }
.row-unknown { opacity: 0.6; }

/* ── Alerts ───────────────────────────────────────────────────── */
.env-warn { margin-top: 0.6rem; font-size: 0.7rem; color: #fbbf24; }
.error-banner {
  margin-top: 0.75rem; padding: 0.65rem 0.875rem;
  background: #450a0a; border: 1px solid #b91c1c44; border-radius: 7px;
  display: flex; align-items: flex-start; gap: 0.5rem;
  color: #f87171; font-size: 0.75rem; line-height: 1.5;
}

/* ── Skeleton Screen ─────────────────────────────────────────── */
.skeleton-inline {
  display: inline-block; background: #334155;
  border-radius: 4px; animation: pulse 1.5s ease-in-out infinite;
}
.skeleton-table { display: flex; flex-direction: column; gap: 0.5rem; margin: 0.75rem 0; }
.skeleton-header, .skeleton-row {
  display: flex; gap: 0.75rem; align-items: center;
}
.skeleton-header .skeleton-cell { height: 10px; flex: 1; background: #334155; border-radius: 3px; animation: pulse 1.5s infinite; }
.skeleton-row .skeleton-cell    { height: 28px; background: #1e3a5f22; border: 1px solid #334155; border-radius: 5px; flex: 1; animation: pulse 1.5s infinite; }
.skeleton-row .skeleton-cell:nth-child(2) { animation-delay: 0.15s; }
.skeleton-row .skeleton-cell:nth-child(3) { animation-delay: 0.3s; }
.skeleton-label { font-size: 0.7rem; color: #64748b; text-align: center; margin-top: 0.5rem; }
@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50%       { opacity: 1; }
}

/* ── Stats Grid ───────────────────────────────────────────────── */
.stats-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem; }
@media (max-width: 768px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
.stat-tile { padding: 0.875rem; border-radius: 8px; border: 1px solid #334155; }
.stat-value { font-size: 1.75rem; font-weight: 800; line-height: 1; }
.stat-label { font-size: 0.6rem; color: #64748b; margin-top: 0.25rem; text-transform: uppercase; letter-spacing: 0.08em; }
.tile-total   { background: #1e293b; }
.tile-extreme { background: #1a0505; border-color: #7f1d1d44; }
.tile-high    { background: #1a0d00; border-color: #7c2d1244; }
.tile-medium  { background: #1a1000; border-color: #78350f44; }
.tile-low     { background: #021a0a; border-color: #14532d44; }
.num-total   { color: #e2e8f0; }
.num-extreme { color: #ef4444; }
.num-high    { color: #f97316; }
.num-medium  { color: #f59e0b; }
.num-low     { color: #22c55e; }

/* ── Table ────────────────────────────────────────────────────── */
.table-topbar {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1rem;
}
.result-count {
  margin-left: 0.5rem; font-size: 0.65rem;
  background: #0f172a; border: 1px solid #334155;
  padding: 0.1rem 0.4rem; border-radius: 9999px; color: #64748b;
}
.filter-row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.filter-input, .filter-select {
  background: #0f172a; border: 1px solid #334155; border-radius: 6px;
  color: #cbd5e1; font-size: 0.75rem; padding: 0.35rem 0.65rem;
  outline: none; font-family: inherit;
}
.filter-input:focus, .filter-select:focus { border-color: #3b82f6; }
.filter-input  { min-width: 180px; }

.table-scroll { overflow-x: auto; border-radius: 7px; border: 1px solid #334155; }
.risk-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.th-cell {
  padding: 0.6rem 0.875rem; text-align: left;
  background: #0f172a; color: #64748b;
  font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
  border-bottom: 1px solid #334155; user-select: none;
  white-space: nowrap;
}
.th-cell:hover { color: #94a3b8; }
.sort-icon { opacity: 0.5; font-size: 0.6rem; }

.td-row { border-bottom: 1px solid #1e293b; transition: background 0.15s; }
.td-row:hover { background: #1e293b; }
.td-row:last-child { border-bottom: none; }
.td-cell { padding: 0.6rem 0.875rem; color: #cbd5e1; vertical-align: middle; }
.reason-cell { max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #94a3b8; font-size: 0.72rem; }

/* Row tints for extreme / high risk */
.row-extreme { background: rgba(127, 29, 29, 0.12); box-shadow: inset 3px 0 0 #ef4444; }
.row-high    { background: rgba(124, 45, 18, 0.10); box-shadow: inset 3px 0 0 #f97316; }
.row-medium  { background: rgba(120, 53, 15, 0.08); box-shadow: inset 3px 0 0 #f59e0b; }

.empty-row { text-align: center; padding: 2rem; color: #475569; font-size: 0.8rem; }

/* ── Demo Log Window ──────────────────────────────────────────── */
.log-window {
  background: #0a0f1e; border: 1px solid #1e293b; border-radius: 6px;
  padding: 0.75rem; max-height: 200px; overflow-y: auto; font-size: 0.72rem;
  scrollbar-width: thin; scrollbar-color: #334155 transparent;
}
.log-line { display: flex; gap: 0.5rem; margin-bottom: 0.2rem; align-items: baseline; }
.log-ts   { color: #475569; flex-shrink: 0; }
.log-tag  { flex-shrink: 0; font-weight: 700; width: 5rem; }
.log-msg  { color: #94a3b8; }
.tag-info    { color: #38bdf8; }
.tag-warn    { color: #fbbf24; }
.tag-error   { color: #f87171; }
.tag-success { color: #4ade80; }
.log-cursor  { color: #38bdf8; }
.live-badge  {
  margin-left: 0.5rem; padding: 0.1rem 0.4rem; border-radius: 4px;
  background: #450a0a; color: #f87171; font-size: 0.6rem; font-weight: 700;
  letter-spacing: 0.08em; border: 1px solid #b91c1c44;
}

/* ── Confidence Bar ───────────────────────────────────────────── */
.confidence-bar-wrap  { display: flex; align-items: center; gap: 0.5rem; min-width: 120px; }
.confidence-bar-track { flex: 1; height: 5px; background: #0f172a; border-radius: 9999px; overflow: hidden; }
.confidence-bar-fill  { height: 100%; border-radius: 9999px; transition: width 0.5s ease; }
.bar-extreme { background: linear-gradient(90deg, #b91c1c, #ef4444); }
.bar-high    { background: linear-gradient(90deg, #c2410c, #f97316); }
.bar-medium  { background: linear-gradient(90deg, #b45309, #f59e0b); }
.bar-low     { background: linear-gradient(90deg, #15803d, #22c55e); }
.confidence-num { font-size: 0.72rem; font-weight: 700; white-space: nowrap; }

/* ── Risk Badge ───────────────────────────────────────────────── */
.risk-badge {
  display: inline-block; padding: 0.15rem 0.5rem; border-radius: 9999px;
  font-size: 0.6rem; font-weight: 700; letter-spacing: 0.08em; white-space: nowrap;
  border: 1px solid transparent;
}
.badge-extreme { background: #450a0a; border-color: #b91c1c55; color: #f87171; }
.badge-high    { background: #431407; border-color: #c2410c55; color: #fb923c; }
.badge-medium  { background: #292524; border-color: #a16207; color: #fbbf24; }
.badge-low     { background: #052e16; border-color: #15803d55; color: #4ade80; }
.badge-unknown { background: #1e293b; border-color: #47556955; color: #94a3b8; }

/* ── Prediction Flags ─────────────────────────────────────────── */
.pred-flag { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.65rem; font-weight: 600; }
.pred-flagged { background: #450a0a; color: #fca5a5; }
.pred-normal  { background: #052e16; color: #86efac; }
.pred-unknown { background: #1e293b; color: #64748b; }

/* ── Spinner ──────────────────────────────────────────────────── */
.ai-spinner {
  width: 14px; height: 14px;
  border: 2px solid #93c5fd44;
  border-top-color: #93c5fd;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ════════════════════════════════════════════════════════════════
   SAR DRAWER
════════════════════════════════════════════════════════════════ */
.drawer-overlay {
  position: fixed; inset: 0; z-index: 50;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(3px);
  display: flex; justify-content: flex-end;
}
.drawer-panel {
  width: min(640px, 92vw); height: 100%;
  background: #0f172a;
  border-left: 1px solid #334155;
  display: flex; flex-direction: column;
  overflow: hidden;
}
.drawer-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #1e293b;
  flex-shrink: 0;
}
.drawer-tag  { font-size: 0.6rem; letter-spacing: 0.12em; color: #ef4444; font-weight: 700; text-transform: uppercase; }
.drawer-uid  { font-size: 1rem; font-weight: 700; color: #f1f5f9; margin: 0.25rem 0; font-family: ui-monospace, monospace; }
.drawer-meta { font-size: 0.72rem; color: #94a3b8; display: flex; align-items: center; gap: 0.25rem; flex-wrap: wrap; }
.drawer-close {
  background: none; border: none; cursor: pointer;
  color: #64748b; padding: 0.25rem; border-radius: 5px;
  transition: color 0.15s;
}
.drawer-close:hover { color: #f1f5f9; }

.drawer-actions {
  display: flex; gap: 0.5rem; padding: 0.75rem 1.5rem;
  border-bottom: 1px solid #1e293b; flex-shrink: 0;
}
.action-btn {
  display: inline-flex; align-items: center; gap: 0.35rem;
  padding: 0.4rem 0.75rem; border-radius: 6px;
  font-size: 0.7rem; font-weight: 600; cursor: pointer;
  background: #1e293b; border: 1px solid #334155; color: #94a3b8;
  transition: all 0.15s; font-family: inherit;
}
.action-btn:hover { background: #334155; color: #f1f5f9; }
.action-btn-ghost { background: transparent; }

.drawer-body {
  flex: 1; overflow-y: auto; padding: 1.5rem;
  scrollbar-width: thin; scrollbar-color: #334155 transparent;
}

/* ── SAR Prose (markdown-it / marked 輸出樣式) ─────────────────
   替代 @tailwindcss/typography prose-invert，手動實作相同效果
── */
.sar-prose { color: #cbd5e1; font-size: 0.82rem; line-height: 1.75; font-family: ui-sans-serif, system-ui, sans-serif; display: flex; flex-direction: column; gap: 1.25rem; }

.record-badge-row { display: flex; gap: 0.5rem; }
.record-badge { padding: 0.4rem 0.875rem; border-radius: 7px; font-size: 0.8rem; font-weight: 700; }
.record-badge-risk    { background: #450a0a; color: #fca5a5; border: 1px solid #b91c1c44; }
.record-badge-normal  { background: #052e16; color: #86efac; border: 1px solid #15803d44; }
.record-badge-unknown { background: #1e293b; color: #94a3b8; border: 1px solid #47556944; }

.record-section { display: flex; flex-direction: column; gap: 0.35rem; }
.record-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #475569; }
.record-value { color: #e2e8f0; font-size: 0.85rem; line-height: 1.6; background: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 0.75rem 1rem; }

.record-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.record-key { padding: 0.4rem 0.75rem; color: #64748b; width: 35%; background: #0f172a; border-bottom: 1px solid #1e293b; }
.record-val { padding: 0.4rem 0.75rem; color: #e2e8f0; border-bottom: 1px solid #1e293b; font-family: ui-monospace, monospace; }
.sar-prose :deep(h1), .sar-prose :deep(h2), .sar-prose :deep(h3) { color: #f1f5f9; font-weight: 700; margin: 1.25em 0 0.5em; line-height: 1.3; }
.sar-prose :deep(h1) { font-size: 1.1rem; border-bottom: 1px solid #334155; padding-bottom: 0.4rem; }
.sar-prose :deep(h2) { font-size: 0.95rem; color: #e2e8f0; }
.sar-prose :deep(h3) { font-size: 0.85rem; color: #cbd5e1; }
.sar-prose :deep(p)  { margin: 0.6em 0; }
.sar-prose :deep(ul), .sar-prose :deep(ol) { margin: 0.6em 0; padding-left: 1.5em; }
.sar-prose :deep(li) { margin: 0.3em 0; }
.sar-prose :deep(strong) { color: #f87171; font-weight: 700; }
.sar-prose :deep(em)     { color: #fbbf24; }
.sar-prose :deep(code)   { background: #1e293b; border: 1px solid #334155; border-radius: 4px; padding: 0.1em 0.35em; font-size: 0.88em; color: #38bdf8; font-family: ui-monospace, monospace; }
.sar-prose :deep(pre)    { background: #1e293b; border: 1px solid #334155; border-radius: 7px; padding: 0.875rem; overflow-x: auto; margin: 0.75em 0; }
.sar-prose :deep(pre code) { background: none; border: none; padding: 0; color: #94a3b8; }
.sar-prose :deep(blockquote) { border-left: 3px solid #ef4444; margin: 0.75em 0; padding: 0.5em 1em; background: #1a0505; color: #fca5a5; border-radius: 0 5px 5px 0; }
.sar-prose :deep(table) { width: 100%; border-collapse: collapse; margin: 0.75em 0; font-size: 0.78rem; }
.sar-prose :deep(th) { background: #0f172a; padding: 0.4rem 0.75rem; text-align: left; color: #94a3b8; border-bottom: 1px solid #334155; }
.sar-prose :deep(td) { padding: 0.4rem 0.75rem; border-bottom: 1px solid #1e293b; }
.sar-prose :deep(hr) { border: none; border-top: 1px solid #334155; margin: 1em 0; }

/* ── Drawer Transition ────────────────────────────────────────── */
.drawer-enter-active { transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), opacity 0.2s; }
.drawer-leave-active { transition: transform 0.25s ease-in, opacity 0.2s; }
.drawer-enter-from   { transform: translateX(100%); opacity: 0; }
.drawer-leave-to     { transform: translateX(100%); opacity: 0; }
</style>
