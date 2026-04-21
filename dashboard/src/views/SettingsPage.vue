<template>
  <div class="settings-page">
    <div class="page-shell">
      <aside class="sidebar">
        <div class="sidebar-title">系统设置</div>
        <nav class="nav-menu">
          <button
            v-for="item in menuItems"
            :key="item.id"
            type="button"
            class="nav-item"
            :class="{ active: currentSection === item.id }"
            @click="switchSection(item.id)"
          >
            {{ item.label }}
          </button>
        </nav>
        <div class="sidebar-footer">
          <span class="version">v1.0.0</span>
        </div>
      </aside>

      <main class="content">
        <header class="page-head">
          <div class="title-group">
            <h2 class="page-title">{{ currentMenuItem?.label }}</h2>
            <p class="page-subtitle">{{ currentMenuItem?.desc }}</p>
          </div>
          <span class="status-pill" :class="{ online: isLoggedIn && !checkingAuth }">
            {{ checkingAuth ? "检测中..." : isLoggedIn ? "已登录" : "未登录" }}
          </span>
        </header>

        <section v-if="checkingAuth" class="card empty-card">
          <div class="empty-state">
            <div class="spinner"></div>
            <p>正在检测登录状态...</p>
          </div>
        </section>

        <section v-else-if="!isLoggedIn" class="card login-card">
          <div class="card-header">
            <h3 class="card-title">欢迎回来</h3>
            <p class="card-desc">
              请先登录后再进行系统设置<br />
              <span class="hint">默认账号密码：<code>doover / doover</code></span>
            </p>
          </div>

          <form class="form-grid" @submit.prevent="handleLogin">
            <div class="row">
              <label class="field">
                <span class="field-label">账号</span>
                <input
                  v-model.trim="loginForm.username"
                  class="text-input"
                  type="text"
                  autocomplete="username"
                  placeholder="请输入账号"
                  required
                />
              </label>
              <label class="field">
                <span class="field-label">密码</span>
                <input
                  v-model.trim="loginForm.password"
                  class="text-input"
                  type="password"
                  autocomplete="current-password"
                  placeholder="请输入密码"
                  required
                />
              </label>
            </div>
            <div class="form-actions">
              <button class="primary-btn" type="submit" :disabled="loginLoading">
                {{ loginLoading ? "登录中..." : "立即登录" }}
              </button>
            </div>
          </form>
        </section>

        <template v-else>
          <transition name="fade-slide" mode="out-in">
            <div v-if="currentSection === 'llm-active'" key="llm-active" class="panel">
              <div class="card">
                <form class="form-grid" @submit.prevent="handleUpdateLlm">
                  <div class="row">
                    <label class="field">
                      <span class="field-label">Provider</span>
                      <div
                        class="custom-select"
                        :class="{ open: activeDropdown === 'active-provider', disabled: !providerNames.length }"
                      >
                        <button
                          type="button"
                          class="text-input select-trigger"
                          :disabled="!providerNames.length"
                          @click="toggleDropdown('active-provider')"
                        >
                          <span>{{ selectedProvider || "请选择 Provider" }}</span>
                        </button>
                        <div v-if="activeDropdown === 'active-provider'" class="select-menu">
                          <button
                            v-for="name in providerNames"
                            :key="name"
                            type="button"
                            class="select-option"
                            :class="{ selected: selectedProvider === name }"
                            @click="chooseProvider(name)"
                          >
                            {{ name }}
                          </button>
                        </div>
                      </div>
                    </label>
                    <label class="field">
                      <span class="field-label">Model</span>
                      <div
                        class="custom-select"
                        :class="{ open: activeDropdown === 'active-model', disabled: !modelNames.length }"
                      >
                        <button
                          type="button"
                          class="text-input select-trigger"
                          :disabled="!modelNames.length"
                          @click="toggleDropdown('active-model')"
                        >
                          <span>{{ selectedModel || "请选择 Model" }}</span>
                        </button>
                        <div v-if="activeDropdown === 'active-model'" class="select-menu">
                          <button
                            v-for="name in modelNames"
                            :key="name"
                            type="button"
                            class="select-option"
                            :class="{ selected: selectedModel === name }"
                            @click="chooseModel(name)"
                          >
                            {{ name }}
                          </button>
                        </div>
                      </div>
                    </label>
                  </div>
                  <div class="form-actions">
                    <button class="primary-btn" type="submit" :disabled="llmSaving || !canSubmitLlm">
                      {{ llmSaving ? "保存中..." : "保存设置" }}
                    </button>
                    <button class="ghost-btn" type="button" :disabled="llmLoading" @click="loadLlmConfig">
                      刷新配置
                    </button>
                  </div>
                </form>
              </div>
            </div>

            <div v-else-if="currentSection === 'llm-providers'" key="llm-providers" class="panel">
              <div class="card">
                <div class="provider-console">
                  <aside class="provider-rail">
                    <div class="provider-rail-head">
                      <span class="field-label">Providers</span>
                      <button
                        type="button"
                        class="provider-add-btn"
                        @click="toggleNewProviderTypePicker"
                      >
                        + 新增
                      </button>
                    </div>

                    <div v-if="showNewProviderTypePicker" class="provider-type-panel">
                      <span class="provider-type-title">选择 Provider 类型</span>
                      <button
                        v-for="option in providerTypeOptions"
                        :key="option.value"
                        type="button"
                        class="provider-type-option"
                        @click="startCreateProvider(option.value)"
                      >
                        {{ option.label }}
                      </button>
                    </div>

                    <div class="provider-list">
                      <div
                        v-for="name in providerNames"
                        :key="name"
                        class="provider-list-row"
                        :class="{ active: !isCreatingProvider && providerForm.provider === name }"
                      >
                        <button
                          type="button"
                          class="provider-list-item"
                          :class="{ active: !isCreatingProvider && providerForm.provider === name }"
                          @click="selectManagedProvider(name)"
                        >
                          <span>{{ name }}</span>
                          <small>{{ providers[name]?.type || "openai" }}</small>
                        </button>
                        <button
                          v-if="name !== activeProviderName"
                          type="button"
                          class="provider-delete-btn"
                          :disabled="providerDeletingName === name"
                          @click.stop="handleDeleteProvider(name)"
                        >
                          <span class="sr-only">删除 {{ name }}</span>
                          <svg viewBox="0 0 24 24" aria-hidden="true">
                            <path
                              d="M9 3h6l1 2h4v2H4V5h4l1-2Zm1 7h2v7h-2v-7Zm4 0h2v7h-2v-7ZM7 10h2v7H7v-7Zm1 10h8a2 2 0 0 0 2-2V8H6v10a2 2 0 0 0 2 2Z"
                            />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </aside>

                  <section class="provider-detail">
                    <div class="provider-config-panel">
                      <div class="provider-section-head">
                        <div>
                          <span class="field-label">Provider Config</span>
                          <h4 class="provider-section-title">
                            {{ isCreatingProvider ? "新增 Provider" : providerForm.provider || "请选择 Provider" }}
                          </h4>
                        </div>
                        <span class="provider-type-pill">{{ selectedProviderTypeLabel }}</span>
                      </div>

                      <div class="row">
                        <label class="field">
                          <span class="field-label">Provider 名称</span>
                          <input
                            v-model.trim="providerForm.provider"
                            class="text-input"
                            type="text"
                            :disabled="!isCreatingProvider"
                            placeholder="例如：openai"
                            required
                          />
                        </label>
                        <label class="field">
                          <span class="field-label">API 类型</span>
                          <input
                            class="text-input"
                            type="text"
                            :value="selectedProviderTypeLabel"
                            disabled
                          />
                        </label>
                      </div>

                      <label class="field">
                        <span class="field-label">Base URL</span>
                        <input
                          v-model.trim="providerForm.baseUrl"
                          class="text-input"
                          type="url"
                          placeholder="https://api.example.com/v1"
                          required
                        />
                      </label>

                      <label class="field">
                        <span class="field-label">API Key</span>
                        <input
                          v-model.trim="providerForm.apiKey"
                          class="text-input"
                          type="password"
                          :placeholder="isCreatingProvider ? 'sk-...' : '留空则不修改'"
                          :required="isCreatingProvider"
                        />
                      </label>

                      <div class="form-actions compact">
                        <button
                          v-if="!isCreatingProvider"
                          class="ghost-btn"
                          type="button"
                          :disabled="providerSaving || !canSaveProviderConfig"
                          @click="handleSaveProviderConfig"
                        >
                          {{ providerSaving ? "保存中..." : "保存平台信息" }}
                        </button>
                      </div>
                    </div>

                    <div class="provider-model-panel">
                      <div class="provider-section-head">
                        <div>
                          <span class="field-label">Models</span>
                          <h4 class="provider-section-title">模型列表</h4>
                        </div>
                        <span v-if="providerModelOptions.length" class="field-hint">
                          待新增 {{ pendingProviderModelAdds.length }} 个，待删除 {{ pendingProviderModelDeletes.length }} 个
                        </span>
                      </div>

                      <div class="provider-models-box" :class="{ empty: !providerModelOptions.length }">
                        <div v-if="providerModelOptions.length" class="provider-models-list">
                          <label
                            v-for="option in providerModelOptions"
                            :key="option.name"
                            class="provider-model-row"
                            :class="{ locked: isProviderModelActive(option.name) }"
                          >
                            <span class="provider-model-name">
                              {{ option.name }}
                              <span v-if="option.existing" class="provider-model-badge">已加入</span>
                              <span v-if="isProviderModelActive(option.name)" class="provider-model-badge active">使用中</span>
                            </span>
                            <span class="provider-model-switch">
                            <input
                              v-model="option.enabled"
                              type="checkbox"
                              class="provider-model-checkbox"
                              :disabled="isProviderModelActive(option.name)"
                            />
                            <span class="provider-model-slider"></span>
                            </span>
                          </label>
                        </div>
                        <p v-else class="provider-models-placeholder">
                          {{ isCreatingProvider ? "填写平台信息后获取模型列表" : "请选择 Provider，然后获取模型列表" }}
                        </p>
                      </div>

                      <div
                        v-if="isCreatingProvider && selectedProviderModels.length"
                        class="default-setting-card"
                      >
                        <div class="default-setting-copy">
                          <span class="field-label">默认 Provider</span>
                          <p class="default-setting-text">
                            添加后将 {{ pendingProviderName }} 设为默认 Provider
                          </p>
                        </div>
                        <label class="provider-model-switch default-setting-switch">
                          <input
                            v-model="providerForm.setActive"
                            type="checkbox"
                            class="provider-model-checkbox"
                          />
                          <span class="provider-model-slider"></span>
                        </label>
                      </div>

                      <div
                        v-if="!isCreatingProvider && pendingProviderModelAdds.length"
                        class="default-setting-card"
                        :class="{ disabled: !canSetManagedModelActive }"
                      >
                        <div class="default-setting-copy">
                          <span class="field-label">默认模型</span>
                          <p class="default-setting-text">
                            {{
                              canSetManagedModelActive
                                ? `保存后将 ${singleManagedAddedModelName} 设为默认模型`
                                : `当前勾选了 ${pendingProviderModelAdds.length} 个新增模型，如需设为默认请只保留一个`
                            }}
                          </p>
                        </div>
                        <label v-if="canSetManagedModelActive" class="provider-model-switch default-setting-switch">
                          <input
                            v-model="providerForm.setActive"
                            type="checkbox"
                            class="provider-model-checkbox"
                          />
                          <span class="provider-model-slider"></span>
                        </label>
                        <span v-else class="default-setting-note">仅单选可设默认</span>
                      </div>

                      <div class="provider-model-actions">
                        <button
                          class="ghost-btn"
                          type="button"
                          :disabled="providerModelsLoading || !canFetchManagedModels"
                          @click="handleFetchProviderModels"
                        >
                          {{
                            providerModelsLoading
                              ? "获取中..."
                              : providerModelOptions.length
                                ? "重新获取模型列表"
                                : "获取模型列表"
                          }}
                        </button>
                        <button
                          class="primary-btn"
                          type="button"
                          :disabled="providerSaving || !canSaveProviderModels"
                          @click="handleSaveProviderModels"
                        >
                          {{ providerSaving ? "保存中..." : isCreatingProvider ? "保存平台与模型" : "保存模型设置" }}
                        </button>
                      </div>
                    </div>
                  </section>
                </div>
              </div>
            </div>

            <div v-else-if="currentSection === 'account-security'" key="account-security" class="panel">
              <div class="card">
                <form class="form-grid" @submit.prevent="handleUpdateAccountSubmit">
                  <div class="row">
                    <label class="field">
                      <span class="field-label">新账号名</span>
                      <input v-model.trim="accountForm.username" class="text-input" type="text" required />
                    </label>
                    <label class="field">
                      <span class="field-label">新密码</span>
                      <input
                        v-model.trim="accountForm.password"
                        class="text-input"
                        type="password"
                        placeholder="留空则不修改"
                      />
                    </label>
                  </div>

                  <div class="alert-box warning" v-if="requirePasswordChange">
                    <span class="alert-icon">⚠️</span>
                    <span>出于安全考虑，请修改默认密码</span>
                  </div>

                  <div class="form-actions">
                    <button class="primary-btn" type="submit" :disabled="accountSaving">
                      {{ accountSaving ? "保存中..." : "更新账号" }}
                    </button>
                    <button class="danger-btn" type="button" @click="handleLogout">
                      退出登录
                    </button>
                  </div>
                </form>

              </div>
            </div>
          </transition>
        </template>
      </main>
    </div>

    <transition name="top-toast">
      <div v-if="llmToast.visible" class="top-toast-shell">
        <ErrorComponent
          v-if="llmToast.type === 'error'"
          class="top-error-card"
          :node="llmToast.node"
          :message="llmToast.text"
        />
        <div v-else class="top-toast-success">
          {{ llmToast.text }}
        </div>
      </div>
    </transition>

    <div v-if="isLoggedIn && requirePasswordChange" class="force-mask">
      <div class="force-card">
        <h3 class="force-title">安全提醒</h3>
        <p class="force-desc">检测到您仍在使用默认账号密码，请先修改以确保账户安全。</p>

        <form class="form-grid" @submit.prevent="handleForceUpdateAccount">
          <label class="field">
            <span class="field-label">新账号名</span>
            <input v-model.trim="accountForm.username" class="text-input" type="text" required />
          </label>
          <label class="field">
            <span class="field-label">设置新密码</span>
            <input v-model.trim="accountForm.password" class="text-input" type="password" required />
          </label>
          <div class="form-actions">
            <button class="primary-btn block" type="submit" :disabled="accountSaving">
              {{ accountSaving ? "保存中..." : "确认修改" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import ErrorComponent from "../components/ErrorComponent.vue";

const API_BASE_URL = "http://localhost:8000";

const props = defineProps<{
  routeAccount: string;
}>();

const menuItems = [
  {
    id: "llm-active",
    label: "模型配置",
    desc: "选择和管理当前使用的 AI 对话模型",
  },
  {
    id: "llm-providers",
    label: "平台与模型",
    desc: "接入并管理 LLM Provider、密钥和模型列表",
  },
  {
    id: "account-security",
    label: "账号安全",
    desc: "管理登录凭据和安全设置",
  },
] as const;

const currentSection = ref<(typeof menuItems)[number]["id"]>("llm-active");

const currentMenuItem = computed(() =>
  menuItems.find((item) => item.id === currentSection.value)
);

function switchSection(sectionId: string) {
  if (sectionId === currentSection.value) return;
  currentSection.value = sectionId as (typeof menuItems)[number]["id"];
  activeDropdown.value = "";
}

type AuthStateResponse = {
  ok: boolean;
  user_name: string;
  require_password_change: boolean;
};

type LlmProviderConfig = {
  type: string;
  base_url: string;
  models: string[];
};

type LlmConfigResponse = {
  active_provider: string;
  active_model: string;
  providers: Record<string, LlmProviderConfig>;
};

type DiscoverModelsResponse = {
  type: string;
  models: string[];
};

type DiscoverProviderModelsResponse = {
  provider: string;
  type: string;
  models: string[];
  configured_models: string[];
};

const checkingAuth = ref(true);
const isLoggedIn = ref(false);
const currentUser = ref("");
const requirePasswordChange = ref(false);

const loginLoading = ref(false);
const loginError = ref("");
const loginForm = ref({
  username: "",
  password: "",
});

const llmLoading = ref(false);
const llmSaving = ref(false);
const llmError = ref("");
const llmMessage = ref("");
const llmToast = ref<{
  visible: boolean;
  type: "error" | "success";
  text: string;
  node: string;
}>({
  visible: false,
  type: "success",
  text: "",
  node: "模型配置",
});
const providers = ref<Record<string, LlmProviderConfig>>({});
const activeProviderName = ref("");
const activeModelName = ref("");
const selectedProvider = ref("");
const selectedModel = ref("");
const activeDropdown = ref("");
let llmToastTimer: number | undefined;

const providerTypeOptions = [
  { value: "openai", label: "OpenAI 兼容" },
] as const;

const providerSaving = ref(false);
const providerDeletingName = ref("");
const providerModelsLoading = ref(false);
const providerError = ref("");
const providerMessage = ref("");
const providerModelOptions = ref<{ name: string; enabled: boolean; existing: boolean }[]>([]);
const isCreatingProvider = ref(false);
const showNewProviderTypePicker = ref(false);
const providerForm = ref({
  provider: "",
  type: "openai",
  baseUrl: "",
  apiKey: "",
  setActive: false,
});

const accountSaving = ref(false);
const accountError = ref("");
const accountMessage = ref("");
const accountForm = ref({
  username: "",
  password: "",
});

const providerNames = computed(() => Object.keys(providers.value));
const modelNames = computed(() => {
  if (!selectedProvider.value) return [];
  return providers.value[selectedProvider.value]?.models ?? [];
});
const canSubmitLlm = computed(() => Boolean(selectedProvider.value && selectedModel.value));
const canFetchProviderModels = computed(() =>
  Boolean(
    providerForm.value.type &&
      providerForm.value.baseUrl.trim() &&
      providerForm.value.apiKey.trim()
  )
);
const canSubmitProvider = computed(() =>
  Boolean(
    providerForm.value.provider.trim() &&
      providerForm.value.baseUrl.trim() &&
      providerForm.value.apiKey.trim() &&
      selectedProviderModels.value.length
  )
);
const selectedProviderModels = computed(() =>
  providerModelOptions.value
    .filter((item) => item.enabled)
    .map((item) => item.name)
);
const pendingProviderName = computed(() => providerForm.value.provider.trim() || "该平台");
const pendingProviderModelAdds = computed(() =>
  providerModelOptions.value
    .filter((item) => item.enabled && !item.existing)
    .map((item) => item.name)
);
const pendingProviderModelDeletes = computed(() =>
  providerModelOptions.value
    .filter((item) => item.existing && !item.enabled)
    .map((item) => item.name)
);
const canFetchManagedModels = computed(() =>
  isCreatingProvider.value
    ? Boolean(
        providerForm.value.type &&
          providerForm.value.baseUrl.trim() &&
          providerForm.value.apiKey.trim()
      )
    : Boolean(providerForm.value.provider)
);
const canSaveProviderConfig = computed(() =>
  Boolean(!isCreatingProvider.value && providerForm.value.provider && providerForm.value.baseUrl.trim())
);
const canSaveProviderModels = computed(() =>
  isCreatingProvider.value
    ? canSubmitProvider.value
    : Boolean(providerForm.value.provider && (pendingProviderModelAdds.value.length || pendingProviderModelDeletes.value.length))
);
const canSetManagedModelActive = computed(() => pendingProviderModelAdds.value.length === 1);
const singleManagedAddedModelName = computed(() =>
  canSetManagedModelActive.value ? pendingProviderModelAdds.value[0] : ""
);
const selectedProviderTypeLabel = computed(() => {
  return (
    providerTypeOptions.find((item) => item.value === providerForm.value.type)?.label ??
    providerTypeOptions[0].label
  );
});

function setRouteAccount(account: string) {
  const normalized = encodeURIComponent(account);
  const nextPath = `/${normalized}`;
  if (window.location.pathname === nextPath) return;
  window.history.replaceState({}, "", nextPath);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

function toggleDropdown(name: string) {
  activeDropdown.value = activeDropdown.value === name ? "" : name;
}

function closeDropdown() {
  activeDropdown.value = "";
}

function chooseProvider(name: string) {
  selectedProvider.value = name;
  closeDropdown();
}

function chooseModel(name: string) {
  selectedModel.value = name;
  closeDropdown();
}

function toggleNewProviderTypePicker() {
  showNewProviderTypePicker.value = !showNewProviderTypePicker.value;
}

function resetProviderEditor() {
  providerForm.value.provider = "";
  providerForm.value.type = "openai";
  providerForm.value.baseUrl = "";
  providerForm.value.apiKey = "";
  providerForm.value.setActive = false;
  providerModelOptions.value = [];
}

function startCreateProvider(type: string) {
  isCreatingProvider.value = true;
  showNewProviderTypePicker.value = false;
  resetProviderEditor();
  providerForm.value.type = type;
}

function selectManagedProvider(name: string) {
  const config = providers.value[name];
  if (!config) return;
  isCreatingProvider.value = false;
  showNewProviderTypePicker.value = false;
  providerForm.value.provider = name;
  providerForm.value.type = config.type || "openai";
  providerForm.value.baseUrl = config.base_url || "";
  providerForm.value.apiKey = "";
  providerForm.value.setActive = false;
  providerModelOptions.value = (config.models ?? []).map((model) => ({
    name: model,
    enabled: true,
    existing: true,
  }));
}

function isProviderModelActive(name: string) {
  return providerForm.value.provider === activeProviderName.value && name === activeModelName.value;
}

function handleDocumentPointerDown(event: Event) {
  const target = event.target as HTMLElement | null;
  if (target?.closest(".custom-select")) return;
  closeDropdown();
}

function showLlmToast(message: string, type: "error" | "success", node = "模型配置") {
  if (!message) return;
  llmToast.value = {
    visible: true,
    type,
    text: message,
    node,
  };
  if (llmToastTimer) {
    window.clearTimeout(llmToastTimer);
  }
  llmToastTimer = window.setTimeout(() => {
    llmToast.value.visible = false;
    llmToastTimer = undefined;
  }, 3000);
}

function resetTransientMessages() {
  llmError.value = "";
  llmMessage.value = "";
  providerError.value = "";
  providerMessage.value = "";
  accountError.value = "";
  accountMessage.value = "";
}

function clearAuthState() {
  isLoggedIn.value = false;
  currentUser.value = "";
  requirePasswordChange.value = false;
  providers.value = {};
  activeProviderName.value = "";
  activeModelName.value = "";
  selectedProvider.value = "";
  selectedModel.value = "";
  isCreatingProvider.value = false;
  showNewProviderTypePicker.value = false;
  providerModelOptions.value = [];
  resetProviderEditor();
  closeDropdown();
  resetTransientMessages();
}

watch(
  () => props.routeAccount,
  (value) => {
    if (!isLoggedIn.value || !value) return;
    if (currentUser.value && currentUser.value !== value) {
      setRouteAccount(currentUser.value);
    }
  }
);

watch(selectedProvider, (provider) => {
  if (!provider) {
    selectedModel.value = "";
    return;
  }
  const models = providers.value[provider]?.models ?? [];
  if (!models.includes(selectedModel.value)) {
    selectedModel.value = models[0] ?? "";
  }
});

watch(
  () => [providerForm.value.type, providerForm.value.baseUrl, providerForm.value.apiKey],
  () => {
    if (isCreatingProvider.value) {
      providerModelOptions.value = [];
    }
  }
);

watch(pendingProviderModelAdds, (models) => {
  if (!isCreatingProvider.value && models.length !== 1) {
    providerForm.value.setActive = false;
  }
});

watch(llmError, (message) => {
  if (!message) return;
  showLlmToast(message, "error", "模型配置");
});

watch(llmMessage, (message) => {
  if (!message) return;
  showLlmToast(message, "success", "模型配置");
});

watch(providerError, (message) => {
  if (!message) return;
  showLlmToast(message, "error", "接入平台");
});

watch(providerMessage, (message) => {
  if (!message) return;
  showLlmToast(message, "success", "接入平台");
});

watch(accountError, (message) => {
  if (!message) return;
  showLlmToast(message, "error", "账号设置");
});

watch(accountMessage, (message) => {
  if (!message) return;
  showLlmToast(message, "success", "账号设置");
});

watch(loginError, (message) => {
  if (!message) return;
  showLlmToast(message, "error", "登录");
});

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    const detail = body?.detail;
    if (typeof detail === "string" && detail.trim()) return detail;
  } catch {
    // ignore
  }
  return `请求失败：${response.status}`;
}

async function requestJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers ?? {});
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response));
  }
  return (await response.json()) as T;
}

