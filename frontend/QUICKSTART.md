# 快速启动指南

## 1. 安装依赖

```bash
npm install
```

## 2. 启动开发服务器

```bash
npm run dev
```

浏览器会自动打开 http://localhost:3000

## 3. 构建生产版本

```bash
npm run build
```

构建完成后，可以在 `dist` 目录找到生产文件。

## 4. 预览生产构建

```bash
npm run preview
```

## 注意事项

1. **环境变量**：如果需要配置 API 地址，创建 `.env` 文件：
   ```
   VITE_API_BASE_URL=/api
   VITE_WEBSOCKET_BASE_URL=/metwebsocket
   ```

2. **图片资源**：当前使用的是 SVG 占位图片，实际使用时请替换为真实图片资源。

3. **后端服务**：本项目需要后端 API 支持，请确保：
   - `/api/get_transcript` - 音频转文字接口
   - `/api/generate_summary` - 生成会议纪要接口（流式）
   - `/api/prompt/default` - 获取默认提示词接口
   - WebSocket 服务用于实时转写

4. **WebSocket 录音库**：代码中引用了 `window.WebSocketConnectMethod` 和 `window.Recorder`，这些需要从外部引入（通常在 `index.html` 中通过 script 标签引入）。

## 项目结构说明

- `src/components/` - 所有组件文件
- `src/views/` - 页面视图
- `src/router/` - 路由配置
- `src/store/` - Vuex 状态管理
- `src/utils/` - 工具函数
- `src/assets/` - 静态资源

## 常见问题

**Q: 启动时报错找不到模块？**
A: 请先运行 `npm install` 安装所有依赖。

**Q: 图片显示不出来？**
A: 当前使用的是 SVG 占位图片，请替换为真实的图片文件。

**Q: API 请求失败？**
A: 请检查后端服务是否正常运行，并确认环境变量配置正确。


