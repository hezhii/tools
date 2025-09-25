#!/bin/bash

# 工业产品爬虫运行脚本

echo "=== 工业产品网站爬虫 ==="
echo "目标网站: https://shwz888.gys.cn/supply/"
echo

# 检查根目录虚拟环境
if [ ! -d "../venv" ]; then
    echo "在根目录创建虚拟环境..."
    cd ..
    python3 -m venv venv
    cd product_scraper
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source ../venv/bin/activate

# 安装依赖
echo "检查并安装依赖..."
pip install -r ../requirements.txt

# 清理之前的输出
if [ -d "output" ]; then
    echo "清理之前的输出文件..."
    rm -rf output/*
fi

echo
echo "开始运行爬虫..."
echo "注意：已优化速度与稳定性平衡，预计1-2小时完成"
echo "智能延时配置：请求间2-5秒，分类间8-15秒，页面间3-8秒"
echo "相比原配置速度提升约50-60%"
echo

# 运行爬虫
python product_scraper.py

echo
echo "=== 运行完成 ==="
echo "查看结果："
echo "- Excel文件: output/products.xlsx"
echo "- 产品图片: output/images/"
echo "- 运行日志: scraper.log"
echo "- 调试信息: output/debug_info.json"