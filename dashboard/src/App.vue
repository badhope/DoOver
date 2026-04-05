<script setup lang="ts">
import { clearCache, setLocale } from '@chenglou/pretext'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import PretextBlock from './components/PretextBlock.vue'

type StepState = {
  name: string
  active: boolean
  loading: boolean
}

type TimelineItem = {
  id: number
  label: string
  value: string
}

type SearchItem = {
  title: string
  url: string
  website: string
  date: string
  snippet: string
}

type PendingQuestion = {
  question: string
  field: string
}

type AlternativeActionItem = {
  key_moment: string
  original_action: string
  alternative_action: string
}

type PendingChoice = {
  field: string
  options: AlternativeActionItem[]
}

type PendingRoleInteraction = {
  roleName: string
  question: string
  field: string
}

type RoleInteractionItem = {
  id: number
  speaker: string
  kind: 'question' | 'user'
  content: string
}

type ModalMode = 'input' | 'question' | 'choice' | 'role' | null

const WS_URL = 'ws://localhost:8765'
const RECONNECT_DELAY_MS = 3000
const bodyFont = '400 15px "Microsoft YaHei UI", "PingFang SC", "Segoe UI", sans-serif'
const smallFont = '400 14px "Microsoft YaHei UI", "PingFang SC", "Segoe UI", sans-serif'

const isConnected = ref(false)
const statusText = ref('连接中')
const inputPreview = ref('等待输入')
const steps = ref<StepState[]>([])
const searchItems = ref<SearchItem[]>([])
const searchLoading = ref(false)
const analysisBuffer = ref('')
const timelineItems = ref<TimelineItem[]>([])
const roleInteractions = ref<RoleInteractionItem[]>([])
const activeNode = ref('idle')
const msgInput = ref('')
const pendingQuestion = ref<PendingQuestion | null>(null)
const pendingChoice = ref<PendingChoice | null>(null)
const pendingRoleInteraction = ref<PendingRoleInteraction | null>(null)
const analysisStreaming = ref(false)
const streamRef = ref<HTMLElement | null>(null)
const analysisRef = ref<HTMLElement | null>(null)
const timelineRef = ref<HTMLElement | null>(null)
const roleRef = ref<HTMLElement | null>(null)
const modalInputRef = ref<HTMLTextAreaElement | null>(null)
const isInputModalOpen = ref(true)
const hasSessionStarted = ref(false)

let socket: WebSocket | null = null
let searchBuffer = ''
let lastNodeName = ''
let timelineId = 0
let roleInteractionId = 0
let reconnectTimer: number | null = null
let isUnmounting = false

const modalMode = computed<ModalMode>(() => {
  if (pendingChoice.value) return 'choice'
  if (pendingRoleInteraction.value) return 'role'
  if (pendingQuestion.value) return 'question'
  return isInputModalOpen.value ? 'input' : null
})

const hasBlockingPrompt = computed(() => Boolean(pendingQuestion.value || pendingChoice.value || pendingRoleInteraction.value))

const modalLead = computed(() => {
  if (pendingChoice.value) return 'Choice'
  if (pendingRoleInteraction.value) return 'Role'
  if (pendingQuestion.value) return 'Question'
  return hasSessionStarted.value ? 'New Input' : 'DoOver Input'
})

const modalTitle = computed(() => {
  if (pendingChoice.value) return '选择一个转折分支'
  if (pendingRoleInteraction.value) return '回应角色互动'
  if (pendingQuestion.value) return '补充信息'
  return hasSessionStarted.value ? '发送新的经历' : '开始一轮分析'
})

const modalDescription = computed(() => {
  if (pendingChoice.value) return '后端已经生成多个可选分支，请点击一张卡片继续后续模拟。'
  if (pendingRoleInteraction.value) return '后端正在等待你回复某个角色，这条内容会作为当前角色互动的上下文继续分析。'
  if (pendingQuestion.value) return '后端正在等待这条补充信息，提交后会继续当前分析流程。'
  if (hasSessionStarted.value) return '发送新的经历会开启下一轮分析，并清空当前实时输出。'
  return '先输入你的经历，页面会开始建立节点、搜索和分析流。'
})

const modalButtonLabel = computed(() => {
  if (pendingRoleInteraction.value) return '发送回应'
  if (pendingQuestion.value) return '发送回答'
  return hasSessionStarted.value ? '发送新输入' : '开始分析'
})