function applyLlmConfig(data: LlmConfigResponse) {
  providers.value = data.providers ?? {};
  activeProviderName.value = data.active_provider || "";
  activeModelName.value = data.active_model || "";
  const all = Object.keys(providers.value);
  const fallbackProvider = all[0] ?? "";
  selectedProvider.value = data.active_provider || fallbackProvider;

  const models = providers.value[selectedProvider.value]?.models ?? [];
  selectedModel.value = models.includes(data.active_model)
    ? data.active_model
    : (models[0] ?? "");

  if (!providerForm.value.provider && selectedProvider.value) {
    selectManagedProvider(selectedProvider.value);
  } else if (!isCreatingProvider.value && providerForm.value.provider) {
    const config = providers.value[providerForm.value.provider];
    if (config) {
      providerForm.value.type = config.type || "openai";
      providerForm.value.baseUrl = config.base_url || "";
    }
  }
}

async function loadLlmConfig() {
  llmLoading.value = true;
  llmError.value = "";
  llmMessage.value = "";
  try {
    const data = await requestJson<LlmConfigResponse>("/llm_config");
    applyLlmConfig(data);
  } catch (error: unknown) {
    llmError.value = error instanceof Error ? error.message : "加载 LLM 配置失败";
  } finally {
    llmLoading.value = false;
  }
}

