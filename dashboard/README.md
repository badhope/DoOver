# DoOver 界面

这是一个基于 `Vue 3 + TypeScript + Vite` 的前端界面项目，用来展示 DoOver 的流式分析结果。

前端会通过 WebSocket 连接到：

```txt
ws://localhost:8765
```

注意：
这个仓库当前只包含前端界面代码，不包含 `8765` 端口对应的后端服务。
如果后端没有启动，页面仍然可以打开，但会显示未连接，并每 3 秒自动重试一次。

## 环境要求

- Node.js
- npm

建议使用较新的 Node.js LTS 版本。

## 别人 `git clone` 下来如何启动

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd doover
```

如果仓库根目录不是 `doover`，进入实际的前端项目目录即可。

### 2. 安装依赖

```bash
npm install
```

### 3. 启动前端开发环境

```bash
npm run dev
```

启动后，终端里会显示本地访问地址，默认一般是：

```txt
http://localhost:5173
```

用浏览器打开即可。

### 4. 启动后端 WebSocket 服务

前端依赖一个运行在 `ws://localhost:8765` 的服务端。

前端当前会发送和接收这些消息类型：

- 发送：`user_input`
- 发送：`user_answer`
- 接收：`ask_user`
- 接收：普通流式文本行
- 接收：`Baidu Search Result: ...`

如果本地没有这个服务：

- 页面可以打开
- 状态会显示连接失败或断开
- 前端会每 3 秒自动重连
- 但无法真正开始分析

所以完整联调时，需要先把对应后端服务启动到 `8765` 端口。

## Pretext 文本排版实现

项目使用了 [`@chenglou/pretext`](https://www.npmjs.com/package/@chenglou/pretext) 作为多行文本测量与换行布局引擎，用它来替代“每次都靠 DOM 量高度、量宽度”的做法。

### 实现位置

- 依赖声明：`package.json`
- 公共封装组件：`src/components/PretextBlock.vue`
- 页面接入位置：`src/App.vue`

### 当前实现方式

`PretextBlock.vue` 是项目里所有长文本区域的统一排版入口，核心流程如下：

1. 通过 `prepareWithSegments(text, font, options)` 预处理文本，得到可复用的排版数据
2. 通过 `layoutWithLines(prepared, width, lineHeight)` 按当前容器宽度计算每一行的内容和总高度
3. 使用 `ResizeObserver` 监听容器宽度变化，只在宽度变化时重新计算换行结果
4. 模板层按 `lines` 逐行渲染，并在流式输出场景下显示光标动画

也就是说，这个项目不是把整段文本直接交给浏览器自由换行，而是先由 Pretext 算好“这一段在当前宽度下应该拆成哪些行”，再交给 Vue 渲染。

### 已接入的界面区域

以下区域已经统一接入 Pretext：

- Input / 当前输入
- Search Feed / 搜索结果摘要
- 实时分析
- 执行轨迹
- Question 弹窗内容

### 在这个项目里的作用

这个界面本质上是一个流式控制台，不是普通静态文章页。它有几个明显特征：

- 文本会不断追加
- 多个模块都是固定高度
- 不同模块会同时滚动、换行和刷新
- 文本内容包含中文、英文、符号、emoji 以及混排情况

Pretext 在这里主要解决的是：

1. 固定宽度下多行文本如何稳定换行
2. 固定高度面板里文本如何更可控地显示和滚动
3. 流式追加文本时如何减少因为重新测量 DOM 导致的抖动

### 使用 Pretext 的优点

- 减少 `getBoundingClientRect`、`offsetHeight` 一类 DOM 测量带来的回流和重排成本
- 换行逻辑更稳定，窗口尺寸变化时表现更一致
- 对中文、英文、emoji、混排文本更友好
- 很适合当前这种“固定高度卡片 + 实时流式输出”的界面结构
- 统一封装到 `PretextBlock.vue` 后，多个模块共用同一套排版规则，维护成本更低
- 更容易实现“新内容出现时自动滚到最新位置”的阅读体验

### 为什么这里比纯 DOM 文本测量更合适

如果完全依赖浏览器原生文本流布局，这个项目在下面这些场景里更容易出现问题：

- 新文本持续插入时，面板高度和滚动位置不稳定
- 面板宽度变化时，换行结果容易跳动
- 多语言混排时，不同区域的显示一致性更难控制

而 Pretext 的价值就在于：

- 先计算文本怎么分行，再交给界面渲染
- 让“换行”和“显示”分离
- 让固定高度模块可以拥有更稳定、更工程化的文本布局行为

## 生产构建

```bash
npm run build
```

构建产物会输出到：

```txt
dist/
```

## 本地预览生产构建

先构建：

```bash
npm run build
```

再预览：

```bash
npm run preview
```

## 常用命令

```bash
npm run dev
npm run build
npm run preview
```

## 启动排查

### 页面能打开，但一直显示未连接

说明前端启动成功了，但 `ws://localhost:8765` 没有可用服务。

检查：

- 后端是否已经启动
- 后端端口是否确实是 `8765`
- 本机防火墙是否拦截了该端口

### `npm install` 失败

通常是 Node.js / npm 环境问题，或网络拉包失败。

检查：

- Node.js 是否正确安装
- `npm -v` 和 `node -v` 是否可用
- 网络是否可以访问 npm registry

### `npm run dev` 后浏览器打不开

检查：

- 终端是否有报错
- 端口是否被占用
- 是否访问了终端输出的实际地址

## 项目脚本

`package.json` 中当前可用脚本：

```json
{
  "dev": "vite",
  "build": "vue-tsc -b && vite build",
  "preview": "vite preview"
}
```
