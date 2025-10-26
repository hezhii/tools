#!/bin/bash
# 运行 output 目录处理脚本

echo "=================================="
echo "处理 output 目录"
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

# 运行处理脚本
echo "运行处理脚本..."
python3 process_output.py

# 显示日志
if [ -f "process_output.log" ]; then
    echo ""
    echo "=================================="
    echo "最近的日志记录："
    echo "=================================="
    tail -20 process_output.log
fi

echo ""
echo "完成！查看 process_output.log 了解详细信息"
