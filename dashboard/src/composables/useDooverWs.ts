// src/composables/useDooverWs.ts
import { onBeforeUnmount, ref } from 'vue'

const WS_BASE_URL = 'ws://localhost:8000/ws'
const RECONNECT_INTERVAL_MS = 3000
const TEXT_CHUNK_BOUNDARY = /(?=node:|background_node_msg:|continue_next_msg:|role_node_msg:|Search_Result:)/g
const SEARCH_NODE_KEY = 'search_node'
const SEARCH_RESULT_PREFIXES = ['Search_Result:'] as const

function getOrCreateSessionId() {
    return crypto.randomUUID()
}

export function useDooverWs() {
    const sessionId = getOrCreateSessionId()
    const isConnected = ref(false)

    const pendingQuestion = ref<null | { field: string; question: string }>(null)
    const pendingRole = ref<null | { field: string; role_name: string; question: string }>(null)
    const pendingChoiceField = ref('choose')
    const pendingChoices = ref<any[]>([])
    const nodeMessages = ref<string[]>([])
    type RoleMessage = { roleName: string; text: string }
    const roleMessages = ref<RoleMessage[]>([])
    const backgroundText = ref('')
    const continueText = ref('')
    const searchContent = ref('')

    let ws: WebSocket | null = null
    let reconnectTimer: number | null = null
    let allowReconnect = true

    function clearReconnectTimer() {
        if (reconnectTimer !== null) {
            window.clearTimeout(reconnectTimer)
            reconnectTimer = null
        }
    }

    function scheduleReconnect() {
        if (!allowReconnect || reconnectTimer !== null) return
        reconnectTimer = window.setTimeout(() => {
            reconnectTimer = null
            if (!allowReconnect) return
            connect()
        }, RECONNECT_INTERVAL_MS)
    }

    function send(payload: any) {
        if (!ws || ws.readyState !== WebSocket.OPEN) return
        ws.send(JSON.stringify(payload))
    }

    function sendUserInput(text: string) {
        send({
            type: "user_input",
            text: String(text || "").trim(),
        })
    }

    function sendUserAnswer(answer: any) {
        if (!pendingQuestion.value) return
        send({
            type: "user_answer",
            field: pendingQuestion.value.field || "follow_up",
            answer: String(answer || "").trim(),
        })
        pendingQuestion.value = null
    }

    function sendUserChoice(choiceText: string, index: number) {
        send({
            type: "user_choice",
            field: pendingChoiceField.value || "choose",
            user_choice: String(choiceText || "").trim(),
            choice_index: Number(index) || 0,
        })
    }

    function sendRoleReply(answer: any) {
        if (!pendingRole.value) return
        send({
            type: "interact_with_role",
            field: pendingRole.value.field || "interact_with_role",
            role_name: pendingRole.value.role_name || "",
            answer: String(answer || "").trim(),
        })
        pendingRole.value = null
    }

    function handleStructuredEvent(msg: any) {
        switch (msg.type) {
            case "ask_user":
                pendingQuestion.value = {
                    field: msg.field || "follow_up",
                    question: msg.question || "",
                }
                return true

            case "ask_user_choice":
            case "turning_event":
                pendingChoiceField.value = msg.field || "choose"
                pendingChoices.value = msg.alternative_action_list || msg.items || []
                return true

            case "interact_with_role":
                pendingRole.value = {
                    field: msg.field || "interact_with_role",
                    role_name: msg.role_name || "",
                    question: msg.question || "",
                }
                return true

            case "user_answer_received":
                return true

            default:
                return false
        }
    }

    function normalizeSearchContent(raw: string) {
        const text = raw.trim()
        if (!text) return ''

        let value: any = text
        for (let i = 0; i < 2; i += 1) {
            if (typeof value !== 'string') break
            const current = value.trim()
            if (!current) return ''

            try {
                value = JSON.parse(current)
            } catch {
                value = current
                break
            }
        }

        if (typeof value === 'string') return value

        try {
            return JSON.stringify(value, null, 2)
        } catch {
            return String(value)
        }
    }

    function appendSearchResult(content: string) {
        if (!content.trim()) return
        if (!searchContent.value.trim()) {
            searchContent.value = content
            return
        }
        searchContent.value = `${searchContent.value}\n\n${content}`
    }

    function handleTextChunk(chunk: string) {
        if (chunk.startsWith("background_node_msg:")) {
            backgroundText.value += chunk.slice("background_node_msg:".length)
            return
        }

        if (chunk.startsWith("continue_next_msg:")) {
            continueText.value += chunk.slice("continue_next_msg:".length)
            return
        }

        if (chunk.startsWith("role_node_msg:")) {
            const content = chunk.slice("role_node_msg:".length).trim()
            const sep = "->"
            const idx = content.indexOf(sep)

            if (idx >= 0) {
                roleMessages.value.push({
                    roleName: content.slice(0, idx).trim(),
                    text: content.slice(idx + sep.length).trim(),
                })
            } else {
                roleMessages.value.push({ roleName: "", text: content })
            }

            return
        }

        const searchPrefix = SEARCH_RESULT_PREFIXES.find((prefix) => chunk.startsWith(prefix))
        if (searchPrefix) {
            const content = normalizeSearchContent(chunk.slice(searchPrefix.length))
            appendSearchResult(content)
            nodeMessages.value.push(SEARCH_NODE_KEY)
            return
        }

        if (chunk.startsWith("node:")) {
            nodeMessages.value.push(chunk.slice(5).trim())
        }
    }

    function connect() {
        if (!allowReconnect) return
        if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
            return
        }

        const socket = new WebSocket(`${WS_BASE_URL}?session_id=${sessionId}`)
        ws = socket

        socket.onopen = () => {
            isConnected.value = true
            clearReconnectTimer()
        }

        socket.onclose = () => {
            if (ws === socket) ws = null
            isConnected.value = false
            scheduleReconnect()
        }

        socket.onerror = () => {
            isConnected.value = false
            if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
                socket.close()
            } else {
                scheduleReconnect()
            }
        }

        socket.onmessage = (event) => {
            const raw = String(event.data || "")

            try {
                const msg = JSON.parse(raw)
                if (msg && typeof msg === "object" && handleStructuredEvent(msg)) return
            } catch { }

            const chunks = raw.replace(/\r/g, "").split(TEXT_CHUNK_BOUNDARY)
            for (const chunk of chunks) {
                if (!chunk) continue
                handleTextChunk(chunk)
            }
        }
    }

    connect()

    onBeforeUnmount(() => {
        allowReconnect = false
        clearReconnectTimer()
        if (!ws) return
        ws.onopen = null
        ws.onclose = null
        ws.onerror = null
        ws.onmessage = null
        ws.close()
        ws = null
        isConnected.value = false
    })

    return {
        sessionId,
        isConnected,
        pendingQuestion,
        pendingRole,
        pendingChoiceField,
        pendingChoices,
        nodeMessages,
        roleMessages,
        backgroundText,
        continueText,
        searchContent,
        send,
        sendUserInput,
        sendUserAnswer,
        sendUserChoice,
        sendRoleReply,
    }
}
