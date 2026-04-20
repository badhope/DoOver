<template>
  <section class="error-card" role="alert" aria-live="polite" aria-label="错误提示">
    <div class="error-pin">ERROR</div>

    <div class="error-scroll">
      <div class="error-head">
        <span class="error-dot">!</span>
        <h3 class="error-title">节点执行失败</h3>
      </div>

      <div class="error-meta">#ERR-NODE-ALERT</div>

      <div class="error-row">
        <span class="label">报错节点</span>
        <span class="value">{{ node }}</span>
      </div>

      <div class="error-row message-row">
        <span class="label">报错内容</span>
        <p class="message">{{ message }}</p>
      </div>
    </div>

    <div class="actions">
      <button class="copy-btn" @click="handleCopy">{{ copied ? "已复制" : "一键复制" }}</button>
    </div>

    <div class="error-fold"></div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from "vue";

const props = defineProps({
  node: { type: String, default: "未知节点" },
  message: { type: String, default: "系统返回了未知错误，请稍后重试。" },
});

const copied = ref(false);
let copiedTimer = null;

const copyText = computed(() => `报错节点：${props.node}\n报错内容：${props.message}`);

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(copyText.value);
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = copyText.value;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }

  copied.value = true;
  if (copiedTimer) {
    clearTimeout(copiedTimer);
  }
  copiedTimer = setTimeout(() => {
    copied.value = false;
    copiedTimer = null;
  }, 1500);
};

onBeforeUnmount(() => {
  if (copiedTimer) {
    clearTimeout(copiedTimer);
    copiedTimer = null;
  }
});
</script>

<style scoped>
.error-card {
  position: relative;
  width: min(560px, 100%);
  background: #fdfdf8;
  border-radius: 6px;
  padding: 34px 26px 16px;
  box-shadow:
    0 2px 6px rgba(60, 48, 30, 0.08),
    0 12px 32px -8px rgba(60, 48, 30, 0.24),
    inset 0 0 0 1px rgba(60, 48, 30, 0.06);
  transform: rotate(0.25deg);
  overflow: visible;
  box-sizing: border-box;
}

.error-scroll {
  padding-right: 0;
}

.error-pin {
  position: absolute;
  top: -12px;
  left: 24px;
  background: #b4433f;
  color: #fdf7f6;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1.8px;
  padding: 5px 14px;
  border-radius: 4px 4px 0 0;
  box-shadow: 0 -1px 4px rgba(0, 0, 0, 0.08);
}

.error-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.error-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #b4433f;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.error-title {
  margin: 0;
  font-size: 16px;
  color: #3d3529;
  font-weight: 650;
  line-height: 1.4;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
}

.error-meta {
  font-family: ui-monospace, SFMono-Regular, "Menlo", monospace;
  font-size: 10px;
  color: #b8ad9c;
  letter-spacing: 1px;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(60, 48, 30, 0.06);
}

.error-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.label {
  width: 64px;
  flex-shrink: 0;
  font-size: 12px;
  color: #b4433f;
  font-weight: 700;
  letter-spacing: 1px;
  user-select: none;
}

.value {
  flex: 1;
  font-size: 14px;
  color: #3d3529;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
  line-height: 1.6;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.message-row {
  margin-bottom: 0;
}

.message {
  margin: 0;
  flex: 1;
  border: 1.5px solid #dfb2af;
  background: rgba(180, 67, 63, 0.06);
  border-radius: 4px;
  padding: 10px 12px;
  font-size: 14px;
  line-height: 1.65;
  color: #5e2d2a;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  max-height: min(42vh, 260px);
  overflow: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(180, 67, 63, 0.4) transparent;
}

.message::-webkit-scrollbar {
  width: 3px;
}

.message::-webkit-scrollbar-track {
  background: transparent;
}

.message::-webkit-scrollbar-thumb {
  background: rgba(180, 67, 63, 0.38);
  border-radius: 999px;
}

.message::-webkit-scrollbar-thumb:hover {
  background: rgba(180, 67, 63, 0.55);
}

.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

.copy-btn {
  background: transparent;
  color: #b4433f;
  border: 1.5px solid #b4433f;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.2px;
  border-radius: 4px;
  cursor: pointer;
  font-family: system-ui, sans-serif;
  transition: all 0.2s;
  user-select: none;
}

.copy-btn:hover {
  background: #b4433f;
  color: #fff8f8;
}

.copy-btn:active {
  transform: scale(0.97);
}

.copy-btn:focus-visible {
  outline: 2px solid rgba(180, 67, 63, 0.28);
  outline-offset: 2px;
}

.error-fold {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 22px;
  height: 22px;
  background: linear-gradient(135deg, #faf6ee 50%, #e4d2ce 50%);
  border-radius: 0 0 6px 0;
  box-shadow: -1px -1px 3px rgba(60, 48, 30, 0.06);
}

</style>
