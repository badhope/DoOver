<template>
  <div class="archive-desk">
    <svg width="0" height="0">
      <defs>
        <linearGradient id="clip-metal" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#9a9a94" />
          <stop offset="50%" stop-color="#cbcbbe" />
          <stop offset="100%" stop-color="#8a8a84" />
        </linearGradient>
      </defs>
    </svg>

    <div class="archive-card">
      <div class="tab-label">
        <span>{{ category }}</span>
      </div>

      <div class="clip-badge">
        <svg v-if="status !== 'success'" viewBox="0 0 28 28" class="clip-svg">
          <path
            d="M11 23V9a4.5 4.5 0 0 1 9 0v12a2.8 2.8 0 0 1-5.6 0V10"
            fill="none"
            stroke="url(#clip-metal)"
            stroke-width="1.6"
            stroke-linecap="round"
          />
        </svg>
        <svg v-else viewBox="0 0 28 28" class="clip-svg">
          <path
            d="M9 14l4 4 7-8"
            fill="none"
            stroke="#5a7a5e"
            stroke-width="2.2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </div>

      <div class="card-inner">
        <div class="file-ref">{{ meta }}</div>
        <div class="card-heading">{{ title }}</div>
        <div class="card-hint">{{ question }}</div>

        <div class="field-section" v-if="status !== 'success'">
          <div class="guide-row">
            <span class="guide-chip">时间地点人物</span>
            <span class="guide-chip">关键冲突与行动</span>
            <span class="guide-chip">结果与反思</span>
          </div>

          <div class="field-wrap" :class="{ focused: isFocused }">
            <span class="field-arrow">▸</span>
            <textarea
              class="field-input"
              v-model="answer"
              :disabled="status === 'loading' || disabled"
              :placeholder="placeholder"
              @focus="isFocused = true"
              @blur="isFocused = false"
            />
          </div>

          <div class="progress-head" :class="{ reached: isRecommendationReached }">
            <span class="progress-tip">{{ progressTip }}</span>
            <span class="progress-count">{{ characterCount }} / {{ RECOMMENDED_CHAR_COUNT }}</span>
          </div>
          <div class="progress-track">
            <span class="progress-fill" :style="{ width: progressWidth }"></span>
          </div>

          <button
            class="archive-btn"
            :disabled="disabled || !answer.trim() || status === 'loading'"
            @click="handleSubmit"
          >
            <span v-if="status === 'loading'" class="anim-dots">
              <i></i><i></i><i></i>
            </span>
            <span v-else>归档</span>
          </button>
          <div v-if="disabled" class="connect-tip">WS 未连接，暂不可输入</div>
        </div>

        <div class="done-section" v-else>
          <div class="done-row">
            <span class="done-arrow">▸</span>
            <span class="done-value">{{ answer }}</span>
          </div>
          <div class="stamp">已归档</div>
        </div>
      </div>

      <div class="fold"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from "vue";

const RECOMMENDED_CHAR_COUNT = 1800;