async function checkLoginStatus() {
  checkingAuth.value = true;
  loginError.value = "";
  try {
    const me = await requestJson<AuthStateResponse>("/auth/me");
    isLoggedIn.value = true;
    currentUser.value = me.user_name;
    requirePasswordChange.value = Boolean(me.require_password_change);
    accountForm.value.username = me.user_name;
    accountForm.value.password = "";
    if (props.routeAccount !== me.user_name) {
      setRouteAccount(me.user_name);
    }
    await loadLlmConfig();
  } catch {
    clearAuthState();
  } finally {
    checkingAuth.value = false;
  }
}

async function handleLogin() {
  loginError.value = "";
  loginLoading.value = true;
  try {
    const result = await requestJson<AuthStateResponse>("/login", {
      method: "POST",
      body: JSON.stringify({
        username: loginForm.value.username,
        password: loginForm.value.password,
      }),
    });
    isLoggedIn.value = true;
    currentUser.value = result.user_name;
    requirePasswordChange.value = Boolean(result.require_password_change);
    accountForm.value.username = result.user_name;
    accountForm.value.password = "";
    setRouteAccount(result.user_name);
    await loadLlmConfig();
  } catch (error: unknown) {
    loginError.value = error instanceof Error ? error.message : "登录失败";
  } finally {
    loginLoading.value = false;
  }
}

