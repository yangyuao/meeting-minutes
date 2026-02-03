#!/bin/bash

# 智能会议纪要系统 - 后端启动脚本 (uv)

cd "$(dirname "$0")/backend"

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到 uv，请先安装 uv"
    echo "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 检查.venv是否存在
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    uv venv
fi

# 同步依赖
echo "同步依赖..."
uv pip sync requirements.txt

# 启动服务
echo "启动后端服务..."
source .venv/bin/activate
python app.py
