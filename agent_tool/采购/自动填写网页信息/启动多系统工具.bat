@echo off
chcp 65001 >nul
echo ================================================================
echo                   多系统表单工具 - 启动器
echo ================================================================
echo.
echo 正在启动多系统表单工具...
echo.

python multi_system_launcher.py

if errorlevel 1 (
    echo.
    echo 启动失败！请检查：
    echo 1. Python 是否已安装
    echo 2. 是否安装了必要的依赖包
    echo.
    echo 可以运行以下命令安装依赖：
    echo pip install -r requirements.txt
    echo.
    pause
)