const props = defineProps({
  meta: {
    type: String,
    default: "#EXP-007",
  },
  category: {
    type: String,
    default: "经历",
  },
  title: {
    type: String,
    default: "一个塑造了你的瞬间",
  },
  question: {
    type: String,
    default: "故事自己会找到结构，只要开始写下第一个真实的画面。",
  },
  placeholder: {
    type: String,
    default: "试着描述：\n• 当时空气是什么味道？\n• 你做了一个什么决定？\n• 现在的你会对当时的自己说什么？",
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["submit"]);

const answer = ref("");
const status = ref("idle");
const isFocused = ref(false);
let submitTimer = null;

const characterCount = computed(() => Array.from(answer.value.trim()).length);

const progressWidth = computed(() => {
  const ratio = Math.min(1, characterCount.value / RECOMMENDED_CHAR_COUNT);
  return `${Math.round(ratio * 100)}%`;
});

const isRecommendationReached = computed(
  () => characterCount.value >= RECOMMENDED_CHAR_COUNT
);

const progressTip = computed(() => {
  const count = characterCount.value;

  if (count === 0) {
    return "先写第一句场景描述，开始后会更容易继续写。";
  }

  if (count < 80) {
    return "很好，继续补充一个细节或对话，内容会更真实。";
  }

  if (count < RECOMMENDED_CHAR_COUNT) {
    return "已经很完整，再补一段“你的思考变化”会更有价值。";
  }

  return "信息非常完整，可以直接归档。";
});

const handleSubmit = () => {
  if (props.disabled) return;
  if (!answer.value.trim() || status.value !== "idle") return;

  status.value = "loading";
  submitTimer = setTimeout(() => {
    submitTimer = null;
    status.value = "success";
    emit("submit", answer.value);
  }, 1200);
};

onBeforeUnmount(() => {
  if (submitTimer) {
    clearTimeout(submitTimer);
    submitTimer = null;
  }
});
</script>

<style scoped>
.archive-desk {
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: min(860px, 95vw);
}

.archive-card {
  position: relative;
  background: #fdfdf8;
  width: min(820px, 95vw);
  min-height: 600px;
  border-radius: 8px;
  padding: 52px 44px 40px;
  box-shadow:
    0 1px 2px rgba(60, 48, 30, 0.04),
    0 6px 18px -2px rgba(60, 48, 30, 0.1),
    inset 0 0 0 1px rgba(60, 48, 30, 0.05);
}

.tab-label {
  position: absolute;
  top: -14px;
  left: 32px;
  background: #c4956a;
  color: #faf6ee;
  padding: 7px 20px;
  border-radius: 4px 4px 0 0;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2.2px;
  box-shadow: 0 -1px 4px rgba(0, 0, 0, 0.06);
}

.tab-label::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: -5px;
  border-style: solid;
  border-width: 0 5px 6px 0;
  border-color: transparent #a87d55 transparent transparent;
}

.clip-badge {
  position: absolute;
  top: 26px;
  right: 28px;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.55);
  border-radius: 6px;
  border: 1px solid rgba(60, 48, 30, 0.06);
}

.clip-svg {
  width: 24px;
  height: 24px;
  display: block;
}

.card-inner {
  position: relative;
  display: flex;
  flex-direction: column;
}

.file-ref {
  font-family: ui-monospace, SFMono-Regular, "Menlo", monospace;
  font-size: 11px;
  color: #b8ad9c;
  letter-spacing: 1.1px;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(60, 48, 30, 0.06);
}

.card-heading {
  font-size: 24px;
  font-weight: 600;
  color: #3d3529;
  line-height: 1.5;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
  margin-bottom: 10px;
  padding-right: 56px;
}

.card-hint {
  font-size: 16px;
  color: #8a7e6d;
  line-height: 1.65;
  margin-bottom: 18px;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
}

.field-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.guide-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.guide-chip {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 11px;
  border-radius: 999px;
  border: 1px dashed rgba(108, 93, 70, 0.35);
  color: #6f6254;
  background: rgba(255, 255, 255, 0.52);
  font-size: 12px;
  letter-spacing: 0.02em;
}

.field-wrap {
  flex: 1;
  display: flex;
  align-items: flex-start;
  border: 2px solid #d5ccba;
  border-radius: 6px;
  padding: 12px 14px;
  transition: border-color 0.25s ease, box-shadow 0.15s ease;
  background: rgba(255, 255, 255, 0.5);
}

.field-wrap.focused {
  border-color: #3d3529;
  box-shadow: inset 0 0 0 1px rgba(61, 53, 41, 0.12);
}

.field-arrow {
  font-size: 16px;
  color: #c4b9a8;
  margin-right: 8px;
  margin-top: 2px;
  flex-shrink: 0;
  user-select: none;
  transition: color 0.25s;
}

.field-wrap.focused .field-arrow {
  color: #3d3529;
}

.field-input {
  flex: 1;
  min-height: 280px;
  max-height: 460px;
  resize: vertical;
  background: transparent;
  border: none;
  padding: 0;
  font-size: 16px;
  line-height: 1.8;
  color: #3d3529;
  caret-color: #9b8f7e;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
  outline: none;
}