const footerHint = computed(() => {
  if (pendingChoice.value) return '当前正在等待你选择一个分支卡片，点击后会立刻继续后端流程。'
  if (pendingRoleInteraction.value) return `当前正在等待你回复角色「${pendingRoleInteraction.value.roleName}」。`
  if (pendingQuestion.value) return '当前正在等待补充信息，问题弹窗会固定显示。'
  if (hasSessionStarted.value) return '需要发起新一轮分析时，点击右上角或底部按钮打开输入弹窗。'
  return '进入页面时会先弹出输入窗口。'
})

const modalPlaceholder = computed(() => {
  if (pendingRoleInteraction.value) return `回复 ${pendingRoleInteraction.value.roleName}...`
  if (pendingQuestion.value) return '补充这条信息...'
  return '输入你的经历，例如：三年之前我和她分手了...'
})

const choiceHint = computed(() => {
  if (!pendingChoice.value) return ''
  return isConnected.value ? '点击一张卡片，前端会立刻把你的选择通过 WebSocket 发回后端。' : '等待 WebSocket 重连后再选择。'
})

const roleCardPill = computed(() => {
  if (pendingRoleInteraction.value) return `等待 ${pendingRoleInteraction.value.roleName}`
  if (roleInteractions.value.length > 0) return `${roleInteractions.value.length} 条记录`
  return 'idle'
})

function setStatus(text: string, connected = false) {
  statusText.value = text
  isConnected.value = connected
}

function resetSession(inputText = '') {
  analysisBuffer.value = ''
  searchBuffer = ''
  pendingQuestion.value = null
  pendingChoice.value = null
  pendingRoleInteraction.value = null
  steps.value = []
  searchItems.value = []
  searchLoading.value = false
  timelineItems.value = []
  roleInteractions.value = []
  activeNode.value = 'idle'
  inputPreview.value = inputText || '等待输入'
  lastNodeName = ''
  analysisStreaming.value = true
}

function addTimeline(label: string, value: string) {
  timelineItems.value.push({
    id: ++timelineId,
    label,
    value,
  })
}

function addRoleInteraction(speaker: string, kind: RoleInteractionItem['kind'], content: string) {
  roleInteractions.value.push({
    id: ++roleInteractionId,
    speaker,
    kind,
    content,
  })
}

function upsertNode(name: string) {
  let current = steps.value.find(step => step.name === name)
  if (!current) {
    current = {
      name,
      active: false,
      loading: false,
    }
    steps.value.push(current)
  }

  for (const step of steps.value) {
    step.active = false
    step.loading = false
  }

  current.active = true
  current.loading = true
  activeNode.value = name
  lastNodeName = name
}

function finishNode(name = lastNodeName) {
  if (!name) return
  const step = steps.value.find(item => item.name === name)
  if (step) step.loading = false
}

function renderSearchLoading() {
  searchLoading.value = true
  searchItems.value = []
}

function appendAnalysis(text: string) {
  analysisBuffer.value += text
}

function normalizeSearchItem(item: unknown): SearchItem {
  const record = typeof item === 'object' && item !== null ? (item as Record<string, unknown>) : {}
  return {
    title: typeof record.title === 'string' ? record.title : '未命名结果',
    url: typeof record.url === 'string' ? record.url : '#',
    website: typeof record.website === 'string' ? record.website : '未知来源',
    date: typeof record.date === 'string' ? record.date : '',
    snippet:
      typeof record.snippet === 'string'
        ? record.snippet
        : typeof record.content === 'string'
          ? record.content
          : '',
  }
}

function renderSearchResult(raw: string) {
  searchBuffer += raw

  let parsed: unknown
  try {
    parsed = JSON.parse(searchBuffer)
  } catch {
    return
  }

  const list = Array.isArray(parsed) ? parsed : []
  searchItems.value = list.map(normalizeSearchItem)
  searchLoading.value = false
  addTimeline('search', `收到 ${searchItems.value.length} 条搜索结果`)
}

function normalizeAlternativeActionItem(item: unknown): AlternativeActionItem | null {
  if (typeof item !== 'object' || item === null) return null

  const record = item as Record<string, unknown>
  const normalized = {
    key_moment: typeof record.key_moment === 'string' ? record.key_moment : '',
    original_action: typeof record.original_action === 'string' ? record.original_action : '',
    alternative_action: typeof record.alternative_action === 'string' ? record.alternative_action : '',
  }

  if (!normalized.key_moment && !normalized.original_action && !normalized.alternative_action) {
    return null
  }

  return normalized
}

