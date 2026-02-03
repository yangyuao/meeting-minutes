#!/bin/bash

# 智能会议纪要系统 - 后端启动脚本 (conda)

cd "$(dirname "$0")/backend"

# 检查conda是否安装
if ! command -v conda &> /dev/null; then
    echo "错误: 未找到 conda，请先安装 Anaconda 或 Miniconda"
    exit 1
fi

# 检查conda环境是否存在
if ! conda env list | grep -q "^meeting-minutes "; then
    echo "创建conda环境..."
    conda env create -f environment.yml
fi

# 激活conda环境
echo "激活conda环境..."
eval "$(conda shell.bash hook)"
conda activate meeting-minutes

# 启动服务
echo "启动后端服务..."
python app.py
