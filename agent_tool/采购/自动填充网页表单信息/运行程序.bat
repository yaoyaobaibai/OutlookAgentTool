@echo off
chcp 65001 >nul
echo ========================================
echo   表单自动填充工具 - FormFiller
echo ========================================
echo.
echo 正在启动程序...
echo.

cd /d "%~dp0"
python form_filler.py

if errorlevel 1 (
    echo.
    echo 程序运行出错！
    echo 请确保已安装 Python 和必要的依赖包
    pause
)
