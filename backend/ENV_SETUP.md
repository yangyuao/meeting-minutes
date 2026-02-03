# 后端环境管理

本项目支持三种Python环境管理方式：uv、venv 和 conda。

## 快速开始

推荐使用 `uv`，它是最快且最现代的Python包管理器。

```bash
./start-backend.sh
```

然后选择对应的环境管理方式。

## 环境管理方式

### 1. uv (推荐)

最快速、现代的Python包管理器。

**安装 uv:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**启动服务:**
```bash
./start-uv.sh
```

**手动操作:**
```bash
cd backend
uv venv                      # 创建.venv虚拟环境
uv pip sync requirements.txt  # 同步依赖
source .venv/bin/activate     # 激活环境
python app.py                 # 启动服务
```

### 2. venv

标准Python虚拟环境。

**启动服务:**
```bash
./start-venv.sh
```

**手动操作:**
```bash
cd backend
python3 -m venv .venv        # 创建.venv虚拟环境
source .venv/bin/activate    # 激活环境
pip install -r requirements.txt  # 安装依赖
python app.py                # 启动服务
```

### 3. conda

使用Anaconda或Miniconda管理环境。

**启动服务:**
```bash
./start-conda.sh
```

**手动操作:**
```bash
cd backend
conda env create -f environment.yml  # 创建meeting-minutes环境
conda activate meeting-minutes       # 激活环境
python app.py                        # 启动服务
```

**更新环境:**
```bash
conda env update -f environment.yml
```

**删除环境:**
```bash
conda remove -n meeting-minutes --all
```

## 虚拟环境命名

- **uv/venv**: `.venv`
- **conda**: `meeting-minutes`

## 配置文件

- `requirements.txt`: 传统的Python依赖列表
- `pyproject.toml`: uv的现代化项目配置
- `environment.yml`: conda环境配置

## 常见问题

### uv未找到
请先安装uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### conda命令未找到
请先安装Anaconda或Miniconda，并确保已初始化conda。

### 端口冲突
修改 `.env` 文件中的 `PORT` 配置。

### CUDA版本问题
确保CUDA版本与torch版本匹配，参考 `requirements.txt` 中的版本。
