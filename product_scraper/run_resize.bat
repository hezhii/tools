@echo off
REM 运行图片尺寸调整脚本

echo ==================================
echo 图片尺寸调整工具
echo ==================================
echo.

REM 切换到脚本目录
cd /d %~dp0

REM 检查虚拟环境
if exist "..\venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call ..\venv\Scripts\activate.bat
) else (
    echo 警告: 未找到虚拟环境
)

REM 运行调整脚本
echo 运行图片调整脚本...
python resize_images.py

REM 显示日志
if exist "resize_images.log" (
    echo.
    echo ==================================
    echo 最近的日志记录：
    echo ==================================
    powershell -command "Get-Content resize_images.log -Tail 30"
)

echo.
echo 完成！查看 resize_images.log 了解详细信息
pause