async function handleLogout() {
  try {
    await requestJson<{ ok: boolean }>("/logout", { method: "POST" });
  } catch {
    // ignore
  } finally {
    clearAuthState();
  }
}

async function handleUpdateLlm() {
  if (!selectedProvider.value || !selectedModel.value) return;
  llmSaving.value = true;
  llmError.value = "";
  llmMessage.value = "";
  try {
    await requestJson<{ provider: string; model: string }>("/update_llm", {
      method: "PUT",
      body: JSON.stringify({
        provider: selectedProvider.value,
        model: selectedModel.value,
      }),
    });
    llmMessage.value = "默认模型配置已更新";
  } catch (error: unknown) {
    llmError.value = error instanceof Error ? error.message : "更新默认模型失败";
  } finally {
    llmSaving.value = false;
  }
}

async function handleFetchProviderModels() {
  providerError.value = "";
  providerMessage.value = "";

  providerModelsLoading.value = true;
  try {
    if (isCreatingProvider.value) {
      if (!canFetchProviderModels.value) {
        providerError.value = "请先填写 API 类型、Base URL 和 API Key";
        return;
      }

      const data = await requestJson<DiscoverModelsResponse>("/discover_llm_models", {
        method: "POST",
        body: JSON.stringify({
          type: providerForm.value.type,
          base_url: providerForm.value.baseUrl,
          api_key: providerForm.value.apiKey,
        }),
      });
      providerModelOptions.value = data.models.map((name) => ({
        name,
        enabled: false,
        existing: false,
      }));
      providerMessage.value = `已获取 ${data.models.length} 个模型`;
      return;
    }

    if (!providerForm.value.provider) {
      providerError.value = "请先选择 Provider";
      return;
    }

    const data = await requestJson<DiscoverProviderModelsResponse>("/discover_provider_models", {
      method: "POST",
      body: JSON.stringify({
        provider: providerForm.value.provider,
      }),
    });

    const configured = new Set(data.configured_models);
    const mergedModels = [...data.models];
    for (const name of data.configured_models) {
      if (!mergedModels.includes(name)) {
        mergedModels.push(name);
      }
    }

    providerModelOptions.value = mergedModels.map((name) => ({
      name,
      enabled: configured.has(name),
      existing: configured.has(name),
    }));
    providerMessage.value = `已获取 ${mergedModels.length} 个模型`;
  } catch (error: unknown) {
    providerModelOptions.value = [];
    providerError.value = error instanceof Error ? error.message : "获取模型列表失败";
  } finally {
    providerModelsLoading.value = false;
  }
}

