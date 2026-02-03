#!/bin/bash

# 智能会议纪要系统 - 后端启动脚本 (venv)

cd "$(dirname "$0")/backend"

# 检查.venv是否存在
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 升级pip
pip install --upgrade pip -q

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt -q

# 启动服务
echo "启动后端服务..."
python app.py