function resolveAlternativeActionList(event: Record<string, unknown>): AlternativeActionItem[] {
  const directItems = Array.isArray(event.turning_event)
    ? event.turning_event
    : Array.isArray(event.items)
      ? event.items
      : []

  if (directItems.length > 0) {
    return directItems.map(normalizeAlternativeActionItem).filter((item): item is AlternativeActionItem => item !== null)
  }

  const wrappedList =
    typeof event.alternative_action_list === 'object' && event.alternative_action_list !== null
      ? (event.alternative_action_list as Record<string, unknown>)
      : null

  const wrappedItems = Array.isArray(wrappedList?.items) ? wrappedList.items : []
  return wrappedItems
    .map(normalizeAlternativeActionItem)
    .filter((item): item is AlternativeActionItem => item !== null)
}

function formatAlternativeActionChoice(option: AlternativeActionItem) {
  return [
    `关键时刻：${option.key_moment || '未提供'}`,
    `原做法：${option.original_action || '未提供'}`,
    `替代做法：${option.alternative_action || '未提供'}`,
  ].join('\n')
}

function openInputModal() {
  if (hasBlockingPrompt.value) return
  msgInput.value = ''
  isInputModalOpen.value = true
}

function closeInputModal() {
  if (hasBlockingPrompt.value) return
  isInputModalOpen.value = false
  msgInput.value = ''
}

function clearReconnectTimer() {
  if (reconnectTimer === null) return
  window.clearTimeout(reconnectTimer)
  reconnectTimer = null
}

function scheduleReconnect(status = '连接失败，3 秒后重试') {
  if (isUnmounting || reconnectTimer !== null) return
  setStatus(status, false)
  reconnectTimer = window.setTimeout(() => {
    reconnectTimer = null
    connect()
  }, RECONNECT_DELAY_MS)
}

function handleStructuredEvent(rawEvent: unknown) {
  if (typeof rawEvent !== 'object' || rawEvent === null) return false

  const event = rawEvent as Record<string, unknown>
  if (event.type === 'ask_user') {
    finishNode()
    pendingChoice.value = null
    pendingRoleInteraction.value = null
    pendingQuestion.value = {
      question: typeof event.question === 'string' ? event.question : '请补充更多信息',
      field: typeof event.field === 'string' ? event.field : 'follow_up',
    }
    msgInput.value = ''
    addTimeline('ask', pendingQuestion.value.question)
    return true
  }

  if (event.type === 'ask_user_choice' || event.type === 'turning_event') {
    finishNode()
    const options = resolveAlternativeActionList(event)
    pendingQuestion.value = null
    pendingRoleInteraction.value = null
    pendingChoice.value = {
      field: typeof event.field === 'string' ? event.field : 'choose',
      options,
    }
    isInputModalOpen.value = false
    msgInput.value = ''
    addTimeline('choice', `收到 ${options.length} 个可选分支`)
    return true
  }

  if (event.type === 'interact_with_role') {
    finishNode()
    pendingQuestion.value = null
    pendingChoice.value = null
    pendingRoleInteraction.value = {
      roleName: typeof event.role_name === 'string' ? event.role_name : '角色',
      question: typeof event.question === 'string' ? event.question : '请继续回复这个角色。',
      field: typeof event.field === 'string' ? event.field : 'interact_with_role',
    }
    isInputModalOpen.value = false
    msgInput.value = ''
    addRoleInteraction(pendingRoleInteraction.value.roleName, 'question', pendingRoleInteraction.value.question)
    addTimeline('role', `${pendingRoleInteraction.value.roleName} 发起互动`)
    return true
  }

  if (event.type === 'user_answer_received') {
    const answer = typeof event.answer === 'string' ? event.answer : ''
    const field = typeof event.field === 'string' ? event.field : ''
    if (field === 'interact_with_role' && answer) {
      addRoleInteraction('你', 'user', answer)
      pendingRoleInteraction.value = null
    } else {
      pendingQuestion.value = null
      pendingChoice.value = null
    }
    msgInput.value = ''
    addTimeline('answer', answer)
    return true
  }

  return false
}

function handleLine(rawLine: string) {
  const trimmed = rawLine.trim()
  if (!trimmed) return

  if (trimmed.startsWith('node:')) {
    const nodeName = trimmed.slice(5).trim()
    if (nodeName.toLowerCase().includes('search')) {
      renderSearchLoading()
    }
    upsertNode(nodeName)
    addTimeline('node', nodeName)
    return
  }

  if (trimmed.startsWith('background_node_msg:')) {
    finishNode()
    appendAnalysis(trimmed.slice('background_node_msg:'.length))
    return
  }

  if (trimmed.startsWith('Baidu Search Result:')) {
    finishNode()
    renderSearchResult(trimmed.slice('Baidu Search Result:'.length).trim())
    return
  }

  finishNode()
  addTimeline(lastNodeName || 'log', trimmed)
}

