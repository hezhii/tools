#!/bin/bash
# 运行图片尺寸调整脚本

echo "=================================="
echo "图片尺寸调整工具"
echo "=================================="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查虚拟环境
if [ -d "../venv" ]; then
    echo "激活虚拟环境..."
    source ../venv/bin/activate
else
    echo "警告: 未找到虚拟环境"
fi

# 运行调整脚本
echo "运行图片调整脚本..."
python3 resize_images.py

# 显示日志
if [ -f "resize_images.log" ]; then
    echo ""
    echo "=================================="
    echo "最近的日志记录："
    echo "=================================="
    tail -30 resize_images.log
fi

echo ""
echo "完成！查看 resize_images.log 了解详细信息"
