<template>
  <div class="desk">
    <div class="letter-paper">
      <div class="paper-texture"></div>
      <div class="ruled-lines"></div>
      <div class="crease horizontal"></div>
      <div class="crease vertical"></div>

      <div class="letter-header">
        <div class="header-top">
          <header class="meta">{{ meta }}</header>
          <button type="button" class="copy-btn" @click.stop="handleCopy">
            {{ copied ? "已复制" : "一键复制" }}
          </button>
        </div>
        <div class="title">{{ text }}</div>
      </div>

      <div class="letter-content">
        <div class="desc-dom">{{ displayContent }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from "vue";

const props = defineProps({
  meta: { type: String, default: "NO.042 / PRIVATE LETTER" },
  text: { type: String, default: "About Link Sync" },
  content: { type: String, default: "" },
  visibleGraphemeCount: { type: Number, default: null },
});

const copied = ref(false);
let copiedTimer = null;
const graphemeSegmenter = new Intl.Segmenter(undefined, {
  granularity: "grapheme",
});

const displayContent = computed(() => {
  const content = props.content || "";
  if (props.visibleGraphemeCount == null) return content;

  const limit = Math.max(0, Math.floor(props.visibleGraphemeCount));
  if (!Number.isFinite(limit)) return content;

  let current = 0;
  let result = "";
  for (const part of graphemeSegmenter.segment(content)) {
    if (current >= limit) break;
    result += part.segment;
    current += 1;
  }
  return result;
});

function handleCopy() {
  const content = props.content || "";

  const done = () => {
    copied.value = true;
    if (copiedTimer) {
      clearTimeout(copiedTimer);
    }
    copiedTimer = setTimeout(() => {
      copied.value = false;
      copiedTimer = null;
    }, 1500);
  };

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard
      .writeText(content)
      .then(done)
      .catch(() => {
        const textarea = document.createElement("textarea");
        textarea.value = content;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.left = "-9999px";
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
        done();
      });
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.value = content;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
  done();
}

onBeforeUnmount(() => {
  if (copiedTimer) {
    clearTimeout(copiedTimer);
    copiedTimer = null;
  }
});
</script>

<style scoped>
.desk {
  width: 100%;
  padding: 20px 0;
  display: flex;
  justify-content: center;
}

.letter-paper {
  --content-top: 138px;
  position: relative;
  background: #fafaf7;
  width: min(90%, 980px);
  max-width: 100%;
  height: min(820px, calc(100vh - 96px));
  border-radius: 2px;
  box-shadow: 0 1px 1px rgba(255, 255, 255, 0.8) inset,
    0 4px 12px -2px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.paper-texture {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.05;
  mix-blend-mode: multiply;
  z-index: 1;
  background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyBAMAAADsEZWCAAAAGFBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAn97UrAAAACHRSTlMA7v9f/v6+vnY9yG0AAAAJcEhZcwAADsQAAA7EAZUrDhsAAAA6SURBVDjLY2AYBaNgFIyCUTCqAB0InBfIeYfAmQfBqQfB6QfBqQfBeYfA6QfB6QfBeYfAGXUAgzMAABy3D9K697Y4AAAAAElFTkSuQmCC");
}

.ruled-lines {
  position: absolute;
  top: var(--content-top);
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 2;
  background-image: repeating-linear-gradient(
    to bottom,
    transparent,
    transparent 27px,
    rgba(0, 0, 0, 0.04) 27px,
    rgba(0, 0, 0, 0.04) 28px
  );
}

.crease {
  position: absolute;
  pointer-events: none;
  z-index: 3;
}

.crease.horizontal {
  top: 50%;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0.4) 0%,
    rgba(0, 0, 0, 0.01) 100%
  );
}

.crease.vertical {
  top: 0;
  left: 33%;
  width: 2px;
  height: 100%;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0.3) 0%,
    rgba(0, 0, 0, 0.01) 100%
  );
}

.letter-header {
  position: relative;
  z-index: 10;
  height: var(--content-top);
  box-sizing: border-box;
  padding: 40px 40px 40px 10px;
  flex-shrink: 0;
}

.letter-content {
  position: relative;
  z-index: 10;
  padding: 0 40px 30px 30px;
  flex: 1;
  min-height: 0;
  box-sizing: border-box;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-gutter: stable;
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.22) transparent;
}

.header-top {
  margin-left: 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.copy-btn {
  background: transparent;
  color: #6f6f66;
  border: 1.5px solid rgba(111, 111, 102, 0.7);
  padding: 4px 14px;
  min-width: 82px;
  height: 30px;
  line-height: 1;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  border-radius: 3px;
  cursor: pointer;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  transition: all 0.2s;
  user-select: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.copy-btn:hover {
  background: rgba(111, 111, 102, 0.9);
  color: #f8f8f4;
}

.copy-btn:active {
  transform: scale(0.97);
}

.copy-btn:focus-visible {
  outline: 2px solid rgba(111, 111, 102, 0.25);
  outline-offset: 2px;
}

.meta {
  margin-left: 0;
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 11px;
  color: #a8a8a0;
  letter-spacing: 1.5px;
  margin-bottom: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  padding-bottom: 8px;
  display: inline-block;
  width: fit-content;
}

.title {
  margin-left: 30px;
  font-size: 21px;
  font-weight: 600;
  color: #333330;
  margin-bottom: 0;
  font-family: "PingFang SC", "Hiragino Sans GB", sans-serif;
  letter-spacing: 0.2px;
}

.desc-dom {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
  color: #66665e;
  font: 16px/32px -apple-system, BlinkMacSystemFont, "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  padding-top: 8px;
}
</style>