function handleSocketMessage(raw: string) {
  try {
    const event = JSON.parse(raw)
    if (handleStructuredEvent(event)) return
  } catch {
    // noop
  }

  const normalized = String(raw).replace(/\r/g, '')
  for (const line of normalized.split('\n')) {
    handleLine(line)
  }
}

function connect() {
  if (isUnmounting) return
  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
    return
  }

  clearReconnectTimer()
  setStatus('连接中', false)
  const nextSocket = new WebSocket(WS_URL)
  socket = nextSocket

  nextSocket.onopen = () => {
    if (socket !== nextSocket) return
    clearReconnectTimer()
    setStatus('已连接', true)
  }

  nextSocket.onmessage = event => {
    if (socket !== nextSocket) return
    handleSocketMessage(String(event.data))
  }

  nextSocket.onclose = () => {
    if (socket === nextSocket) {
      socket = null
    }
    analysisStreaming.value = false
    scheduleReconnect('连接已断开，3 秒后重试')
  }

  nextSocket.onerror = () => {
    if (socket !== nextSocket) return
    setStatus('连接错误，3 秒后重试', false)
    if (nextSocket.readyState === WebSocket.CONNECTING || nextSocket.readyState === WebSocket.OPEN) {
      nextSocket.close()
      return
    }
    scheduleReconnect('连接错误，3 秒后重试')
  }
}

function sendPayload(payload: Record<string, unknown>) {
  if (!socket || socket.readyState !== WebSocket.OPEN) return
  socket.send(JSON.stringify(payload))
}

function sendMessage() {
  const text = msgInput.value.trim()
  if (!text || pendingChoice.value) return

  if (pendingRoleInteraction.value) {
    sendPayload({
      type: 'interact_with_role',
      field: pendingRoleInteraction.value.field,
      answer: text,
      role_name: pendingRoleInteraction.value.roleName,
    })
    pendingRoleInteraction.value = null
    msgInput.value = ''
    return
  }

  if (pendingQuestion.value) {
    sendPayload({
      type: 'user_answer',
      field: pendingQuestion.value.field,
      answer: text,
    })
    pendingQuestion.value = null
    msgInput.value = ''
    return
  }

  resetSession(text)
  hasSessionStarted.value = true
  isInputModalOpen.value = false
  addTimeline('session', '开始新一轮分析')
  sendPayload({
    type: 'user_input',
    text,
  })
  msgInput.value = ''
}

function sendChoice(option: AlternativeActionItem, index: number) {
  if (!pendingChoice.value || !isConnected.value) return

  const choiceText = formatAlternativeActionChoice(option)
  addTimeline('choice_selected', option.alternative_action || `option_${index + 1}`)
  sendPayload({
    type: 'user_choice',
    field: pendingChoice.value.field,
    user_choice: choiceText,
    choice_index: index,
  })
  pendingChoice.value = null
}

function handleModalKeydown(event: KeyboardEvent) {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault()
    sendMessage()
    return
  }

  if (event.key === 'Escape') {
    closeInputModal()
  }
}

watch(
  [
    analysisBuffer,
    () => timelineItems.value.length,
    () => searchItems.value.length,
    () => roleInteractions.value.length,
    searchLoading,
  ],
  async () => {
    await nextTick()
    if (streamRef.value) {
      streamRef.value.scrollTop = streamRef.value.scrollHeight
    }
    if (analysisRef.value) {
      analysisRef.value.scrollTop = analysisRef.value.scrollHeight
    }
    if (timelineRef.value) {
      timelineRef.value.scrollTop = timelineRef.value.scrollHeight
    }
    if (roleRef.value) {
      roleRef.value.scrollTop = roleRef.value.scrollHeight
    }
  },
  { flush: 'post' },
)

watch(
  [modalMode, isConnected],
  async ([mode, connected]) => {
    if (!mode || !connected || mode === 'choice') return
    await nextTick()
    modalInputRef.value?.focus()
    modalInputRef.value?.setSelectionRange(msgInput.value.length, msgInput.value.length)
  },
  { flush: 'post' },
)