async function handleSaveProviderConfig() {
  providerError.value = "";
  providerMessage.value = "";

  if (isCreatingProvider.value || !providerForm.value.provider) {
    providerError.value = "请先选择已有 Provider";
    return;
  }

  providerSaving.value = true;
  try {
    await requestJson<{ provider: string }>("/update_llm_provider", {
      method: "PUT",
      body: JSON.stringify({
        provider: providerForm.value.provider,
        base_url: providerForm.value.baseUrl,
        api_key: providerForm.value.apiKey,
      }),
    });
    providerMessage.value = "平台信息已保存";
    await loadLlmConfig();
  } catch (error: unknown) {
    providerError.value = error instanceof Error ? error.message : "保存平台信息失败";
  } finally {
    providerSaving.value = false;
  }
}

async function handleDeleteProvider(name: string) {
  if (!name || name === activeProviderName.value || providerDeletingName.value) return;

  providerError.value = "";
  providerMessage.value = "";
  providerDeletingName.value = name;

  try {
    if (providerForm.value.provider === name) {
      isCreatingProvider.value = false;
      resetProviderEditor();
    }

    await requestJson<{ provider: string }>("/delete_llm_provider", {
      method: "DELETE",
      body: JSON.stringify({
        provider: name,
      }),
    });

    providerMessage.value = "Provider 已删除";
    await loadLlmConfig();
  } catch (error: unknown) {
    providerError.value = error instanceof Error ? error.message : "删除 Provider 失败";
  } finally {
    providerDeletingName.value = "";
  }
}

async function handleSaveProviderModels() {
  providerError.value = "";
  providerMessage.value = "";

  if (isCreatingProvider.value) {
    const models = selectedProviderModels.value.slice();
    if (!models.length) {
      providerError.value = "请先开启至少一个模型";
      return;
    }

    providerSaving.value = true;
    try {
      await requestJson<{ provider: string; model: string }>("/add_llm_provider", {
        method: "PUT",
        body: JSON.stringify({
          provider: providerForm.value.provider,
          type: providerForm.value.type || "openai",
          base_url: providerForm.value.baseUrl,
          api_key: providerForm.value.apiKey,
          models,
          set_active: providerForm.value.setActive,
        }),
      });
      providerMessage.value = "Provider 已新增";
      isCreatingProvider.value = false;
      showNewProviderTypePicker.value = false;
      await loadLlmConfig();
      if (providerForm.value.provider) {
        selectManagedProvider(providerForm.value.provider);
      }
    } catch (error: unknown) {
      providerError.value = error instanceof Error ? error.message : "新增 Provider 失败";
    } finally {
      providerSaving.value = false;
    }
    return;
  }

  if (!providerForm.value.provider) {
    providerError.value = "请先选择 Provider";
    return;
  }

  const modelsToAdd = pendingProviderModelAdds.value.slice();
  const modelsToDelete = pendingProviderModelDeletes.value.slice();
  if (!modelsToAdd.length && !modelsToDelete.length) {
    providerError.value = "当前没有需要保存的模型变更";
    return;
  }

  if (providerForm.value.setActive && modelsToAdd.length > 1) {
    providerError.value = "设为默认模型时只能勾选一个新增模型";
    return;
  }

  providerSaving.value = true;
  try {
    for (const [index, model] of modelsToAdd.entries()) {
      await requestJson<{ provider: string; model: string }>("/add_llm_model", {
        method: "PUT",
        body: JSON.stringify({
          provider: providerForm.value.provider,
          model,
          set_active: providerForm.value.setActive && index === 0,
        }),
      });
    }

    for (const model of modelsToDelete) {
      await requestJson<{ provider: string; deleted_model: string }>("/delete_llm_model", {
        method: "DELETE",
        body: JSON.stringify({
          provider: providerForm.value.provider,
          model,
        }),
      });
    }

    const summary: string[] = [];
    if (modelsToAdd.length) summary.push(`新增 ${modelsToAdd.length} 个`);
    if (modelsToDelete.length) summary.push(`删除 ${modelsToDelete.length} 个`);
    providerMessage.value = `模型设置已保存：${summary.join("，")}`;
    providerForm.value.setActive = false;
    await loadLlmConfig();
    await handleFetchProviderModels();
  } catch (error: unknown) {
    providerError.value = error instanceof Error ? error.message : "保存模型设置失败";
  } finally {
    providerSaving.value = false;
  }
}

