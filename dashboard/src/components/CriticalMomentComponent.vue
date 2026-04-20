<template>
  <div class="desk">
    <div class="note-wrap">
      <article class="moment-card">
        <div class="paper-texture"></div>

        <div class="ui-corner top-left"></div>
        <div class="ui-corner top-right"></div>

        <header class="card-header">
          <div class="header-icon">◆</div>
          <div class="title-content">
            <span class="category-tag">TIMELINE EVENT</span>
            <h1 class="card-title">{{ title }}</h1>
          </div>
        </header>

        <div class="branch-container">
          <div class="main-trunk"></div>

          <section class="path-grid">
            <div class="path-node current-path">
              <div class="node-label">
                <span class="dot"></span> {{ leftTitle }}
              </div>
              <div class="choice-box reality-box">
                <div class="corner-bracket"></div>
                <div class="content">{{ leftChoice }}</div>
                <div class="status-badge">RECOREDED</div>
              </div>
            </div>

            <div class="path-node potential-path">
              <div class="node-label">{{ rightTitle }}</div>
              <ul class="choice-list">
                <li
                  v-for="(item, index) in rightChoices"
                  :key="index"
                  class="choice-item"
                  role="button"
                  tabindex="0"
                  @click="handleChoose(item, index)"
                  @keyup.enter="handleChoose(item, index)"
                >
                  <span class="choice-bullet">◇</span>
                  {{ item }}
                </li>
              </ul>
            </div>
          </section>
        </div>

        <div class="ui-footer-line"></div>
      </article>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['submit'])

defineProps({
  title: {
    type: String,
    default: '关键时刻：门外有脚步声，你会？',
  },
  leftTitle: {
    type: String,
    default: '当时做法',
  },
  rightTitle: {
    type: String,
    default: '其他做法',
  },
  leftChoice: {
    type: String,
    default: '躲进柜子',
  },
  rightChoices: {
    type: Array,
    default: () => ['直接开门查看', '关灯误导对方'],
  },
})

const handleChoose = (choiceText, index) => {
  emit('submit', String(choiceText || '').trim(), Number(index) || 0)
}
</script>

<style scoped>
.desk {
  padding: 24px 20px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: fit-content;
}

.note-wrap {
  position: relative;
  transition: transform 0.3s ease;
}

.moment-card {
  position: relative;
  width: 500px;
  background: #fdfdf8;
  border: 1px solid rgba(60, 48, 30, 0.1);
  box-shadow:
    20px 20px 60px rgba(0, 0, 0, 0.05),
    0 0 20px rgba(60, 48, 30, 0.02);
  padding: 30px;
  overflow: hidden;
}

.ui-corner {
  position: absolute;
  width: 10px;
  height: 10px;
  border: 2px solid #9a8e7d;
  opacity: 0.4;
}

.top-left {
  top: 10px;
  left: 10px;
  border-right: 0;
  border-bottom: 0;
}

.top-right {
  top: 10px;
  right: 10px;
  border-left: 0;
  border-bottom: 0;
}

.card-header {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.header-icon {
  color: #9a8e7d;
  font-size: 18px;
  margin-top: 4px;
}

.category-tag {
  font-size: 10px;
  letter-spacing: 2px;
  color: #9a8e7d;
  font-weight: 800;
  display: block;
  margin-bottom: 4px;
}

.card-title {
  font-size: 18px;
  color: #3b352d;
  font-weight: 700;
  line-height: 1.4;
  margin: 0;
}

.branch-container {
  position: relative;
  padding-top: 10px;
}

.main-trunk {
  position: absolute;
  top: -20px;
  left: 50%;
  width: 2px;
  height: 30px;
  background: linear-gradient(to bottom, transparent, rgba(60, 48, 30, 0.14));
  transform: translateX(-50%);
}

.path-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  position: relative;
}

.path-grid::before {
  content: '';
  position: absolute;
  top: 10px;
  left: 10%;
  right: 10%;
  height: 1px;
  background: rgba(60, 48, 30, 0.14);
}

.path-node {
  position: relative;
}

.node-label {
  font-size: 11px;
  color: #9a8e7d;
  font-weight: 700;
  margin-bottom: 15px;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.reality-box {
  background: #f8f8f0;
  padding: 16px;
  border: 1px solid rgba(60, 48, 30, 0.08);
  position: relative;
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  transition: all 0.3s ease;
}

.reality-box .content {
  font-size: 15px;
  color: #3b352d;
  font-weight: 600;
  z-index: 1;
}

.corner-bracket {
  position: absolute;
  inset: 5px;
  border: 1px solid rgba(154, 142, 125, 0.3);
  pointer-events: none;
}

.status-badge {
  position: absolute;
  bottom: -8px;
  right: 10px;
  background: #3b352d;
  color: #fdfdf8;
  font-size: 8px;
  padding: 2px 6px;
  font-weight: 900;
  letter-spacing: 0.5px;
}

.choice-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.choice-item {
  font-size: 14px;
  color: #7c7467;
  padding: 8px 12px;
  border: 1px solid transparent;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  transition: all 0.2s ease;
  cursor: pointer;
  border-radius: 2px;
}

.choice-item:hover {
  background: rgba(154, 142, 125, 0.08);
  color: #3b352d;
  transform: translateX(5px);
}

.choice-bullet {
  color: #9a8e7d;
  font-size: 12px;
}

.ui-footer-line {
  margin-top: 40px;
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(60, 48, 30, 0.1), transparent);
}

.paper-texture {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.04;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}
</style>