onMounted(() => {
  setLocale(document.documentElement.lang || navigator.language || 'zh-CN')
  connect()
})

onBeforeUnmount(() => {
  isUnmounting = true
  clearReconnectTimer()
  socket?.close()
  clearCache()
})
</script>

<template>
  <div>
    <div class="shell">
      <header class="topbar">
        <div class="title-wrap">
          <p class="eyebrow">DoOver Console</p>
          <h1>DoOver 人生背景流式控制台</h1>
        </div>

        <div class="topbar-actions">
          <button class="ghost-button" type="button" :disabled="hasBlockingPrompt || !isConnected" @click="openInputModal">
            {{ hasSessionStarted ? '发送新输入' : '输入经历' }}
          </button>

          <div class="status-chip" :class="{ connected: isConnected }">
            <span class="status-dot"></span>
            <span>{{ statusText }}</span>
          </div>
        </div>
      </header>

      <div class="layout">
        <aside class="sidebar">
          <section class="sidebar-card input-card">
            <div class="panel-title">Input</div>
            <div class="field-label">当前输入</div>
            <PretextBlock
              class="input-preview"
              :text="inputPreview"
              :font="bodyFont"
              :line-height="26"
              white-space="pre-wrap"
            />
          </section>

          <section class="sidebar-card steps">
            <div class="panel-title">Flow</div>
            <div class="step-list">
              <div
                v-for="step in steps"
                :key="step.name"
                class="step-item"
                :class="{ active: step.active, loading: step.loading }"
              >
                <span class="step-bullet"></span>
                <span class="step-name">{{ step.name }}</span>
              </div>
              <div v-if="steps.length === 0" class="empty-copy">等待流程节点</div>
            </div>
          </section>

          <section class="sidebar-card search-feed">
            <div class="panel-title">Search Feed</div>

            <div v-if="searchLoading" class="search-item loading">
              <span class="spinner"></span>
              <span>正在搜索...</span>
            </div>

            <template v-else-if="searchItems.length > 0">
              <article v-for="item in searchItems" :key="`${item.title}-${item.url}`" class="search-item">
                <a :href="item.url" target="_blank" rel="noreferrer">{{ item.title }}</a>
                <div class="meta">
                  {{ item.website }}
                  <span v-if="item.date"> · {{ item.date }}</span>
                </div>
                <PretextBlock
                  class="search-snippet"
                  :text="item.snippet"
                  :font="smallFont"
                  :line-height="22"
                  white-space="pre-wrap"
                />
              </article>
            </template>

            <div v-else class="empty-copy">等待搜索结果</div>
          </section>
        </aside>

        <main class="main">
          <div ref="streamRef" class="stream">
            <div class="stream-grid">
              <section class="card card-primary analysis-card">
                <div class="card-head">
                  <strong>实时分析</strong>
                  <span class="pill">{{ activeNode }}</span>
                </div>
                <div ref="analysisRef" class="card-body analysis-body">
                  <PretextBlock
                    class="rich-text"
                    :text="analysisBuffer"
                    :font="bodyFont"
                    :line-height="28"
                    white-space="pre-wrap"
                    :streaming="analysisStreaming"
                  />
                </div>
              </section>

              <section class="card card-secondary role-card">
                <div class="card-head">
                  <strong>角色互动</strong>
                  <span class="pill">{{ roleCardPill }}</span>
                </div>
                <div class="card-body role-body">
                  <div ref="roleRef" class="role-feed">
                    <article
                      v-for="item in roleInteractions"
                      :key="item.id"
                      class="role-item"
                      :class="item.kind"
                    >
                      <div class="role-item-head">
                        <span class="role-speaker">{{ item.speaker }}</span>
                        <span class="role-kind">{{ item.kind === 'question' ? '角色提问' : '你的回复' }}</span>
                      </div>
                      <PretextBlock
                        class="role-text"
                        :text="item.content"
                        :font="smallFont"
                        :line-height="24"
                        white-space="pre-wrap"
                      />
                    </article>

                    <div v-if="roleInteractions.length === 0" class="empty-copy">等待角色互动问题</div>
                  </div>
                </div>
              </section>

              <section class="card card-secondary timeline-card">
                <div class="card-head">
                  <strong>执行轨迹</strong>
                  <span class="pill">fixed</span>
                </div>
                <div class="card-body timeline-body">
                  <div ref="timelineRef" class="timeline">
                    <article v-for="item in timelineItems" :key="item.id" class="timeline-item">
                      <div class="timeline-key">{{ item.label }}</div>
                      <PretextBlock
                        class="timeline-value"
                        :text="item.value"
                        :font="smallFont"
                        :line-height="24"
                        white-space="pre-wrap"
                      />
                    </article>

                    <div v-if="timelineItems.length === 0" class="empty-copy">等待会话开始</div>
                  </div>
                </div>
              </section>
            </div>
          </div>

          <footer class="footer-bar">
            <div class="footer-copy">
              <span class="footer-label">Input</span>
              <span>{{ footerHint }}</span>
            </div>

            <button class="ghost-button footer-button" type="button" :disabled="hasBlockingPrompt || !isConnected" @click="openInputModal">
              {{ hasSessionStarted ? '发送新输入' : '开始输入' }}
            </button>
          </footer>
        </main>
      </div>
    </div>

    <transition name="modal-fade">
      <div v-if="modalMode" class="modal-backdrop">
        <section class="modal-panel" aria-modal="true" role="dialog">
          <div class="modal-head">
            <div>
              <div class="modal-lead">{{ modalLead }}</div>
              <h2>{{ modalTitle }}</h2>
            </div>

            <button v-if="modalMode === 'input'" class="modal-close" type="button" @click="closeInputModal">
              ×
            </button>
          </div>

          <p class="modal-description">{{ modalDescription }}</p>

          <div v-if="pendingRoleInteraction" class="modal-question">
            <div class="modal-question-label">Role · {{ pendingRoleInteraction.roleName }}</div>
            <PretextBlock
              class="modal-question-text"
              :text="pendingRoleInteraction.question"
              :font="bodyFont"
              :line-height="26"
              white-space="pre-wrap"
            />
          </div>

          <div v-else-if="pendingQuestion" class="modal-question">
            <div class="modal-question-label">Question</div>
            <PretextBlock
              class="modal-question-text"
              :text="pendingQuestion.question"
              :font="bodyFont"
              :line-height="26"
              white-space="pre-wrap"
            />
          </div>

          <div v-if="pendingChoice" class="modal-choice-grid">
            <button
              v-for="(option, index) in pendingChoice.options"
              :key="`${index}-${option.key_moment}-${option.alternative_action}`"
              class="choice-card"
              type="button"
              :disabled="!isConnected"
              @click="sendChoice(option, index)"
            >
              <div class="choice-card-index">Option {{ index + 1 }}</div>

              <div class="choice-card-section">
                <div class="choice-card-label">Key Moment</div>
                <PretextBlock
                  class="choice-card-text"
                  :text="option.key_moment || '未提供'"
                  :font="smallFont"
                  :line-height="24"
                  white-space="pre-wrap"
                />
              </div>

              <div class="choice-card-section">
                <div class="choice-card-label">Original Action</div>
                <PretextBlock
                  class="choice-card-text"
                  :text="option.original_action || '未提供'"
                  :font="smallFont"
                  :line-height="24"
                  white-space="pre-wrap"
                />
              </div>

              <div class="choice-card-section">
                <div class="choice-card-label">Alternative Action</div>
                <PretextBlock
                  class="choice-card-text"
                  :text="option.alternative_action || '未提供'"
                  :font="smallFont"
                  :line-height="24"
                  white-space="pre-wrap"
                />
              </div>

              <span class="choice-card-action">Select This Path</span>
            </button>

            <div v-if="pendingChoice.options.length === 0" class="empty-copy">后端尚未返回可选分支</div>
          </div>

          <template v-if="!pendingChoice">
            <label class="modal-label" for="messageBox">
              {{ pendingRoleInteraction ? '你的回复' : pendingQuestion ? '你的回答' : '你的经历' }}
            </label>

            <textarea
              id="messageBox"
              ref="modalInputRef"
              v-model="msgInput"
              class="modal-textarea"
              :placeholder="modalPlaceholder"
              :disabled="!isConnected"
              @keydown="handleModalKeydown"
            ></textarea>

            <div class="modal-actions">
              <span class="modal-hint">
                {{ isConnected ? '按 Ctrl/Command + Enter 发送' : '等待 WebSocket 连接恢复后再发送' }}
              </span>

              <button class="primary-button" type="button" :disabled="!isConnected || !msgInput.trim()" @click="sendMessage">
                {{ modalButtonLabel }}
              </button>
            </div>
          </template>

          <div v-else class="modal-choice-hint">
            {{ choiceHint }}
          </div>
        </section>
      </div>
    </transition>
  </div>
</template>
