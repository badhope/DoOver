<div align="center">

# DoOver

### 致那个回不去的夏天，和那个没说出口的"如果"

**An emotionally aware LLM project for replaying missed moments, unresolved choices, and alternate futures.**

[![Version](https://img.shields.io/badge/version-v0.1.0-blue.svg)](https://github.com/Radiant303/DoOver)
[![License](https://img.shields.io/badge/license-AGPL--3.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/framework-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Vue](https://img.shields.io/badge/frontend-Vue%203-42b883.svg)](https://vuejs.org/)
[![GitHub Stars](https://img.shields.io/github/stars/Radiant303/DoOver?style=social)](https://github.com/Radiant303/DoOver/stargazers)

<img src="https://count.getloli.com/@DoOver?name=DoOver&theme=miku&padding=7&offset=0&align=center&scale=0.3&pixelated=1&darkmode=auto" alt="visitor count" />

</div>

---

## 🌧️ 你懂那种感觉吗？ | Do You Know That Feeling?

**[中文](#中文文档) | [English](#english-documentation)**

---

# 中文文档

## 📖 项目简介

DoOver 是一个基于 **LangGraph** 构建的情感化 AI 应用，旨在帮助用户回顾人生中那些"如果当时"的遗憾时刻。通过先进的大语言模型技术，DoOver 能够深入分析用户的人生经历，提供情感陪伴式的"人生背景建模"体验。

> **核心承诺**：我们不承诺改变过去，但我们承诺给你一个清晰的答案。让你知道，那条没走的路，或许并不如想象中美好；让你知道，现在的你，比任何时候都更懂得如何去爱。

### 🎯 核心特性

- **🧠 智能人生背景建模**：基于 LangGraph 状态图编排，实现多轮对话的深度分析
- **💬 流式实时输出**：完整的 SSE 流式响应处理，实时呈现分析过程
- **🔍 智能信息补全**：自动识别信息缺口，渐进式收集用户背景
- **🌐 多 LLM 支持**：灵活切换 OpenAI、Kimi、StepFun 等多种大模型
- **📊 可视化控制台**：Vue 3 构建的实时交互界面，WebSocket 双向通信
- **🔒 隐私优先**：本地部署，数据完全掌控

## 🌟 愿景与使命

### 我们的愿景

成为全球领先的 AI 情感陪伴平台，帮助每一个人：

- 📝 **书写人生回忆录**：用 AI 技术记录和分析人生重要时刻
- 🔮 **探索平行人生**：通过"如果"场景模拟，理解不同选择的可能性
- 💪 **获得情感治愈**：在 AI 的陪伴下，与过去的遗憾和解
- 🎓 **实现自我成长**：从过往经历中汲取智慧，更好地面对未来

### 我们的使命

> "让每一个遗憾都有回响，让每一次选择都有答案。"

DoOver 致力于：
1. **情感陪伴**：提供温暖、理解、不评判的 AI 陪伴体验
2. **认知重构**：帮助用户以新的视角看待过去的决定
3. **心理疗愈**：通过结构化分析，促进情感释放和自我接纳
4. **智慧传承**：将个人经历转化为可传承的人生智慧

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Dashboard (Vue 3 + Vite)                  │
│                    WebSocket 实时通信                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ WebSocket (ws://localhost:8765)
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Python + LangGraph)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Graph   │  │   LLM    │  │  Tools   │  │  Utils   │     │
│  │  Nodes   │  │ Provider │  │ Registry │  │  Logger  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Vue 3 + TypeScript + Vite | 响应式实时交互界面 |
| **后端框架** | LangGraph | 状态图编排引擎 |
| **LLM 框架** | LangChain Core | 大模型统一接口 |
| **LLM 提供商** | OpenAI / Kimi / StepFun | 多模型支持 |
| **搜索工具** | Tavily / 百度千帆 | 外部信息检索 |
| **通信协议** | WebSocket | 实时双向通信 |
| **日志系统** | Loguru | 结构化日志 |

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 pnpm

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/Radiant303/DoOver.git
cd DoOver

# 2. 配置 LLM 提供商
cp llm/config/provider.json.example llm/config/provider.json
# 编辑 provider.json 填入你的 API Key

# 3. 配置搜索工具
cp tools/config/tools.example tools/config/tools.json
# 编辑 tools.json 填入搜索 API Key

# 4. 安装后端依赖
pip install -r requirements.txt

# 5. 启动后端服务
python test.py

# 6. 启动前端（新终端）
cd dashboard
npm install
npm run dev
```

### 配置说明

#### LLM 配置 (`llm/config/provider.json`)

```json
{
  "active_llm_provider": "openai",
  "active_llm_model": "gpt-4",
  "llm_providers": {
    "openai": {
      "type": "openai",
      "base_url": "https://api.openai.com/v1",
      "api_key": "your-api-key",
      "models": ["gpt-4", "gpt-3.5-turbo"]
    },
    "moonshot": {
      "type": "moonshot",
      "base_url": "https://api.moonshot.cn/v1",
      "api_key": "your-kimi-api-key",
      "models": ["kimi-k2.5"]
    }
  }
}
```

#### 搜索工具配置 (`tools/config/tools.json`)

```json
{
  "search": {
    "active_search_provider": "tavily",
    "tavily": {
      "base_url": "https://api.tavily.com/search",
      "api_key": "your-tavily-api-key"
    }
  }
}
```

## 🗺️ 未来路线图

### v0.2.0 - 情感深化 (计划中)

- [ ] 多语言支持（英语、日语、韩语）
- [ ] 情感分析仪表盘
- [ ] 人生时间线可视化
- [ ] 导出分析报告（PDF/Markdown）

### v0.3.0 - 社交连接 (规划中)

- [ ] 匿名分享故事
- [ ] 社区情感支持
- [ ] AI 角色定制
- [ ] 多人协作回忆录

### v0.4.0 - 专业扩展 (远期)

- [ ] 心理咨询师接口
- [ ] 专业版 API
- [ ] 企业版部署方案
- [ ] 移动端应用

### 🔮 长期愿景

| 方向 | 描述 |
|------|------|
| **AI 心理健康** | 与专业心理机构合作，提供临床级别的情感支持 |
| **人生档案馆** | 构建个人数字遗产平台，永久保存人生故事 |
| **跨代对话** | AI 模拟与已故亲人的对话，实现情感延续 |
| **元宇宙集成** | 在虚拟世界中重现人生重要场景 |

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 贡献方式

- 🐛 提交 Bug 报告
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码 PR
- 🌍 翻译项目
- ⭐ 给项目点 Star

## 📄 许可证

本项目采用 [GNU Affero General Public License v3.0](LICENSE) 许可证。

这意味着：
- ✅ 你可以自由使用、修改和分发本软件
- ✅ 你必须以相同许可证分享你的修改
- ✅ 网络服务使用也需要开源代码

## 🙏 致谢

感谢以下开源项目：

- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - 状态图编排
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架

---

<div align="center">

**别让你的青春，只留在回忆里。**

打开 DoOver，给那个夏天的自己，写一封迟到的信。

[![Star History Chart](https://api.star-history.com/svg?repos=Radiant303/DoOver&type=Date)](https://www.star-history.com/chart?repos=Radiant303/DoOver)

</div>

---

# English Documentation

## 📖 Overview

DoOver is an emotionally-aware AI application built on **LangGraph**, designed to help users revisit those "what if" moments in life. Through advanced Large Language Model technology, DoOver provides deep analysis of life experiences with an emotionally supportive "Life Background Modeling" experience.

> **Our Promise**: We don't promise to change the past, but we promise to give you a clear answer. To help you understand that the road not taken might not be as beautiful as you imagined; to help you realize that who you are now knows better than ever how to love.

### 🎯 Key Features

- **🧠 Intelligent Life Background Modeling**: Deep multi-turn analysis based on LangGraph state orchestration
- **💬 Real-time Streaming Output**: Complete SSE streaming response processing
- **🔍 Smart Information Completion**: Automatically identify information gaps and progressively collect user background
- **🌐 Multi-LLM Support**: Flexible switching between OpenAI, Kimi, StepFun, and more
- **📊 Visual Console**: Real-time interactive interface built with Vue 3, WebSocket bidirectional communication
- **🔒 Privacy First**: Local deployment, complete data control

## 🌟 Vision & Mission

### Our Vision

To become the world's leading AI emotional companionship platform, helping everyone:

- 📝 **Write Life Memoirs**: Record and analyze important life moments with AI technology
- 🔮 **Explore Parallel Lives**: Understand possibilities of different choices through "what if" scenario simulation
- 💪 **Achieve Emotional Healing**: Reconcile with past regrets with AI companionship
- 🎓 **Achieve Self-Growth**: Draw wisdom from past experiences to better face the future

### Our Mission

> "Let every regret have an echo, let every choice have an answer."

DoOver is committed to:
1. **Emotional Companionship**: Providing warm, understanding, non-judgmental AI companionship
2. **Cognitive Restructuring**: Helping users view past decisions from new perspectives
3. **Psychological Healing**: Promoting emotional release and self-acceptance through structured analysis
4. **Wisdom Transmission**: Transforming personal experiences into inheritable life wisdom

## 🏗️ Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Dashboard (Vue 3 + Vite)                  │
│                    WebSocket Real-time Communication         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ WebSocket (ws://localhost:8765)
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Python + LangGraph)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Graph   │  │   LLM    │  │  Tools   │  │  Utils   │     │
│  │  Nodes   │  │ Provider │  │ Registry │  │  Logger  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology | Description |
|-------|------------|-------------|
| **Frontend** | Vue 3 + TypeScript + Vite | Responsive real-time interactive interface |
| **Backend Framework** | LangGraph | State graph orchestration engine |
| **LLM Framework** | LangChain Core | Unified LLM interface |
| **LLM Providers** | OpenAI / Kimi / StepFun | Multi-model support |
| **Search Tools** | Tavily / Baidu Qianfan | External information retrieval |
| **Communication** | WebSocket | Real-time bidirectional communication |
| **Logging** | Loguru | Structured logging |

## 🚀 Quick Start

### Requirements

- Python 3.10+
- Node.js 18+
- npm or pnpm

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Radiant303/DoOver.git
cd DoOver

# 2. Configure LLM provider
cp llm/config/provider.json.example llm/config/provider.json
# Edit provider.json and add your API Key

# 3. Configure search tools
cp tools/config/tools.example tools/config/tools.json
# Edit tools.json and add search API Key

# 4. Install backend dependencies
pip install -r requirements.txt

# 5. Start backend service
python test.py

# 6. Start frontend (new terminal)
cd dashboard
npm install
npm run dev
```

### Configuration

#### LLM Configuration (`llm/config/provider.json`)

```json
{
  "active_llm_provider": "openai",
  "active_llm_model": "gpt-4",
  "llm_providers": {
    "openai": {
      "type": "openai",
      "base_url": "https://api.openai.com/v1",
      "api_key": "your-api-key",
      "models": ["gpt-4", "gpt-3.5-turbo"]
    },
    "moonshot": {
      "type": "moonshot",
      "base_url": "https://api.moonshot.cn/v1",
      "api_key": "your-kimi-api-key",
      "models": ["kimi-k2.5"]
    }
  }
}
```

#### Search Tool Configuration (`tools/config/tools.json`)

```json
{
  "search": {
    "active_search_provider": "tavily",
    "tavily": {
      "base_url": "https://api.tavily.com/search",
      "api_key": "your-tavily-api-key"
    }
  }
}
```

## 🗺️ Roadmap

### v0.2.0 - Emotional Deepening (Planned)

- [ ] Multi-language support (English, Japanese, Korean)
- [ ] Emotion analysis dashboard
- [ ] Life timeline visualization
- [ ] Export analysis reports (PDF/Markdown)

### v0.3.0 - Social Connection (Planned)

- [ ] Anonymous story sharing
- [ ] Community emotional support
- [ ] AI character customization
- [ ] Collaborative memoirs

### v0.4.0 - Professional Extension (Long-term)

- [ ] Psychological counselor interface
- [ ] Professional API
- [ ] Enterprise deployment solutions
- [ ] Mobile applications

### 🔮 Long-term Vision

| Direction | Description |
|-----------|-------------|
| **AI Mental Health** | Partner with professional psychological institutions to provide clinical-level emotional support |
| **Life Archive** | Build a personal digital heritage platform to permanently preserve life stories |
| **Intergenerational Dialogue** | AI simulation of conversations with deceased loved ones for emotional continuity |
| **Metaverse Integration** | Recreate important life scenes in virtual worlds |

## 🤝 Contributing

We welcome all forms of contributions! Please check [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Ways to Contribute

- 🐛 Submit bug reports
- 💡 Propose new features
- 📝 Improve documentation
- 🔧 Submit code PRs
- 🌍 Translate the project
- ⭐ Star the project

## 📄 License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE).

This means:
- ✅ You can freely use, modify, and distribute this software
- ✅ You must share your modifications under the same license
- ✅ Network service usage also requires open-sourcing code

## 🙏 Acknowledgments

Thanks to the following open-source projects:

- [LangChain](https://github.com/langchain-ai/langchain) - LLM Application Framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - State Graph Orchestration
- [Vue.js](https://vuejs.org/) - Progressive JavaScript Framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python Web Framework

---

<div align="center">

**Don't let your youth stay only in memories.**

Open DoOver and write a late letter to yourself from that summer.

[![Star History Chart](https://api.star-history.com/svg?repos=Radiant303/DoOver&type=Date)](https://www.star-history.com/chart?repos=Radiant303/DoOver)

</div>
