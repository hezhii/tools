@echo off
REM 运行 output 目录处理脚本

echo ==================================
echo 处理 output 目录
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

REM 运行处理脚本
echo 运行处理脚本...
python process_output.py

REM 显示日志
if exist "process_output.log" (
    echo.
    echo ==================================
    echo 最近的日志记录：
    echo ==================================
    powershell -command "Get-Content process_output.log -Tail 20"
)

echo.
echo 完成！查看 process_output.log 了解详细信息
pause