function handleUpdateAccountSubmit() {
  void handleUpdateAccount(false);
}

function handleForceUpdateAccount() {
  void handleUpdateAccount(true);
}

async function handleUpdateAccount(forceMode = false) {
  accountError.value = "";
  accountMessage.value = "";

  if (!accountForm.value.username || !accountForm.value.password) {
    accountError.value = "账号和密码都不能为空";
    return;
  }

  accountSaving.value = true;
  try {
    await requestJson<{ ok: boolean }>("/update_user", {
      method: "PUT",
      body: JSON.stringify({
        username: accountForm.value.username,
        password: accountForm.value.password,
      }),
    });
    accountMessage.value = forceMode ? "" : "账号密码已更新";
    currentUser.value = accountForm.value.username;
    requirePasswordChange.value = false;
    setRouteAccount(accountForm.value.username);
    accountForm.value.password = "";
  } catch (error: unknown) {
    accountError.value = error instanceof Error ? error.message : "更新账号密码失败";
  } finally {
    accountSaving.value = false;
  }
}

onMounted(() => {
  document.addEventListener("pointerdown", handleDocumentPointerDown);
  void checkLoginStatus();
});

onBeforeUnmount(() => {
  if (llmToastTimer) {
    window.clearTimeout(llmToastTimer);
  }
  document.removeEventListener("pointerdown", handleDocumentPointerDown);
});
</script>
<style scoped>
/* 基础设定 - 纯净的米纸背景 */
html, body {
  min-height: 100vh;
  background: #e8e6e1;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  color: #333330;
  line-height: 1.6;
}

.page-shell {
  position: relative;
  background: #fafaf7;
  width: min(95%, 1200px);
  margin: 40px auto;
  height: calc(100vh - 80px);
  border-radius: 3px;
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  display: grid;
  grid-template-columns: 220px 1fr;
}

/* 仅保留极淡的纸张纹理 */
.page-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.03;
  background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyBAMAAADsEZWCAAAAGFBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAn97UrAAAACHRSTlMA7v9f/v6+vnY9yG0AAAAJcEhZcwAADsQAAA7EAZUrDhsAAAA6SURBVDjLY2AYBaNgFIyCUTCqAB0InBfIeYfAmQfBqQfB6QfB6QfBeYfA6QfB6QfBeYfAGXUAgzMAABy3D9K697Y4AAAAAElFTkSuQmCC");
  z-index: 1;
}

/* 侧边栏 - 无线框，仅靠背景色区分 */
.sidebar {
  position: relative;
  z-index: 10;
  padding: 40px 0;
  display: flex;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.015); /* 极淡的背景色替代边框 */
}

.sidebar-title {
  padding: 0 28px;
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 10px;
  font-weight: 600;
  color: #a8a8a0;
  text-transform: uppercase;
  letter-spacing: 2.5px;
  margin-bottom: 24px;
  /* 移除 border-bottom，改用字间距和颜色对比 */
}

.nav-menu {
  display: flex;
  flex-direction: column;
  padding: 0 16px;
  gap: 6px;
}

.nav-item {
  text-align: left;
  padding: 10px 16px;
  border: none;
  background: transparent;
  color: #7a7a70;
  font-size: 14px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
  letter-spacing: 0.3px;
}

.nav-item:hover {
  color: #4a4a45;
  background: rgba(0, 0, 0, 0.03);
}

/* 激活状态：用圆点替代竖线 */
.nav-item.active {
  color: #2c2c29;
  font-weight: 600;
  background: rgba(139, 115, 85, 0.08);
}

.nav-item.active::before {
  content: "•";
  position: absolute;
  left: 4px;
  top: 50%;
  transform: translateY(-50%);
  color: #8b7355;
  font-size: 20px;
  line-height: 1;
  opacity: 0.8;
}

.sidebar-footer {
  margin-top: auto;
  padding: 24px 28px;
  /* 移除 border-top */
}

.version {
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 11px;
  color: #b8b8b0;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.version::before {
  content: "";
  width: 4px;
  height: 4px;
  background: #9ca3af;
  border-radius: 50%;
}

/* 主内容区 */
.content {
  position: relative;
  z-index: 10;
  padding: 48px 56px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.1) transparent;
}

/* 页头 - 仅靠留白分隔，无线框 */
.page-head {
  margin-bottom: 48px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  /* 移除 border-bottom */
}

.title-group {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c2c29;
  margin: 0 0 8px 0;
  letter-spacing: -0.3px;
}

.page-subtitle {
  font-size: 14px;
  color: #8b8b80;
  margin: 0;
  font-weight: 400;
}

/* 状态标签 - 徽章风格，无线框 */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.04);
  color: #7a7a70;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  font-family: ui-monospace, SFMono-Regular, monospace;
  border: none; /* 确保无线框 */
}

.status-pill::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #d1d5db;
}

.status-pill.online {
  background: rgba(34, 197, 94, 0.08);
  color: #15803d;
}

.status-pill.online::before {
  background: #22c55e;
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
}

/* 卡片 - 纯留白分隔 */
.card {
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 0;
  box-shadow: none;
  margin-bottom: 56px; /* 用更大的间距替代线条 */
  position: relative;
}

/* 彻底移除卡片间分隔线 */
.card:not(:last-child)::after {
  display: none;
}

.card-header {
  margin-bottom: 28px;
  /* 移除 border-bottom */
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: #2c2c29;
  margin: 0 0 8px 0;
  letter-spacing: -0.2px;
}

/* 移除圆点装饰 */
.card-title::before {
  display: none;
}

.card-desc {
  font-size: 14px;
  color: #7a7a70;
  margin: 0;
  line-height: 1.5;
}

.card-desc .hint {
  display: inline-block;
  margin-top: 8px;
  font-size: 12px;
  color: #8b7355;
  background: rgba(139, 115, 85, 0.06);
  padding: 6px 12px;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, monospace;
  border: none;
}

.card-desc code {
  background: rgba(0, 0, 0, 0.04);
  padding: 3px 8px;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 13px;
  color: #5c5c56;
  border: none;
}

/* 表单布局 */
.row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
  margin-bottom: 24px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field-label {
  font-size: 12px;
  font-weight: 600;
  color: #6b6b60;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-family: ui-monospace, SFMono-Regular, monospace;
}

.field-hint {
  font-size: 12px;
  color: #aaa;
  margin-top: 4px;
  font-style: normal;
}

/* 输入框 - 极简底边，hover时显现 */
.text-input {
  width: 100%;
  padding: 12px 4px;
  border: none;
  border-radius: 0;
  font-size: 15px;
  color: #333330;
  background: transparent;
  transition: all 0.2s;
  box-sizing: border-box;
  font-family: inherit;
  /* 默认状态完全无线 */
  box-shadow: 0 1px 0 0 rgba(0, 0, 0, 0.06);
}

