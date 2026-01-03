# 智能会议纪要系统

基于 Vue 2 + Vite 构建的智能会议纪要应用。

## 功能特性

- 🎙️ 实时录音转文字
- 📝 智能会议纪要生成
- 🎨 现代化 UI 设计
- 📱 响应式布局

## 技术栈

- Vue 2.7
- Vite 5
- Element UI
- Vue Router
- Vuex
- Markdown-it

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 http://localhost:3000 启动

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist` 目录

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 组件
│   ├── router/          # 路由配置
│   ├── store/           # Vuex 状态管理
│   ├── utils/           # 工具函数
│   ├── views/           # 页面视图
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── index.html           # HTML 模板
├── vite.config.js       # Vite 配置
└── package.json         # 项目配置
```

## 环境变量

创建 `.env` 文件（可选）：

```
VUE_APP_API_BASE_URL=/api
VUE_APP_WEBSOCKET_BASE_URL=/metwebsocket
```

## 注意事项

1. 本项目需要后端 API 支持，请确保后端服务正常运行
2. WebSocket 功能需要后端支持实时转写
3. 图片资源为占位图片，实际使用时请替换为真实资源


