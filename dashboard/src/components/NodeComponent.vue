<template>
  <div class="desk">
    <!-- 存放全局公用的铅笔渐变定义 -->
    <svg width="0" height="0" class="svg-defs">
      <defs>
        <linearGradient id="pencil-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#3a3a38" />
          <!-- 深碳灰 -->
          <stop offset="50%" stop-color="#6e6e6a" />
          <!-- 中石墨 -->
          <stop offset="100%" stop-color="#a5a5a0" />
          <!-- 浅银灰 -->
        </linearGradient>
      </defs>
    </svg>

    <div class="note-wrap">
      <!-- 磨砂隐形胶带 -->
      <div class="tape"></div>
      <div class="note-paper" :class="{ 'is-msg': isMsg }">
        <div class="paper-texture"></div>

        <div class="note-body">
          <div class="status-icon">
            <svg viewBox="0 0 40 40" class="morph-svg">
              <path
                class="pencil-base"
                :class="{ hide: !isLoading }"
                d="M 20 6 C 27.73 6 34 12.27 34 20 C 34 27.73 27.73 34 20 34 C 12.27 34 6 27.73 6 20 C 6 12.27 12.27 6 20 6"
              />
              <path
                class="pencil-stroke"
                :class="{ 'is-check': !isLoading }"
                :d="
                  isLoading
                    ? 'M 20 6 C 27.73 6 34 12.27 34 20 C 34 27.73 27.73 34 20 34 C 12.27 34 6 27.73 6 20 C 6 12.27 12.27 6 20 6'
                    : 'M 10 20 C 12 22 14 24 16 26 C 17 27 18 27.5 19 26 C 23 21 27 16 31 11 C 32 10 33 9 34 8'
                "
              />
            </svg>
          </div>

          <div class="note-content">
            <header class="meta">{{ meta }}</header>
            <div class="title">{{ text }}</div>
            <div class="desc">{{ description }}</div>
          </div>
        </div>

        <div class="crease-line"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const props = defineProps({
  isLoading: { type: Boolean, default: true },
  isMsg: { type: Boolean, default: false }, // 新增
  meta: { type: String, default: "#042 LINE-SYNC" },
  text: { type: String, default: "数据链路同步" },
  description: {
    type: String,
    default: "正在通过加密信道传输数据分片，请稍后...",
  },
});
</script>

<style scoped>
.desk {
  padding: 10px;
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

/* ================= 纸张容器 ================= */
.note-wrap {
  position: relative;
  display: inline-block;
}
.note-paper.is-msg {
  background: #e5fff4; /* 浅绿色：青春薄荷感 */
}
.note-paper {
  position: relative;
  background: #fafaf7;
  padding: calc(19.2px + 12px) 30px 24px;
  min-width: 340px;
  clip-path: polygon(
    0% 1%,
    4% 0%,
    8% 2%,
    14% 0%,
    21% 3%,
    26% 0%,
    33% 2%,
    41% 0%,
    48% 3%,
    55% 1%,
    63% 2%,
    71% 0%,
    78% 3%,
    85% 0%,
    92% 2%,
    100% 1%,
    99% 9%,
    100% 17%,
    98% 25%,
    100% 34%,
    99% 42%,
    100% 51%,
    98% 59%,
    100% 68%,
    99% 77%,
    100% 86%,
    98% 94%,
    100% 100%,
    94% 98%,
    88% 100%,
    81% 99%,
    74% 100%,
    67% 98%,
    60% 100%,
    53% 99%,
    46% 100%,
    39% 98%,
    31% 100%,
    24% 99%,
    17% 100%,
    10% 98%,
    4% 100%,
    0% 99%,
    1% 92%,
    0% 84%,
    2% 75%,
    0% 67%,
    1% 58%,
    0% 50%,
    2% 41%,
    0% 33%,
    1% 24%,
    0% 16%,
    2% 8%
  );
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1),
    0 10px 25px -10px rgba(0, 0, 0, 0.08);
}

/* ================= 高级磨砂隐形胶带 (重点优化) ================= */
.tape {
  position: absolute;
  left: 50%;
  top: -12.8px;
  width: 130px;
  height: 28px; /* 稍微调窄，显得更轻盈不臃肿 */
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

  /* 极轻薄的外阴影 + 微弱反光的顶边缘内阴影，使它看起来完全紧贴在纸上 */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04),
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

/* 在胶带表层平铺微弱的噪点，这就是真正带来“高级哑光/磨砂颗粒感”的魔法 */
.tape::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyBAMAAADsEZWCAAAAGFBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAn97UrAAAACHRSTlMA7v9f/v6+vnY9yG0AAAAJcEhZcwAADsQAAA7EAZUrDhsAAAA6SURBVDjLY2AYBaNgFIyCUTCqAB0InBfIeYfAmQfBqQfB6QfBqQfBeYfA6QfB6QfBeYfAGXUAgzMAABy3D9K697Y4AAAAAElFTkSuQmCC");
  opacity: 0.06;
  pointer-events: none;
}

/* ================= 纸张元素 ================= */
.paper-texture {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyBAMAAADsEZWCAAAAGFBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAn97UrAAAACHRSTlMA7v9f/v6+vnY9yG0AAAAJcEhZcwAADsQAAA7EAZUrDhsAAAA6SURBVDjLY2AYBaNgFIyCUTCqAB0InBfIeYfAmQfBqQfB6QfBqQfBeYfA6QfB6QfBeYfAGXUAgzMAABy3D9K697Y4AAAAAElFTkSuQmCC");
  opacity: 0.04;
  mix-blend-mode: multiply;
}

.note-body {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  z-index: 2;
  position: relative;
  margin-top: 5px;
}

.status-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.morph-svg {
  width: 32px;
  height: 32px;
  display: block;
}

.pencil-base {
  fill: none;
  stroke: url(#pencil-grad);
  stroke-width: 1.2;
  opacity: 0.2;
  transition: opacity 0.4s ease;
}

.pencil-base.hide {
  opacity: 0;
}

.pencil-stroke {
  fill: none;
  stroke: url(#pencil-grad);
  stroke-width: 2.2;
  stroke-linecap: round;
  stroke-linejoin: round;
  transition: d 0.5s cubic-bezier(0.34, 1.56, 0.64, 1),
    stroke-dasharray 0.5s ease-out;
}

.pencil-stroke:not(.is-check) {
  stroke-dasharray: 30 58;
  animation: stroke-crawl 0.6s linear infinite;
}

.pencil-stroke.is-check {
  stroke-dasharray: 100 0;
  stroke-dashoffset: 0;
  animation: none;
}

@keyframes stroke-crawl {
  from {
    stroke-dashoffset: 88;
  }
  to {
    stroke-dashoffset: 0;
  }
}

.note-content {
  display: flex;
  flex-direction: column;
}

.meta {
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 9px;
  color: #c0c0b8;
  letter-spacing: 1px;
  margin-bottom: 4px;
}

.title {
  font-size: 16px;
  font-weight: 600;
  color: #333330;
  margin-bottom: 2px;
  font-family: "PingFang SC", "Hiragino Sans GB", sans-serif;
}

.desc {
  font-size: 13px;
  color: #7a7a72;
  line-height: 1.5;
  font-family: system-ui, -apple-system, sans-serif;
}

.crease-line {
  position: absolute;
  top: 50%;
  left: 0;
  width: 100%;
  height: 1px;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.02) 0%,
    rgba(0, 0, 0, 0) 50%,
    rgba(255, 255, 255, 0.5) 100%
  );
  pointer-events: none;
}
</style>