.text-input:hover {
  box-shadow: 0 1px 0 0 rgba(0, 0, 0, 0.15);
}

.text-input:focus {
  outline: none;
  box-shadow: 0 2px 0 0 #8b7355;
  background: rgba(139, 115, 85, 0.02);
}

/* 文本域 - 淡色背景区块替代边框 */
.textarea-input {
  min-height: 120px;
  resize: vertical;
  line-height: 1.6;
  padding: 16px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.025);
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 14px;
  border: none;
  box-shadow: none;
}

.textarea-input:hover {
  background: rgba(0, 0, 0, 0.035);
}

.textarea-input:focus {
  background: rgba(139, 115, 85, 0.04);
  box-shadow: 0 0 0 2px rgba(139, 115, 85, 0.1);
}

.provider-models-box {
  height: 240px;
  padding: 16px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.025);
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-gutter: stable;
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.22) transparent;
}

.provider-models-box.empty {
  display: flex;
  align-items: center;
}

.provider-models-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.row.single-column {
  grid-template-columns: 1fr;
  gap: 0;
}

.provider-console {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 28px;
  align-items: start;
}

.provider-rail {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.provider-rail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.provider-add-btn {
  border: none;
  border-radius: 999px;
  padding: 8px 14px;
  background: rgba(139, 115, 85, 0.1);
  color: #5c4b38;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.provider-add-btn:hover {
  background: rgba(139, 115, 85, 0.16);
  transform: translateY(-1px);
}

.provider-type-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.03);
}

.provider-type-title {
  color: #7a7a70;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.4px;
}

.provider-type-option {
  border: none;
  border-radius: 10px;
  padding: 11px 12px;
  background: rgba(139, 115, 85, 0.08);
  color: #4f4232;
  font-size: 14px;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.provider-type-option:hover {
  background: rgba(139, 115, 85, 0.14);
}

.provider-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: min(460px, calc(100vh - 320px));
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px;
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 115, 85, 0.35) transparent;
}

.provider-list::-webkit-scrollbar {
  width: 6px;
}

.provider-list::-webkit-scrollbar-track {
  background: transparent;
}

.provider-list::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgba(139, 115, 85, 0.28);
}

.provider-list-row {
  position: relative;
}

.provider-list-row:hover .provider-delete-btn,
.provider-list-row:focus-within .provider-delete-btn {
  opacity: 1;
  pointer-events: auto;
}

.provider-list-item {
  width: 100%;
  border: none;
  border-radius: 14px;
  padding: 14px 48px 14px 16px;
  background: rgba(0, 0, 0, 0.03);
  color: #4a4a45;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.provider-list-item:hover {
  background: rgba(139, 115, 85, 0.08);
  transform: translateY(-1px);
}

.provider-list-item.active {
  background: rgba(139, 115, 85, 0.14);
  color: #2c2c29;
}

.provider-list-item span {
  font-size: 15px;
  font-weight: 700;
}

.provider-list-item small {
  color: #8b8b80;
  font-size: 12px;
  letter-spacing: 0.3px;
}

.provider-delete-btn {
  position: absolute;
  top: 50%;
  right: 12px;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(201, 63, 63, 0.08);
  color: #c64a4a;
  cursor: pointer;
  transform: translateY(-50%);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.18s ease, background-color 0.18s ease, color 0.18s ease;
}

.provider-delete-btn:hover:not(:disabled) {
  background: rgba(201, 63, 63, 0.16);
  color: #a22929;
}

.provider-delete-btn:disabled {
  opacity: 0.55;
  cursor: wait;
}

.provider-delete-btn svg {
  width: 15px;
  height: 15px;
  fill: currentColor;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.provider-detail {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 22px;
  min-width: 0;
  min-height: 0;
}

.provider-config-panel,
.provider-model-panel {
  padding: 20px 22px;
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.025);
}

.provider-section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.provider-section-title {
  margin: 6px 0 0;
  color: #2c2c29;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.2px;
}

.provider-type-pill {
  flex-shrink: 0;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(139, 115, 85, 0.12);
  color: #6c563b;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.form-actions.compact {
  margin-top: 24px;
}

.provider-model-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(139, 115, 85, 0.06);
  cursor: pointer;
}

.provider-model-row.locked {
  background: rgba(0, 0, 0, 0.03);
}

.provider-model-name {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  color: #5c4b38;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

.provider-model-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.06);
  color: #7a7a70;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.4px;
}

.provider-model-badge.active {
  background: rgba(34, 197, 94, 0.12);
  color: #15803d;
}

.provider-model-switch {
  position: relative;
  display: inline-flex;
  width: 42px;
  height: 24px;
  flex-shrink: 0;
}

.provider-model-checkbox {
  position: absolute;
  inset: 0;
  margin: 0;
  opacity: 0;
  cursor: pointer;
}

.provider-model-slider {
  width: 100%;
  height: 100%;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.14);
  transition: background-color 0.2s ease;
  position: relative;
}

.provider-model-slider::after {
  content: "";
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #fafaf7;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.16);
  transition: transform 0.2s ease;
}

.provider-model-checkbox:checked + .provider-model-slider {
  background: #8b7355;
}

.provider-model-checkbox:checked + .provider-model-slider::after {
  transform: translateX(18px);
}

.provider-model-checkbox:focus-visible + .provider-model-slider {
  outline: 2px solid rgba(139, 115, 85, 0.25);
  outline-offset: 2px;
}

.provider-model-checkbox:disabled + .provider-model-slider {
  opacity: 0.72;
  cursor: not-allowed;
}

.default-setting-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin: 22px 0 8px;
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(139, 115, 85, 0.07);
}

.default-setting-card.disabled {
  background: rgba(0, 0, 0, 0.035);
}

.default-setting-copy {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.default-setting-text {
  margin: 0;
  color: #5c4b38;
  font-size: 14px;
  line-height: 1.6;
}

.default-setting-note {
  flex-shrink: 0;
  color: #8b8b80;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.default-setting-switch {
  flex-shrink: 0;
}

.provider-models-placeholder {
  margin: 0;
  color: #8b8b80;
  font-size: 14px;
  line-height: 1.6;
}

.provider-model-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  flex-wrap: wrap;
}

/* 自定义下拉 */
.custom-select {
  position: relative;
}

.custom-select.disabled .select-trigger {
  cursor: not-allowed;
  opacity: 0.5;
}

.select-trigger {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.02);
  box-shadow: 0 1px 0 0 rgba(0, 0, 0, 0.06);
}

.select-trigger::after {
  content: "";
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%238b7355' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: center;
  background-size: 16px;
  transition: transform 0.2s ease;
}

.custom-select.open .select-trigger::after {
  transform: rotate(180deg);
}

.select-trigger:focus-visible {
  outline: none;
  background-color: rgba(139, 115, 85, 0.06);
  box-shadow: 0 0 0 2px rgba(139, 115, 85, 0.15);
}