.field-wrap.focused .field-input {
  caret-color: #7b6b56;
}

.field-input::placeholder {
  color: #b7aa97;
  font-style: italic;
  font-size: 14px;
  line-height: 1.8;
}

.progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #877864;
}

.progress-tip {
  font-size: 13px;
  line-height: 1.5;
}

.progress-count {
  font-family: ui-monospace, SFMono-Regular, "Menlo", monospace;
  font-size: 12px;
  letter-spacing: 0.03em;
  color: #9b8f7e;
  white-space: nowrap;
}

.progress-head.reached {
  color: #507258;
}

.progress-head.reached .progress-count {
  color: #507258;
}

.progress-track {
  height: 4px;
  border-radius: 999px;
  background: transparent;
  border: 1px solid rgba(111, 98, 84, 0.28);
  overflow: hidden;
}

.progress-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #7b6b56;
  transition: width 0.28s ease;
}

.archive-btn {
  align-self: flex-end;
  background: transparent;
  color: #3d3529;
  border: 1.5px solid #3d3529;
  padding: 9px 22px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 1.8px;
  border-radius: 6px;
  cursor: pointer;
  font-family: system-ui, sans-serif;
  transition: all 0.2s;
  flex-shrink: 0;
  user-select: none;
}

.archive-btn:hover:not(:disabled) {
  background: #3d3529;
  color: #faf6ee;
}

.archive-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.archive-btn:disabled {
  border-color: #cdc3b2;
  color: #cdc3b2;
  cursor: not-allowed;
}

.connect-tip {
  margin-top: 2px;
  font-size: 12px;
  color: #9b8f7e;
  line-height: 1.4;
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

.done-section {
  position: relative;
  padding-top: 4px;
}

.done-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  border-bottom: 2px solid #5a7a5e;
  padding-bottom: 4px;
  width: fit-content;
  max-width: 100%;
}

.done-arrow {
  color: #5a7a5e;
  font-size: 16px;
  font-weight: 800;
  flex-shrink: 0;
}

.done-value {
  font-size: 16px;
  color: #3d3529;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
  font-weight: 500;
  word-break: break-all;
}

.stamp {
  position: absolute;
  right: 0;
  bottom: -8px;
  border: 2px solid rgba(90, 122, 94, 0.45);
  color: rgba(90, 122, 94, 0.5);
  padding: 4px 16px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 4px;
  transform: rotate(-10deg);
  pointer-events: none;
  animation: stamp-press 0.35s cubic-bezier(0.2, 0.8, 0.3, 1.1);
}

@keyframes stamp-press {
  0% {
    opacity: 0;
    transform: rotate(-10deg) scale(1.6);
  }
  50% {
    opacity: 0.7;
    transform: rotate(-10deg) scale(0.92);
  }
  100% {
    opacity: 0.5;
    transform: rotate(-10deg) scale(1);
  }
}

.fold {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #faf6ee 50%, #e2dbd0 50%);
  border-radius: 0 0 8px 0;
  box-shadow: -1px -1px 3px rgba(60, 48, 30, 0.04);
  z-index: 5;
}

@media (max-width: 900px) {
  .archive-desk {
    width: min(94vw, 760px);
    padding: 20px 12px 16px;
  }

  .archive-card {
    width: min(94vw, 760px);
    min-height: 540px;
    padding: 42px 24px 26px;
  }

  .card-heading {
    font-size: 22px;
  }

  .field-input {
    min-height: 220px;
  }
}

@media (max-width: 640px) {
  .tab-label {
    font-size: 10px;
    letter-spacing: 1.5px;
  }

  .card-heading {
    font-size: 19px;
    line-height: 1.45;
  }

  .card-hint {
    font-size: 14px;
  }

  .field-input {
    min-height: 190px;
    font-size: 15px;
  }

  .archive-btn {
    align-self: stretch;
  }
}
</style>