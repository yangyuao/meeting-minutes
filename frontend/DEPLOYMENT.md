## 智能会议纪要系统部署手册（对外）

### 1. 项目概述

- **项目名称**：智能会议纪要系统（前端）
- **技术栈**：Vue 2.7 + Vite 4、Vue Router、Vuex、Element UI
- **运行形态**：纯前端单页应用，通过 HTTP API 和 WebSocket 调用后端服务

> 本手册仅说明前端项目的部署步骤，需配合已上线的后端 API 服务一起使用。

---

### 2. 部署前置条件

- **Node.js**：建议使用 Node.js 16 或 18（LTS 版本）
- **npm**：推荐使用 npm 8+（随 Node.js 一起安装）
- **代码仓库权限**：可从 Git 仓库拉取本项目代码
- **后端环境**：
  - 已有对外可访问的 HTTP API 地址
  - 已有对外可访问的 WebSocket 地址（用于实时转写）

---

### 3. 安装依赖

 **安装依赖**

```bash
npm install
```

---

### 4. 环境变量配置

前端通过环境变量配置后端 API 和 WebSocket 地址，关键变量如下：

- **VUE_APP_API_BASE_URL**：HTTP API 根路径，例如 `/api` 或 `https://api.xxx.com`
- **VUE_APP_WEBSOCKET_BASE_URL**：WebSocket 根路径或完整地址，例如 `/metwebsocket` 或 `wss://ws.xxx.com/metwebsocket`

#### 4.1 生产环境示例

在项目根目录创建 `.env.production`（适用于 `npm run build` 默认 production 模式）：

```bash
VUE_APP_API_BASE_URL=/api
VUE_APP_WEBSOCKET_BASE_URL=/metwebsocket
```

如需直接指向外部完整地址，也可以写成：

```bash
VUE_APP_API_BASE_URL=https://your-api-domain.com/api
VUE_APP_WEBSOCKET_BASE_URL=wss://your-ws-domain.com/metwebsocket
```

> 说明：当前端与后端部署在同一域名下时，推荐使用路径写法（如 `/api`），再通过 Nginx/网关做反向代理。

---

### 5. 构建前端静态资源

在项目根目录执行：

```bash
# 标准生产构建
npm run build

# 如有需要，也可以使用自定义模式（可选）
# npm run build:prod   # 对应 .env.prod
# npm run build:test   # 对应 .env.test
```

- 构建完成后，生成的静态资源位于 `dist/` 目录。
- 其中的 `index.html` 和 `assets/` 即为需要部署到 Web 服务器上的文件。

---

### 6. 生产环境部署方式（推荐：Nginx）

#### 6.1 拷贝构建产物到服务器

将本地 `dist/` 目录上传到目标服务器，例如：

- Linux：`/opt/meeting-minutes/dist`
- Windows：`D:\webroot\meeting-minutes\dist`

#### 6.2 Nginx 配置思路（示意）

运维可参考如下配置思路（伪代码，仅供参考）：

- **静态资源**：将域名根路径 `/` 指向 `dist` 目录  
- **API 反向代理**：将 `/api` 转发到后端 HTTP 服务  
- **WebSocket 代理**：将 `/metwebsocket` 转发到后端 WebSocket 服务  

> 实际部署时，请根据公司统一规范调整端口、域名、证书与安全策略。

---

### 7. 启动与验证

1. **启动 Web 服务器**（如 Nginx、IIS、Apache 或云平台内置静态站点服务）
2. 在浏览器访问配置好的域名，例如：

```text
https://your-frontend-domain.com
```

3. 验证功能：
   - 页面能否正常加载、无静态资源 404
   - 录音上传/转写是否成功，是否可以生成会议纪要
   - 浏览器控制台是否存在 API 或 WebSocket 连接错误

---

### 8. 快速体验（测试/演示环境）

如仅需在一台机器上临时演示或测试前端，可直接本地启动开发服务器：

```bash
npm install
npm run dev
```

- 默认访问地址：`https://localhost:3000`
- 此模式仅供本地开发和内部演示使用，不建议直接对外提供服务。


