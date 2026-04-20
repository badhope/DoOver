<template>
  <div class="desk">
    <div class="note-wrap">
      <div class="tape"></div>

      <article class="speech-card">
        <div class="paper-texture"></div>

        <header class="role-row">
          <span class="role-tag">角色</span>
          <h3 class="role-name">{{ roleName }}</h3>
        </header>

        <div class="divider"></div>

        <section class="speech-row">
          <span class="speech-label">发言</span>
          <p class="speech-text">{{ speech }}</p>
        </section>
      </article>
    </div>
  </div>
</template>

<script setup>
defineProps({
  roleName: { type: String, default: "产品经理" },
  speech: {
    type: String,
    default: "我们先聚焦最核心的用户路径，确保关键流程稳定后再扩展功能。",
  },
});
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
  display: inline-block;
  transform: rotate(-0.35deg);
}

.tape {
  position: absolute;
  left: 50%;
  top: -12.8px;
  width: 130px;
  height: 28px;
  transform: translateX(-50%) rotate(-2.5deg);
  z-index: 20;
  background: linear-gradient(
    110deg,
    rgb(255 255 255 / 23%) 0%,
    rgb(255 255 255 / 49%) 40%,
    rgb(255 255 255 / 0%) 50%,
    rgb(255 255 255 / 0%) 60%,
    rgb(255 255 255 / 30%) 100%
  );
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.04),
    inset 0 1px 1px rgba(255, 255, 255, 0.5);
  clip-path: polygon(
    0% 5%,
    2% 20%,
    0% 40%,
    3% 60%,
    1% 80%,
    2% 95%,
    98% 95%,
    100% 80%,
    97% 60%,
    100% 40%,
    98% 20%,
    100% 5%
  );
}

.tape::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyBAMAAADsEZWCAAAAGFBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAn97UrAAAACHRSTlMA7v9f/v6+vnY9yG0AAAAJcEhZcwAADsQAAA7EAZUrDhsAAAA6SURBVDjLY2AYBaNgFIyCUTCqAB0InBfIeYfAmQfBqQfB6QfBqQfBeYfA6QfB6QfBeYfAGXUAgzMAABy3D9K697Y4AAAAAElFTkSuQmCC");
  opacity: 0.06;
  pointer-events: none;
}

.speech-card {
  position: relative;
  width: 390px;
  background: #fafaf7;
  border-radius: 4px;
  padding: 28px 24px 24px;
  box-shadow:
    0 1px 2px rgba(60, 48, 30, 0.05),
    0 6px 18px -4px rgba(60, 48, 30, 0.12),
    inset 0 0 0 1px rgba(60, 48, 30, 0.05);
  overflow: hidden;
}

.paper-texture {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.06;
  z-index: 0;
  background-image: radial-gradient(rgba(0, 0, 0, 0.22) 0.5px, transparent 0.5px);
  background-size: 3px 3px;
}

.role-row,
.divider,
.speech-row {
  position: relative;
  z-index: 1;
}

.role-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.role-tag {
  font-size: 10px;
  letter-spacing: 1.6px;
  color: #faf6ee;
  background: #7f745f;
  padding: 4px 8px;
  border-radius: 3px;
  font-weight: 700;
  flex-shrink: 0;
}

.role-name {
  margin: 0;
  font-size: 17px;
  line-height: 1.4;
  color: #3b352d;
  font-weight: 650;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
}

.divider {
  margin: 12px 0 14px;
  border-bottom: 1px solid rgba(60, 48, 30, 0.12);
}

.speech-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.speech-label {
  margin-top: 2px;
  font-size: 12px;
  color: #9a8e7d;
  font-weight: 700;
  letter-spacing: 1px;
  flex-shrink: 0;
}

.speech-text {
  margin: 0;
  flex: 1;
  font-size: 14px;
  line-height: 1.7;
  color: #4c463e;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
}
</style>
