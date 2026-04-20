<template>
  <div class="desk">
    <section class="search-card" aria-label="搜索内容">
      <div class="paper-texture"></div>

    <header class="search-head">
      <h3 class="search-title">搜索内容</h3>
    </header>

    <div class="divider"></div>

    <div class="search-content">
      <p class="search-text">{{ content }}</p>
    </div>
  </section>
  </div>
</template>

<script setup>
defineProps({
  content: {
    type: String,
    default: "暂无搜索结果。",
  },
});
</script>

<style scoped>
.desk {
  padding: 24px 20px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: min(560px, 100%);
}
.search-card {
  position: relative;
  width: min(560px, 100%);
  background: #fdfdf8;
  border-radius: 6px;
  padding: 24px 24px 20px;
  box-shadow:
    0 2px 6px rgba(60, 48, 30, 0.08),
    0 12px 32px -8px rgba(60, 48, 30, 0.2),
    inset 0 0 0 1px rgba(60, 48, 30, 0.06);
  overflow: hidden;
  box-sizing: border-box;
}

.paper-texture {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.05;
  mix-blend-mode: multiply;
  z-index: 0;
  background-image: radial-gradient(rgba(0, 0, 0, 0.2) 0.5px, transparent 0.5px);
  background-size: 3px 3px;
}

.search-head,
.divider,
.search-content {
  position: relative;
  z-index: 1;
}

.search-title {
  margin: 0;
  font-size: 16px;
  color: #3d3529;
  font-weight: 650;
  line-height: 1.4;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
}

.divider {
  margin: 12px 0 14px;
  border-bottom: 1px solid rgba(60, 48, 30, 0.1);
}

.search-content {
  max-height: min(42vh, 320px);
  overflow: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(60, 48, 30, 0.3) transparent;
}

.search-content::-webkit-scrollbar {
  width: 3px;
}

.search-content::-webkit-scrollbar-track {
  background: transparent;
}

.search-content::-webkit-scrollbar-thumb {
  background: rgba(60, 48, 30, 0.32);
  border-radius: 999px;
}

.search-content::-webkit-scrollbar-thumb:hover {
  background: rgba(60, 48, 30, 0.5);
}

.search-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: #4c463e;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
}
</style>
