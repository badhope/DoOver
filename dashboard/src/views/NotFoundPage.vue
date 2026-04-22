<template>
  <div class="not-found-page">
    <div class="page-shell">
      <aside class="sidebar">
        <div class="sidebar-title">{{ sidebarTitle }}</div>
        <div class="sidebar-footer">
          <span class="version">v1.0.0</span>
        </div>
      </aside>

      <main class="content">
        <section class="message-card">
          <span class="kicker">404</span>
          <h1 class="title">{{ titleText }}</h1>
          <p class="desc">{{ descText }}</p>
          <p v-if="path" class="path">{{ pathLabel }}{{ path }}</p>
          <div class="actions">
            <button type="button" class="primary-btn" @click="goHome">{{ homeLabel }}</button>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

defineProps<{ path?: string }>();
const router = useRouter();

const sidebarTitle = "\u7cfb\u7edf\u9875\u9762";
const titleText = "\u60a8\u5f53\u524d\u8bbf\u95ee\u7684\u9875\u9762\u4e0d\u5b58\u5728";
const descText = "\u8bf7\u68c0\u67e5\u8bbf\u95ee\u5730\u5740\u662f\u5426\u6b63\u786e\uff0c\u6216\u8fd4\u56de\u9996\u9875\u7ee7\u7eed\u4f7f\u7528\u3002";
const pathLabel = "\u8def\u5f84\uff1a";
const homeLabel = "\u8fd4\u56de\u9996\u9875";

function goHome() {
  if (router.currentRoute.value.path === "/") return;
  void router.replace("/");
}
</script>

<style scoped>
.not-found-page {
  --md-sys-color-primary: #00639b;
  --md-sys-color-on-primary: #ffffff;
  --md-sys-color-primary-container: #cde5ff;
  --md-sys-color-on-primary-container: #001d33;
  --md-sys-color-surface: #f8f9ff;
  --md-sys-color-surface-container: #eceef4;
  --md-sys-color-surface-container-high: #e6e8ee;
  --md-sys-color-surface-container-highest: #dfe2e8;
  --md-sys-color-on-surface: #191c20;
  --md-sys-color-on-surface-variant: #414852;
  --md-sys-color-outline-variant: #c1c7d1;
  --app-bg: var(--md-sys-color-surface);
  --shell-bg: var(--app-bg);
  --surface: var(--md-sys-color-surface-container);
  --surface-muted: var(--md-sys-color-surface-container-high);
  --surface-soft: var(--md-sys-color-surface-container-highest);
  --text-primary: var(--md-sys-color-on-surface);
  --text-secondary: var(--md-sys-color-on-surface-variant);
  --text-muted: #5a626d;
  --border: var(--md-sys-color-outline-variant);
  --accent: var(--md-sys-color-primary);
  --accent-soft: var(--md-sys-color-primary-container);
  min-height: 100vh;
  background:
    radial-gradient(circle at top right, rgba(0, 99, 155, 0.08), transparent 48%),
    var(--app-bg);
}

.page-shell {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  width: 100%;
  min-height: 100vh;
  background: var(--shell-bg);
}

.sidebar {
  padding: 44px 0 36px;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border-right: 1px solid var(--border);
}

.sidebar-title {
  padding: 0 32px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 2.8px;
}

.sidebar-footer {
  margin-top: auto;
  padding: 28px 32px;
}

.version {
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 1px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.version::before {
  content: "";
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--text-muted);
}

.content {
  display: grid;
  place-items: center;
  padding: 40px 44px;
}

.message-card {
  width: min(680px, 100%);
  border-radius: 24px;
  border: 1px solid var(--border);
  background: var(--surface);
  padding: 34px 36px;
}

.kicker {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--md-sys-color-on-primary-container);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.4px;
}

.title {
  margin: 16px 0 10px;
  color: var(--text-primary);
  font-size: 30px;
  line-height: 1.3;
  letter-spacing: -0.3px;
}

.desc {
  margin: 0;
  color: var(--text-secondary);
  font-size: 15px;
  line-height: 1.7;
}

.path {
  margin: 14px 0 0;
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.5;
  word-break: break-all;
}

.actions {
  margin-top: 26px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.primary-btn {
  min-height: 40px;
  padding: 10px 24px;
  border-radius: 999px;
  border: 1px solid transparent;
  background: var(--accent);
  color: var(--md-sys-color-on-primary);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.1px;
  cursor: pointer;
}

.primary-btn:hover {
  background: #005b8f;
}

.primary-btn:focus-visible {
  outline: 2px solid rgba(0, 99, 155, 0.24);
  outline-offset: 2px;
}

@media (max-width: 968px) {
  .page-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    border-right: none;
    border-bottom: 1px solid var(--border);
    padding: 24px;
  }

  .sidebar-footer {
    display: none;
  }

  .content {
    padding: 24px;
  }

  .message-card {
    padding: 26px 22px;
  }

  .title {
    font-size: 24px;
  }
}
</style>
