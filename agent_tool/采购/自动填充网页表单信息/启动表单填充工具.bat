@echo off
chcp 65001 >nul
echo ========================================
echo   表单自动填充工具 - FormFiller
echo ========================================
echo.
echo 正在启动程序...
echo.

cd /d "%~dp0"
FormFiller.exe

pause
