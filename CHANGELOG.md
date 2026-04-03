# Changelog | 变更日志

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] | 未发布

### Added | 新增
- Internationalization support (i18n) | 国际化支持
- Multi-language README (Chinese/English) | 多语言 README（中英文）
- CONTRIBUTING.md guide | 贡献指南
- CODE_OF_CONDUCT.md | 行为准则
- LICENSE file (AGPL-3.0) | 许可证文件

### Changed | 变更
- Enhanced project documentation | 增强项目文档

---

## [0.1.0] - 2025-01-15

### Added | 新增

#### Core Features | 核心功能
- **Life Background Modeling Engine**: Intelligent analysis of user life experiences | 人生背景建模引擎：智能分析用户人生经历
- **LangGraph State Orchestration**: Multi-turn conversation workflow | LangGraph 状态编排：多轮对话工作流
- **Real-time Streaming Output**: SSE-based streaming response | 实时流式输出：基于 SSE 的流式响应
- **Smart Information Completion**: Progressive background collection | 智能信息补全：渐进式背景收集

#### LLM Support | LLM 支持
- OpenAI GPT series support | OpenAI GPT 系列支持
- Kimi (Moonshot) integration with custom implementation | Kimi（Moonshot）集成与自定义实现
- StepFun API support | StepFun API 支持
- Flexible provider configuration system | 灵活的提供商配置系统

#### Tools | 工具
- Tavily search integration | Tavily 搜索集成
- Baidu Qianfan AI search support | 百度千帆 AI 搜索支持
- User interaction tool (ask_user) | 用户交互工具（ask_user）

#### Frontend | 前端
- Vue 3 + TypeScript dashboard | Vue 3 + TypeScript 仪表盘
- WebSocket real-time communication | WebSocket 实时通信
- Real-time analysis display | 实时分析显示
- Execution timeline visualization | 执行时间线可视化
- Search results feed | 搜索结果流

#### Infrastructure | 基础设施
- Loguru-based logging system | 基于 Loguru 的日志系统
- WebSocket server for real-time updates | 用于实时更新的 WebSocket 服务器
- IP-based geolocation | 基于 IP 的地理位置
- JSON configuration management | JSON 配置管理

### Technical Details | 技术细节

#### Graph Nodes | 图节点
- `init_world_params`: Initialize world parameters | 初始化世界参数
- `intake_node`: Receive user input | 接收用户输入
- `background_node`: Execute life background modeling | 执行人生背景建模
- `agent_node`: Information completion decision | 信息补全决策
- `tool_node`: Execute tool calls | 执行工具调用
- `wait_user_node`: Wait for user input | 等待用户输入

#### Prompt Engineering | Prompt 工程
- Life Background Modeling Prompt with fact/inference/unknown distinction | 人生背景建模 Prompt，区分事实/推断/未知
- Information Completion Decision Prompt | 信息补全决策 Prompt
- Structured output format | 结构化输出格式

---

## [0.0.1] - 2024-12-01

### Added | 新增
- Initial project structure | 初始项目结构
- Basic LangGraph integration | 基础 LangGraph 集成
- Simple LLM client | 简单 LLM 客户端
- Basic frontend scaffold | 基础前端脚手架

---

## Roadmap | 路线图

### [0.2.0] - Planned | 计划中

#### Added | 新增
- Multi-language support (English, Japanese, Korean) | 多语言支持（英语、日语、韩语）
- Emotion analysis dashboard | 情感分析仪表盘
- Life timeline visualization | 人生时间线可视化
- Export analysis reports (PDF/Markdown) | 导出分析报告（PDF/Markdown）
- User authentication system | 用户认证系统
- Session persistence | 会话持久化

#### Changed | 变更
- Improved prompt engineering | 改进 Prompt 工程
- Enhanced error handling | 增强错误处理
- Performance optimization | 性能优化

### [0.3.0] - Future | 未来

#### Added | 新增
- Anonymous story sharing | 匿名分享故事
- Community emotional support | 社区情感支持
- AI character customization | AI 角色定制
- Collaborative memoirs | 多人协作回忆录
- Voice input support | 语音输入支持

### [0.4.0] - Long-term | 远期

#### Added | 新增
- Psychological counselor interface | 心理咨询师接口
- Professional API | 专业版 API
- Enterprise deployment solutions | 企业版部署方案
- Mobile applications (iOS/Android) | 移动端应用（iOS/Android）
- Integration with mental health platforms | 与心理健康平台集成

---

## Version Naming Convention | 版本命名规范

- **Major (X.0.0)**: Breaking changes, major features | 重大变更、主要功能
- **Minor (0.X.0)**: New features, backward compatible | 新功能、向后兼容
- **Patch (0.0.X)**: Bug fixes, minor improvements | Bug 修复、小改进

---

## How to Read This Changelog | 如何阅读此变更日志

- **Added**: New features | 新功能
- **Changed**: Changes in existing functionality | 现有功能的变更
- **Deprecated**: Soon-to-be removed features | 即将移除的功能
- **Removed**: Removed features | 已移除的功能
- **Fixed**: Bug fixes | Bug 修复
- **Security**: Security-related changes | 安全相关变更

---

[Unreleased]: https://github.com/Radiant303/DoOver/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Radiant303/DoOver/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/Radiant303/DoOver/releases/tag/v0.0.1
