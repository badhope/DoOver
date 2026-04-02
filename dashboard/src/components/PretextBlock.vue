<script setup lang="ts">
import { layoutWithLines, prepareWithSegments, type LayoutLine } from '@chenglou/pretext'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

type WhiteSpaceMode = 'normal' | 'pre-wrap'

const props = withDefaults(
  defineProps<{
    text: string
    font: string
    lineHeight: number
    whiteSpace?: WhiteSpaceMode
    streaming?: boolean
  }>(),
  {
    whiteSpace: 'pre-wrap',
    streaming: false,
  },
)

const blockRef = ref<HTMLElement | null>(null)
const width = ref(0)
let resizeObserver: ResizeObserver | null = null

const prepared = computed(() =>
  prepareWithSegments(props.text, props.font, { whiteSpace: props.whiteSpace }),
)

const layoutResult = computed(() => {
  const nextWidth = Math.max(1, Math.floor(width.value))
  if (!nextWidth) return null
  return layoutWithLines(prepared.value, nextWidth, props.lineHeight)
})

const emptyLine: LayoutLine = {
  text: '',
  width: 0,
  start: { segmentIndex: 0, graphemeIndex: 0 },
  end: { segmentIndex: 0, graphemeIndex: 0 },
}

const displayLines = computed(() => {
  const lines = layoutResult.value?.lines ?? []
  return lines.length > 0 ? lines : [emptyLine]
})

const blockStyle = computed(() => ({
  font: props.font,
  lineHeight: `${props.lineHeight}px`,
  minHeight: `${layoutResult.value?.height ?? props.lineHeight}px`,
}))

function syncWidth() {
  width.value = blockRef.value?.clientWidth ?? 0
}

onMounted(() => {
  syncWidth()
  if (!blockRef.value) return

  resizeObserver = new ResizeObserver(entries => {
    width.value = entries[0]?.contentRect.width ?? blockRef.value?.clientWidth ?? 0
  })
  resizeObserver.observe(blockRef.value)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
})
</script>

<template>
  <div ref="blockRef" class="pretext-block" :style="blockStyle">
    <div
      v-for="(line, index) in displayLines"
      :key="`${line.start.segmentIndex}:${line.start.graphemeIndex}:${index}`"
      class="pretext-line"
      :style="{ minHeight: `${lineHeight}px` }"
    >
      <span>{{ line.text }}</span>
      <span
        v-if="streaming && index === displayLines.length - 1"
        class="pretext-cursor"
        aria-hidden="true"
      ></span>
    </div>
  </div>
</template>

<style scoped>
.pretext-block {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.pretext-line {
  white-space: pre;
  overflow-wrap: normal;
}

.pretext-cursor {
  display: inline-block;
  width: 8px;
  height: 1.05em;
  margin-left: 4px;
  vertical-align: text-bottom;
  border-radius: 999px;
  background: var(--accent, #b95c37);
  animation: blink 1s steps(1) infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}
</style>
