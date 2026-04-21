<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import InteractionPage from "./views/InteractionPage.vue";
import SettingsPage from "./views/SettingsPage.vue";

const currentPath = ref(window.location.pathname);

function updatePath() {
  currentPath.value = window.location.pathname;
}

onMounted(() => {
  window.addEventListener("popstate", updatePath);
});

onBeforeUnmount(() => {
  window.removeEventListener("popstate", updatePath);
});

const routeAccount = computed(() => {
  const normalized = currentPath.value.replace(/^\/+|\/+$/g, "");
  if (!normalized) return "";
  const parts = normalized.split("/").filter(Boolean);
  if (parts.length !== 1) return "";
  return decodeURIComponent(parts[0]);
});
</script>

<template>
  <SettingsPage v-if="routeAccount" :route-account="routeAccount" />
  <InteractionPage v-else />
</template>
