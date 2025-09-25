@echo off
chcp 65001 >nul

echo === 工业产品网站爬虫 ===
echo 目标网站: https://shwz888.gys.cn/supply/
echo.

REM 检查根目录虚拟环境
if not exist "..\venv" (
    echo 在根目录创建虚拟环境...
    cd ..
    python -m venv venv
    cd product_scraper
)

REM 激活虚拟环境
echo 激活虚拟环境...
call ..\venv\Scripts\activate.bat

REM 安装依赖
echo 检查并安装依赖...
pip install -r ..\requirements.txt

REM 清理之前的输出
if exist "output" (
    echo 清理之前的输出文件...
    rmdir /s /q output
)

echo.
echo 开始运行爬虫...
echo 注意：爬虫已优化速度和稳定性平衡，具备强大的反反爬机制
echo 智能延时配置：请求间2-5秒，分类间8-15秒，页面间3-8秒
echo 预计运行时间：1-2小时（相比之前提升了50-60%的速度）
echo.

REM 运行爬虫
python product_scraper.py

echo.
echo === 运行完成 ===
echo 查看结果：
echo - Excel文件: output\products.xlsx
echo - 产品图片: output\images\
echo - 运行日志: scraper.log
echo - 调试信息: output\debug_info.json

pause