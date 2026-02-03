# 智能会议纪要系统

基于 FastAPI + Vue 2 的智能会议纪要自动生成系统，支持语音转文字、LLM 生成会议纪要、导出 Word 文档等功能。

## 项目结构

```
meeting-minutes/
├── backend/               # 后端服务
│   ├── app.py           # FastAPI 主应用
│   ├── requirements.txt # Python依赖
│   ├── pyproject.toml   # uv项目配置
│   ├── environment.yml  # conda环境配置
│   ├── ENV_SETUP.md     # 环境管理说明
│   ├── hotwords.txt     # 热词列表
│   └── 会议纪要模板.docx
├── frontend/             # 前端应用
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── components/
│   │   ├── views/
│   │   ├── router/
│   │   ├── store/
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── start-backend.sh      # 后端启动脚本
├── start-uv.sh           # uv启动脚本
├── start-venv.sh         # venv启动脚本
├── start-conda.sh        # conda启动脚本
├── start-frontend.sh     # 前端启动脚本
├── .gitignore
├── .env.example
└── README.md
```

## 功能特性

### 后端
- 语音识别 (基于 FunASR)
- 文本清洗与预处理
- 大语言模型集成 (Ollama / vLLM)
- 数据库记录存储
- DOCX 文档导出

### 前端
- 音频录制与上传
- 实时转录显示
- 会议纪要生成
- Word 文档下载
- Markdown 渲染

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+ / 8.0+
- CUDA 11.x+ (GPU 加速)

### 后端设置

本项目支持三种Python环境管理方式：**uv** (推荐)、**venv** 和 **conda**。

详细说明请参考 [backend/ENV_SETUP.md](backend/ENV_SETUP.md)。

#### 方式一：使用启动脚本（推荐）

```bash
./start-backend.sh
```

然后选择对应的环境管理方式。

#### 方式二：手动设置

**uv (最快):**
```bash
cd backend
uv venv                          # 创建.venv虚拟环境
uv pip sync requirements.txt     # 同步依赖
source .venv/bin/activate        # 激活环境
python app.py                     # 启动服务
```

**venv:**
```bash
cd backend
python3 -m venv .venv            # 创建.venv虚拟环境
source .venv/bin/activate        # 激活环境
pip install -r requirements.txt  # 安装依赖
python app.py                    # 启动服务
```

**conda:**
```bash
cd backend
conda env create -f environment.yml   # 创建meeting-minutes环境
conda activate meeting-minutes         # 激活环境
python app.py                          # 启动服务
```

#### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库、API 等参数
```

#### 创建数据库

```sql
CREATE DATABASE meeting_minutes DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

服务将在 `http://localhost:8002` 启动。

### 前端设置

1. 安装依赖
```bash
cd frontend
npm install
```

2. 配置后端 API 地址
编辑 `src/utils/env.js`，设置正确的 API_BASE_URL。

3. 启动开发服务器
```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动。

### 生产部署

#### 后端
```bash
cd backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8002 app:app
```

#### 前端
```bash
cd frontend
npm run build
# 使用 nginx 托管 dist 目录
```

## API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | 健康检查 |
| GET | `/prompt/default` | 获取默认提示词模板 |
| GET | `/test-vllm` | 测试 vLLM 模型 |
| POST | `/get_transcript` | 音频转文字 |
| POST | `/generate_summary` | 生成会议纪要 |
| POST | `/generate_docx` | 导出 Word 文档 |
| POST | `/upload` | 上传音频文件 |

## 配置说明

### 环境变量

参考 `.env.example` 文件，主要配置项：

- `HOST`: 后端服务监听地址
- `PORT`: 后端服务端口
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`: MySQL 数据库配置
- `OLLAMA_API`, `OLLAMA_MODEL`: Ollama 模型配置
- `VLLM_API`, `VLLM_MODEL`: vLLM 模型配置
- `ASR_MODEL`, `VAD_MODEL`, `PUNC_MODEL`, `SPK_MODEL`: 语音识别模型路径

### 热词配置

编辑 `backend/hotwords.txt`，每行一个热词，用于提高识别准确率。

### Word 模板

修改 `backend/会议纪要模板.docx` 自定义导出文档格式。

## 技术栈

### 后端
- FastAPI - Web 框架
- FunASR - 语音识别
- PyMySQL - 数据库驱动
- python-docx - Word 文档生成

### 前端
- Vue 2 - 前端框架
- Vue Router - 路由
- Vuex - 状态管理
- Element UI - UI 组件库
- Vite - 构建工具
- Axios - HTTP 客户端
- markdown-it - Markdown 渲染

## 常见问题

### 语音识别失败
- 检查 CUDA 是否可用
- 确认模型文件路径正确
- 查看日志确认错误信息

### LLM 生成失败
- 确认 LLM 服务正常运行
- 检查 API 地址和配置

### 数据库连接失败
- 确认 MySQL 服务运行
- 检查用户名密码和权限

## 许可证

MIT License
