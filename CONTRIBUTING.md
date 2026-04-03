# Contributing to DoOver | 贡献指南

[English](#english) | [中文](#中文)

---

# English

First off, thank you for considering contributing to DoOver! It's people like you that make DoOver such a great tool for emotional healing and self-reflection.

## 🌟 Ways to Contribute

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what you expected**
- **Include screenshots or animated GIFs if possible**
- **Include your environment details** (OS, Python version, Node version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and explain the expected behavior**
- **Explain why this enhancement would be useful**

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Include screenshots and animated GIFs in your pull request whenever possible
- Follow the code style guidelines
- Document new code based on the Documentation Styleguide
- End all files with a newline

## 🛠️ Development Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Git
- A code editor (VS Code recommended)

### Setting Up Your Development Environment

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/DoOver.git
cd DoOver

# 3. Add upstream remote
git remote add upstream https://github.com/Radiant303/DoOver.git

# 4. Create a branch for your changes
git checkout -b feature/your-feature-name

# 5. Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# 6. Install frontend dependencies
cd dashboard
npm install
```

### Running Tests

```bash
# Backend tests
pytest

# Frontend tests
cd dashboard
npm run test
```

### Code Style Guidelines

#### Python

- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Maximum line length: 100 characters

#### TypeScript/Vue

- Follow the Vue 3 Composition API style
- Use TypeScript for all new code
- Follow the ESLint configuration in the project

### Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

**Examples:**
```
feat(graph): add new node for emotion analysis
fix(llm): resolve streaming issue with Kimi provider
docs(readme): update installation instructions
```

## 📋 Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature or request |
| `documentation` | Improvements or additions to documentation |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention is needed |
| `priority: high` | High priority issue |
| `priority: low` | Low priority issue |

## 🤝 Community

- Be respectful and inclusive
- Welcome newcomers
- Focus on what is best for the community
- Show empathy towards other community members

---

# 中文

首先，感谢您考虑为 DoOver 做出贡献！正是像您这样的人让 DoOver 成为一个优秀的情感治愈和自我反思工具。

## 🌟 贡献方式

### 报告 Bug

在创建 bug 报告之前，请先检查 issue 列表，您可能会发现问题已经存在。创建 bug 报告时，请尽可能包含详细信息：

- **使用清晰、描述性的标题**
- **描述重现问题的确切步骤**
- **提供具体示例来演示步骤**
- **描述您观察到的行为和期望的行为**
- **如果可能，包含截图或动画 GIF**
- **包含您的环境详情**（操作系统、Python 版本、Node 版本等）

### 建议改进

改进建议作为 GitHub issues 跟踪。创建改进建议时，请包含：

- **使用清晰、描述性的标题**
- **提供逐步描述建议的改进**
- **提供具体示例来演示步骤**
- **描述当前行为并解释期望的行为**
- **解释为什么这个改进会有用**

### Pull Requests

- 填写所需的模板
- 不要在 PR 标题中包含 issue 编号
- 尽可能包含截图和动画 GIF
- 遵循代码风格指南
- 根据文档风格指南记录新代码
- 所有文件以换行符结束

## 🛠️ 开发环境设置

### 前置要求

- Python 3.10 或更高版本
- Node.js 18 或更高版本
- Git
- 代码编辑器（推荐 VS Code）

### 设置开发环境

```bash
# 1. 在 GitHub 上 fork 仓库

# 2. 克隆您的 fork
git clone https://github.com/YOUR_USERNAME/DoOver.git
cd DoOver

# 3. 添加上游远程仓库
git remote add upstream https://github.com/Radiant303/DoOver.git

# 4. 为您的更改创建分支
git checkout -b feature/your-feature-name

# 5. 安装 Python 依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果有

# 6. 安装前端依赖
cd dashboard
npm install
```

### 运行测试

```bash
# 后端测试
pytest

# 前端测试
cd dashboard
npm run test
```

### 代码风格指南

#### Python

- 遵循 PEP 8 风格指南
- 为函数参数和返回值使用类型提示
- 为所有公共函数和类编写文档字符串
- 最大行长度：100 字符

#### TypeScript/Vue

- 遵循 Vue 3 Composition API 风格
- 所有新代码使用 TypeScript
- 遵循项目中的 ESLint 配置

### 提交信息指南

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <description>

[可选的正文]

[可选的页脚]
```

**类型：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 仅文档更改
- `style`: 不影响代码含义的更改
- `refactor`: 既不修复 bug 也不添加功能的代码更改
- `perf`: 提高性能的代码更改
- `test`: 添加缺失的测试或更正现有测试
- `chore`: 构建过程或辅助工具的更改

**示例：**
```
feat(graph): 添加情感分析节点
fix(llm): 解决 Kimi 提供商的流式问题
docs(readme): 更新安装说明
```

## 📋 Issue 标签

| 标签 | 描述 |
|------|------|
| `bug` | 某些东西不工作 |
| `enhancement` | 新功能或请求 |
| `documentation` | 文档改进或添加 |
| `good first issue` | 适合新手 |
| `help wanted` | 需要额外关注 |
| `priority: high` | 高优先级问题 |
| `priority: low` | 低优先级问题 |

## 🤝 社区

- 尊重和包容
- 欢迎新人
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

---

## 📄 License

By contributing to DoOver, you agree that your contributions will be licensed under the AGPL-3.0 License.

通过向 DoOver 贡献，您同意您的贡献将根据 AGPL-3.0 许可证授权。
