@echo off
chcp 65001 >nul
echo ========================================
echo   PyInstaller 打包脚本
echo ========================================
echo.
echo 开始打包 FormFiller...
echo 这可能需要 5-10 分钟
echo 请不要关闭此窗口
echo.
echo 开始时间：%time%
echo.

cd /d "%~dp0"

REM 清理旧文件
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM 执行打包
"C:\Users\p1325970\AppData\Local\Python\pythoncore-3.14-64\Scripts\pyinstaller.exe" ^
  --name FormFiller ^
  --onefile ^
  --console ^
  --add-data "form_config.json;." ^
  --add-data "attachment_config.json;." ^
  --hidden-import pandas ^
  --hidden-import openpyxl ^
  --hidden-import playwright ^
  --hidden-import tkinter ^
  --exclude-module torch ^
  --exclude-module torchvision ^
  --exclude-module tensorflow ^
  --exclude-module onnxruntime ^
  form_filler.py

echo.
echo 结束时间：%time%
echo.

if exist "dist\FormFiller.exe" (
    echo ========================================
    echo   ✓✓✓ 打包成功！
    echo ========================================
    echo.
    for %%A in ("dist\FormFiller.exe") do (
        echo 文件路径：%%~fA
        echo 文件大小：%%~zA 字节
    )
    echo.
    echo 按任意键打开程序文件夹...
    pause >nul
    explorer "dist"
) else (
    echo ========================================
    echo   ✗✗✗ 打包失败
    echo ========================================
    echo.
    echo 请检查上面的错误信息
    echo.
    pause
)
