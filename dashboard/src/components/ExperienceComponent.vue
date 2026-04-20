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
      <!-- 文件夹标签条 -->
      <div class="tab-label">
        <span>{{ category }}</span>
      </div>

      <!-- 回形针 / 成功勾 -->
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
        <!-- 档案编号 -->
        <div class="file-ref">{{ meta }}</div>

        <!-- 问题标题 -->
        <div class="card-heading">{{ title }}</div>

        <!-- 补充说明 -->
        <div class="card-hint">{{ question }}</div>

        <!-- 填写区域 -->
        <div class="field-section" v-if="status !== 'success'">
          <div class="field-wrap" :class="{ focused: isFocused }">
            <span class="field-arrow">▸</span>
            <textarea
              class="field-input"
              v-model="answer"
              :disabled="status === 'loading'"
              :placeholder="placeholder"
              @focus="isFocused = true"
              @blur="isFocused = false"
            />
          </div>
          <button
            class="archive-btn"
            :disabled="!answer.trim() || status === 'loading'"
            @click="handleSubmit"
          >
            <span v-if="status === 'loading'" class="anim-dots">
              <i></i><i></i><i></i>
            </span>
            <span v-else>归档</span>
          </button>
        </div>

        <!-- 已归档展示 -->
        <div class="done-section" v-else>
          <div class="done-row">
            <span class="done-arrow">▸</span>
            <span class="done-value">{{ answer }}</span>
          </div>
          <div class="stamp">已归档</div>
        </div>
      </div>

      <!-- 折角 -->
      <div class="fold"></div>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, ref } from "vue";

const props = defineProps({
  meta: { type: String, default: "#EXP-007 PERSONAL-FILE" },
  category: { type: String, default: "工作经历" },
  title: { type: String, default: "请描述您最难忘的一段工作经历" },
  question: {
    type: String,
    default: "包括时间、地点、角色以及您从中获得的核心收获。",
  },
  placeholder: { type: String, default: "简要记录这段经历..." },
});

const emit = defineEmits(["submit"]);

const answer = ref("");
const status = ref("idle");
const isFocused = ref(false);
let submitTimer = null;

const handleSubmit = () => {
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
  padding: 24px 20px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: fit-content;
}

/* ====== 档案卡片主体 ====== */
.archive-card {
  position: relative;
  background: #fdfdf8;
  width: 388px;
  min-height: 310px;
  border-radius: 6px;
  padding: 38px 28px 28px;
  box-shadow:
    0 1px 2px rgba(60, 48, 30, 0.04),
    0 4px 14px -2px rgba(60, 48, 30, 0.09),
    inset 0 0 0 1px rgba(60, 48, 30, 0.05);
  transform: rotate(0.4deg);
}

/* ====== 顶部标签条 ====== */
.tab-label {
  position: absolute;
  top: -14px;
  left: 28px;
  background: #c4956a;
  color: #faf6ee;
  padding: 5px 18px;
  border-radius: 4px 4px 0 0;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2.5px;
  box-shadow: 0 -1px 4px rgba(0, 0, 0, 0.06);
}

/* 标签左下小折痕 */
.tab-label::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: -5px;
  border-style: solid;
  border-width: 0 5px 6px 0;
  border-color: transparent #a87d55 transparent transparent;
}

/* ====== 回形针角标 ====== */
.clip-badge {
  position: absolute;
  top: 22px;
  right: 22px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.55);
  border-radius: 5px;
  border: 1px solid rgba(60, 48, 30, 0.06);
  transition: border-color 0.3s;
}

.clip-svg {
  width: 20px;
  height: 20px;
  display: block;
}

/* ====== 内容区 ====== */
.card-inner {
  position: relative;
  display: flex;
  flex-direction: column;
}

.file-ref {
  font-family: ui-monospace, SFMono-Regular, "Menlo", monospace;
  font-size: 9.5px;
  color: #b8ad9c;
  letter-spacing: 1px;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(60, 48, 30, 0.06);
}

.card-heading {
  font-size: 15px;
  font-weight: 600;
  color: #3d3529;
  line-height: 1.55;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
  margin-bottom: 6px;
  padding-right: 40px;
}

.card-hint {
  font-size: 13px;
  color: #8a7e6d;
  line-height: 1.65;
  margin-bottom: 24px;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
}

/* ====== 输入行 ====== */
.field-section {
  display: flex;
  align-items: center;
  gap: 14px;
}

.field-wrap {
  flex: 1;
  display: flex;
  align-items: flex-start;
  border: 1.5px solid #d5ccba;
  border-radius: 4px;
  padding: 8px 10px;
  transition: border-color 0.25s ease, box-shadow 0.15s ease;
  background: rgba(255, 255, 255, 0.45);
}

.field-wrap.focused {
  border-color: #3d3529;
  box-shadow: inset 0 0 0 1px rgba(61, 53, 41, 0.12);
}

.field-arrow {
  font-size: 14px;
  color: #c4b9a8;
  margin-right: 7px;
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
  min-height: 72px;
  max-height: 180px;
  resize: vertical;
  background: transparent;
  border: none;
  padding: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #3d3529;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
  outline: none;
}

.field-input::placeholder {
  color: #cdc3b2;
  font-style: italic;
  font-size: 13px;
}

/* ====== 归档按钮 ====== */
.archive-btn {
  background: transparent;
  color: #3d3529;
  border: 1.5px solid #3d3529;
  padding: 6px 18px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 2px;
  border-radius: 4px;
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
  transform: scale(0.96);
}

.archive-btn:disabled {
  border-color: #cdc3b2;
  color: #cdc3b2;
  cursor: not-allowed;
}

/* ====== 加载弹跳圆点 ====== */
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

/* ====== 已归档状态 ====== */
.done-section {
  position: relative;
  padding-top: 4px;
}

.done-row {
  display: flex;
  align-items: baseline;
  gap: 7px;
  border-bottom: 2px solid #5a7a5e;
  padding-bottom: 3px;
  width: fit-content;
  max-width: 100%;
}

.done-arrow {
  color: #5a7a5e;
  font-size: 14px;
  font-weight: 800;
  flex-shrink: 0;
}

.done-value {
  font-size: 14px;
  color: #3d3529;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
  font-weight: 500;
  word-break: break-all;
}

/* ====== 印章 ====== */
.stamp {
  position: absolute;
  right: 0;
  bottom: -8px;
  border: 2px solid rgba(90, 122, 94, 0.45);
  color: rgba(90, 122, 94, 0.5);
  padding: 3px 14px;
  border-radius: 4px;
  font-size: 10px;
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

/* ====== 右下折角 ====== */
.fold {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 22px;
  height: 22px;
  background: linear-gradient(135deg, #faf6ee 50%, #e2dbd0 50%);
  border-radius: 0 0 6px 0;
  box-shadow: -1px -1px 3px rgba(60, 48, 30, 0.04);
  z-index: 5;
}
</style>
