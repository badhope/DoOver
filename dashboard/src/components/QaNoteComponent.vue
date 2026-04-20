<template>
  <div class="desk">
    <svg width="0" height="0" class="svg-defs">
      <defs>
        <linearGradient id="pencil-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#3a3a38" />
          <stop offset="50%" stop-color="#6e6e6a" />
          <stop offset="100%" stop-color="#a5a5a0" />
        </linearGradient>
      </defs>
    </svg>

    <div class="note-wrap">
      <div class="note-paper">
        <div class="ruled-lines"></div>
        <div class="margin-line"></div>
        <div class="dog-ear"></div>

        <div class="note-body">
          <div class="note-content">
            <header class="meta">{{ meta }}</header>

            <div class="title-row">
              <div class="status-badge">
                <svg viewBox="0 0 24 24" class="badge-svg" v-if="status !== 'success'">
                  <path
                    d="M 16.5 3.5 L 20.5 7.5 L 8 20 L 3.5 21 L 4.5 16.5 Z M 14.5 5.5 L 18.5 9.5"
                    fill="none"
                    stroke="url(#pencil-grad)"
                    stroke-width="1.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
                <svg viewBox="0 0 24 24" class="badge-svg" v-else>
                  <path
                    d="M 5 12.5 L 10 17.5 L 19 7"
                    fill="none"
                    stroke="#5a7a5e"
                    stroke-width="2.2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </div>
              <div class="title">{{ role }}</div>
            </div>

            <div class="desc">{{ question }}</div>

            <div class="qa-action-row" v-if="status !== 'success'">
              <div class="input-group">
                <span class="input-label">A:</span>
                <input
                  type="text"
                  class="pencil-input"
                  v-model="answer"
                  :disabled="status === 'loading' || disabled"
                  :placeholder="placeholder"
                  @keyup.enter="handleSubmit"
                />
              </div>
              <button
                class="submit-btn"
                :disabled="disabled || !answer.trim() || status === 'loading'"
                @click="handleSubmit"
              >
                <span v-if="status === 'loading'" class="anim-dots">
                  <i></i><i></i><i></i>
                </span>
                <span v-else>回答</span>
              </button>
            </div>
            <div v-if="disabled && status !== 'success'" class="connect-tip">WS 未连接，暂不可输入</div>

            <div class="success-feedback" v-if="status === 'success'">
              <div class="answer-row">
                <span class="answer-label">A:</span>
                <span class="answer-text">{{ answer }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref } from "vue";

const props = defineProps({
  meta: { type: String, default: "#Q-042 SECURE-PROMPT" },
  role: { type: String, default: "请补充更多信息" },
  question: {
    type: String,
    default: "请仔细阅读上方片段，并在下方填写你的答案。",
  },
  placeholder: { type: String, default: "在此输入答案..." },
  disabled: { type: Boolean, default: false },
});

const emit = defineEmits(["submit"]);

const answer = ref("");
const status = ref("idle");
let submitTimer = null;

const handleSubmit = () => {
  if (props.disabled) return;
  if (!answer.value.trim() || status.value !== "idle") return;

  status.value = "loading";
  submitTimer = setTimeout(() => {
    submitTimer = null;
    status.value = "success";
    emit("submit", answer.value);
  }, 1500);
};

onBeforeUnmount(() => {
  if (submitTimer) {
    clearTimeout(submitTimer);
    submitTimer = null;
  }
});
</script>

<style scoped>
.desk {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 40px;
  max-width: fit-content;
}

.svg-defs {
  position: absolute;
  width: 0;
  height: 0;
}

.note-wrap {
  position: relative;
  display: inline-block;
  transform: rotate(-0.5deg);
}

.note-paper {
  position: relative;
  background: #fdfdf8;
  padding: 28px 32px 24px 48px;
  width: 360px;
  min-height: 380px;
  border-radius: 2px;
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.06),
    0 6px 16px -4px rgba(0, 0, 0, 0.08),
    inset 0 0 0 1px rgba(0, 0, 0, 0.03);
  overflow: hidden;
}

