# 8000 主链路 WebSocket（只保留你要的）

## 连接地址

`ws://localhost:8000/ws?session_id=<session_id>`

可选（显式指定）：
- `ws://localhost:8000/ws/guest?session_id=<session_id>`
- `ws://localhost:8000/ws/auth?session_id=<session_id>`

---

## 发什么（客户端 -> 服务端）

全部都是 JSON 文本帧：

### 1) 发起分析 `user_input`
```json
{"type":"user_input","text":"你的经历文本"}
```

### 2) 回答追问 `user_answer`
```json
{"type":"user_answer","field":"follow_up","answer":"你的回答"}
```

### 3) 选择分支 `user_choice`
```json
{"type":"user_choice","field":"choose","user_choice":"选择内容","choice_index":0}
```

### 4) 角色互动回复 `interact_with_role`
```json
{"type":"interact_with_role","field":"interact_with_role","role_name":"母亲","answer":"你的回复"}
```

---

## 收什么（服务端 -> 客户端）

### A) JSON 事件

1. `ask_user`
```json
{"type":"ask_user","question":"...","field":"follow_up"}
```

2. `ask_user_choice`（兼容 `turning_event`）
```json
{"type":"ask_user_choice","alternative_action_list":{"items":[...]},"field":"choose"}
```

3. `interact_with_role`
```json
{"type":"interact_with_role","role_name":"...","question":"...","field":"interact_with_role"}
```

4. `user_answer_received`
```json
{"type":"user_answer_received","field":"...","answer":"..."}
```

### B) 文本流（非 JSON，按行）

- `node:<node_name>`
- `background_node_msg:<stream_chunk>`
- `continue_next_node:<stream_chunk>`
- `Search_Result:<json_string>`
- 其他普通日志行

---

## 如何发送（前端）

```js
function send(ws, payload) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(payload));
  }
}
```

---

## 如何接收（前端）

```js
ws.onmessage = (event) => {
  const raw = String(event.data);

  // 1) 先按 JSON 事件处理
  try {
    const msg = JSON.parse(raw);
    // msg.type: ask_user / ask_user_choice / interact_with_role / user_answer_received
    return;
  } catch {}

  // 2) 不是 JSON 就按文本流逐行处理
  for (const line of raw.replace(/\r/g, "").split("\n")) {
    if (!line.trim()) continue;
    // line 前缀: node:, background_node_msg:, continue_next_node:, Search_Result:
  }
};
```

---

## 前端发送 + 接收处理示例（完整）

```js
const WS_BASE_URL = "ws://localhost:8000/ws";
const sessionId = crypto.randomUUID();
const ws = new WebSocket(`${WS_BASE_URL}?session_id=${sessionId}`);

let pendingQuestion = null; // { field, question }
let pendingRole = null; // { field, role_name, question }
let pendingChoiceField = "choose";

function send(payload) {
  if (ws.readyState !== WebSocket.OPEN) return;
  ws.send(JSON.stringify(payload));
}

// 发送：发起分析
function sendUserInput(text) {
  send({
    type: "user_input",
    text: String(text || "").trim(),
  });
}

// 发送：回答追问
function sendUserAnswer(answer) {
  if (!pendingQuestion) return;
  send({
    type: "user_answer",
    field: pendingQuestion.field || "follow_up",
    answer: String(answer || "").trim(),
  });
  pendingQuestion = null;
}

// 发送：选择分支
function sendUserChoice(choiceText, index) {
  send({
    type: "user_choice",
    field: pendingChoiceField || "choose",
    user_choice: String(choiceText || "").trim(),
    choice_index: Number(index) || 0,
  });
}

// 发送：角色互动回复
function sendRoleReply(answer) {
  if (!pendingRole) return;
  send({
    type: "interact_with_role",
    field: pendingRole.field || "interact_with_role",
    role_name: pendingRole.role_name || "",
    answer: String(answer || "").trim(),
  });
  pendingRole = null;
}

// 接收：JSON 事件处理
function handleStructuredEvent(msg) {
  switch (msg.type) {
    case "ask_user":
      pendingQuestion = {
        field: msg.field || "follow_up",
        question: msg.question || "",
      };
      console.log("[ask_user]", pendingQuestion.question);
      return true;

    case "ask_user_choice":
    case "turning_event":
      pendingChoiceField = msg.field || "choose";
      console.log("[ask_user_choice]", msg.alternative_action_list || msg.items || []);
      return true;

    case "interact_with_role":
      pendingRole = {
        field: msg.field || "interact_with_role",
        role_name: msg.role_name || "",
        question: msg.question || "",
      };
      console.log("[interact_with_role]", pendingRole.role_name, pendingRole.question);
      return true;

    case "user_answer_received":
      console.log("[user_answer_received]", msg.field, msg.answer);
      return true;

    default:
      return false;
  }
}

// 接收：文本流处理
function handleTextLine(line) {
  if (line.startsWith("node:")) {
    console.log("[node]", line.slice(5).trim());
    return;
  }
  if (line.startsWith("background_node_msg:")) {
    console.log("[background_chunk]", line.slice("background_node_msg:".length));
    return;
  }
  if (line.startsWith("continue_next_node:")) {
    console.log("[continue_chunk]", line.slice("continue_next_node:".length));
    return;
  }
  if (line.startsWith("Search_Result:")) {
    const raw = line.slice("Search_Result:".length).trim();
    console.log("[search_result_raw]", raw);
    return;
  }
  console.log("[log]", line);
}

ws.onopen = () => {
  console.log("ws connected");
  sendUserInput("我一直放不下那段关系。");
};

ws.onmessage = (event) => {
  const raw = String(event.data || "");

  // 1) 先尝试当作 JSON 事件处理
  try {
    const msg = JSON.parse(raw);
    if (msg && typeof msg === "object" && handleStructuredEvent(msg)) return;
  } catch {}

  // 2) 非 JSON 按文本流逐行处理
  for (const line of raw.replace(/\r/g, "").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    handleTextLine(trimmed);
  }
};

ws.onclose = (e) => {
  console.log("ws closed", e.code, e.reason);
};

ws.onerror = () => {
  console.log("ws error");
};
```
