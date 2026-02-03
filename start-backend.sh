#!/bin/bash

# 智能会议纪要系统 - 后端启动脚本 (通用)

echo "========================================"
echo "  智能会议纪要系统 - 后端启动脚本"
echo "========================================"
echo ""
echo "请选择包管理工具:"
echo "  1) uv      (推荐，快速)"
echo "  2) venv    (标准Python虚拟环境)"
echo "  3) conda   (Anaconda/Miniconda)"
echo ""
read -p "请输入选项 (1-3) [默认: 2]: " choice
choice=${choice:-2}

case $choice in
    1)
        exec "$(dirname "$0")/start-uv.sh"
        ;;
    2)
        exec "$(dirname "$0")/start-venv.sh"
        ;;
    3)
        exec "$(dirname "$0")/start-conda.sh"
        ;;
    *)
        echo "无效的选项"
        exit 1
        ;;
esac