.ruled-lines {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    to bottom,
    transparent 0px,
    transparent 27px,
    #d4d8cc 27px,
    #d4d8cc 28px
  );
  opacity: 0.4;
  mask-image: linear-gradient(to bottom, transparent 0%, black 12%, black 85%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 12%, black 85%, transparent 100%);
}

.margin-line {
  position: absolute;
  left: 40px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #d4726a;
  opacity: 0.35;
  pointer-events: none;
}

.dog-ear {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #fdfdf8 50%, #e8e5dc 50%);
  box-shadow: -2px -2px 4px rgba(0, 0, 0, 0.04);
  z-index: 5;
}

.note-body {
  position: relative;
  z-index: 2;
}

.note-content {
  display: flex;
  flex-direction: column;
}

.meta {
  font-family: ui-monospace, SFMono-Regular, "Menlo", monospace;
  font-size: 10px;
  color: #b0b0a8;
  letter-spacing: 0.8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.title-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 8px;
}

.status-badge {
  width: 26px;
  height: 26px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
  border: 1.5px solid rgba(0, 0, 0, 0.08);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.6);
}

.badge-svg {
  width: 16px;
  height: 16px;
  display: block;
}

.title {
  font-size: 15px;
  font-weight: 600;
  color: #2c2c28;
  line-height: 1.5;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
}

.desc {
  font-size: 13px;
  color: #807e76;
  line-height: 1.6;
  margin-bottom: 18px;
  margin-top: 2px;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
}

.qa-action-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.input-group {
  display: flex;
  align-items: baseline;
  flex: 1;
  border-bottom: 1.5px dashed #b5b3aa;
  padding-bottom: 2px;
  transition: border-color 0.3s ease;
}

.input-group:focus-within {
  border-bottom-style: solid;
  border-bottom-color: #3a3a38;
}

.input-label {
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 13px;
  color: #a5a5a0;
  font-weight: 600;
  margin-right: 6px;
  flex-shrink: 0;
  user-select: none;
}

.pencil-input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 4px 0;
  font-size: 14px;
  color: #2c2c28;
  font-family: "PingFang SC", "Hiragino Sans GB", sans-serif;
  outline: none;
}

.pencil-input::placeholder {
  color: #c5c3ba;
  font-style: italic;
  font-size: 13px;
}

.submit-btn {
  background: transparent;
  color: #3a3a38;
  border: 1.5px solid #3a3a38;
  padding: 5px 16px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  border-radius: 2px;
  cursor: pointer;
  font-family: system-ui, sans-serif;
  transition: all 0.2s;
  flex-shrink: 0;
  user-select: none;
}

.submit-btn:hover:not(:disabled) {
  background: #3a3a38;
  color: #fdfdf8;
}

.submit-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.submit-btn:disabled {
  border-color: #c5c3ba;
  color: #c5c3ba;
  cursor: not-allowed;
}

.connect-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #9f9382;
}

.anim-dots {
  display: inline-flex;
  gap: 4px;
  align-items: center;
  height: 16px;
}

.anim-dots i {
  display: block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: currentColor;
  animation: dot-bounce 1s ease-in-out infinite;
}

.anim-dots i:nth-child(2) {
  animation-delay: 0.15s;
}

.anim-dots i:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes dot-bounce {
  0%,
  80%,
  100% {
    opacity: 0.25;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-4px);
  }
}

.success-feedback {
  padding-top: 4px;
}

.answer-row {
  display: flex;
  align-items: baseline;
  gap: 6px;
  border-bottom: 1.5px solid #6b8f71;
  padding-bottom: 2px;
  width: fit-content;
  max-width: 100%;
}

.answer-label {
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 13px;
  color: #5a7a5e;
  font-weight: 700;
  flex-shrink: 0;
}

.answer-text {
  font-size: 14px;
  color: #2c2c28;
  font-family: "PingFang SC", "Hiragino Sans GB", sans-serif;
  font-weight: 500;
  word-break: break-all;
}
</style>