.select-trigger:disabled {
  pointer-events: none;
}

.select-menu {
  position: absolute;
  left: 0;
  right: 0;
  top: calc(100% + 8px);
  z-index: 40;
  max-height: 240px;
  overflow-y: auto;
  padding: 6px;
  border-radius: 8px;
  border: 1px solid rgba(139, 115, 85, 0.2);
  background: #fafaf7;
  box-shadow: 0 16px 28px -16px rgba(0, 0, 0, 0.5);
}

.select-option {
  width: 100%;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #333330;
  font-size: 15px;
  text-align: left;
  padding: 10px 12px;
  cursor: pointer;
  transition: background-color 0.18s ease;
}

.select-option:hover {
  background: rgba(0, 0, 0, 0.04);
}

.select-option.selected {
  background: rgba(139, 115, 85, 0.14);
  color: #2c2c29;
  font-weight: 600;
}

/* 复选框 - 极简 */
.checkbox-line {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 24px 0;
  font-size: 14px;
  color: #4a4a45;
  cursor: pointer;
  padding: 8px 0;
}

.checkbox-line input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #8b7355;
  cursor: pointer;
  border: none;
  border-radius: 4px;
  /* 移除默认边框，使用系统样式但淡化 */
}

/* 按钮区域 - 仅靠顶部留白 */
.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 40px;
  padding-top: 0; /* 移除 border-top 对应的 padding */
  border-top: none;
  align-items: center;
}

.primary-btn,
.ghost-btn,
.danger-btn {
  padding: 10px 24px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none; /* 移除边框 */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  letter-spacing: 0.3px;
  font-family: inherit;
  background: rgba(0, 0, 0, 0.06);
  color: #5c5c56;
}

.primary-btn:hover:not(:disabled) {
  background: #8b7355;
  color: #fff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px -2px rgba(139, 115, 85, 0.3);
}

.ghost-btn {
  background: transparent;
  color: #7a7a70;
}

.ghost-btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.04);
  color: #4a4a45;
}

.danger-btn {
  background: rgba(220, 38, 38, 0.06);
  color: #b91c1c;
  margin-left: auto;
}

.danger-btn:hover:not(:disabled) {
  background: #dc2626;
  color: white;
  box-shadow: 0 4px 12px -2px rgba(220, 38, 38, 0.25);
}

button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none !important;
}

button.block {
  width: 100%;
}

/* 消息提示 - 背景色块，无左边框 */
.error-text {
  color: #92400e;
  font-size: 14px;
  margin: 0;
  padding: 16px;
  background: rgba(251, 191, 36, 0.08);
  border-radius: 8px;
  border-left: none; /* 移除左边框 */
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 10px;
}

.error-text::before {
  content: "⚠";
  font-size: 16px;
  opacity: 0.7;
}

.success-text {
  color: #15803d;
  font-size: 14px;
  margin: 0;
  padding: 16px;
  background: rgba(34, 197, 94, 0.08);
  border-radius: 8px;
  border-left: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 10px;
}

.success-text::before {
  content: "✓";
  font-size: 18px;
  font-weight: 700;
  opacity: 0.8;
}

/* 顶部 Toast（LLM 设置反馈） */
.top-toast-shell {
  position: fixed;
  top: 22px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 220;
  width: min(92vw, 620px);
}

.top-toast-success {
  min-width: 260px;
  padding: 12px 18px;
  border-radius: 10px;
  box-shadow: 0 14px 28px -16px rgba(0, 0, 0, 0.45);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.45;
  backdrop-filter: blur(8px);
  background: rgba(21, 128, 61, 0.92);
  color: #f0fdf4;
}

:deep(.top-error-card.error-card) {
  width: 100%;
  transform: none;
}

.top-toast-enter-active,
.top-toast-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.top-toast-enter-from,
.top-toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -8px);
}

/* 警告框 - 淡琥珀背景 */
.alert-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  margin: 24px 0;
  font-size: 14px;
  background: rgba(251, 191, 36, 0.1);
  color: #854d0e;
  border: none;
  position: relative;
}

/* 移除左侧竖线 */
.alert-box::before {
  display: none;
}

.alert-icon {
  font-size: 18px;
  opacity: 0.8;
}

/* 加载状态 */
.empty-card {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.empty-state {
  text-align: center;
  color: #999;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 2px solid rgba(0, 0, 0, 0.05);
  border-top-color: #8b7355;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 强制弹窗 - 无线框版本 */
.force-mask {
  position: fixed;
  inset: 0;
  background: rgba(40, 38, 35, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 100;
}

.force-card {
  background: #fafaf7;
  border-radius: 12px;
  padding: 48px;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 24px 48px -12px rgba(0, 0, 0, 0.15);
  border: none; /* 移除边框 */
}

.force-card::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.02;
  background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyBAMAAADsEZWCAAAAGFBMVEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAn97UrAAAACHRSTlMA7v9f/v6+vnY9yG0AAAAJcEhZcwAADsQAAA7EAZUrDhsAAAA6SURBVDjLY2AYBaNgFIyCUTCqAB0InBfIeYfAmQfBqQfB6QfB6QfBeYfA6QfB6QfBeYfAGXUAgzMAABy3D9K697Y4AAAAAElFTkSuQmCC");
  border-radius: 12px;
}

.force-title {
  font-size: 24px;
  font-weight: 700;
  color: #2c2c29;
  margin: 0 0 12px 0;
  border-bottom: none; /* 移除底边 */
  padding-bottom: 0;
}

.force-desc {
  color: #7a7a70;
  margin-bottom: 32px;
  line-height: 1.6;
  font-size: 15px;
}

/* 过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 响应式 */
@media (max-width: 968px) {
  .page-shell {
    grid-template-columns: 1fr;
    margin: 20px auto;
    width: min(98%, 640px);
    height: calc(100vh - 40px);
  }
  
  .sidebar {
    background: transparent; /* 移动端也无线框 */
    border-bottom: none; /* 确保无下边线 */
    padding: 32px 24px;
  }
  
  .sidebar-title {
    margin-bottom: 16px;
  }
  
  .nav-menu {
    flex-direction: row;
    flex-wrap: wrap;
    padding: 0;
    gap: 8px;
  }
  
  .nav-item {
    margin: 0;
    white-space: nowrap;
    font-size: 14px;
    padding: 8px 14px;
    background: rgba(0, 0, 0, 0.03);
    border-radius: 20px;
  }
  
  .nav-item.active {
    background: rgba(139, 115, 85, 0.12);
  }
  
  .nav-item.active::before {
    display: none; /* 移动端无圆点 */
  }
  
  .sidebar-footer {
    display: none;
  }
  
  .content {
    padding: 32px 28px;
  }

  .provider-console {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .row {
    grid-template-columns: 1fr;
    gap: 8px; /* 更紧凑 */
  }
  
  .field {
    margin-bottom: 20px;
  }
}
</style>
