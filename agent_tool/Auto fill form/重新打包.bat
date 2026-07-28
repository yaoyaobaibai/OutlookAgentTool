@echo off
chcp 65001 >nul
echo ========================================
echo   重新打包 FormFiller
echo ========================================
echo.
echo 正在删除旧的打包文件...
if exist "dist" (
    rmdir /s /q dist
    echo 已删除旧的 dist 目录
) else (
    echo dist 目录不存在
)
echo.

echo 正在打包...
echo 这可能需要 2-5 分钟，请耐心等待...
echo.

"C:\Users\p1325970\AppData\Local\Python\pythoncore-3.14-64\Scripts\pyinstaller.exe" ^
  --name FormFiller ^
  --onedir ^
  --console ^
  --add-data "form_config.json;." ^
  --add-data "attachment_config.json;." ^
  --hidden-import pandas ^
  --hidden-import openpyxl ^
  --hidden-import playwright ^
  --hidden-import tkinter ^
  --add-data "workflows;workflows" ^
  --add-data "handlers;handlers" ^
  --hidden-import workflow_manager ^
  --hidden-import workflow_engine ^
  --hidden-import handlers ^
  --hidden-import handlers.input_handler ^
  --hidden-import handlers.select_handler ^
  --hidden-import handlers.checkbox_handler ^
  --hidden-import handlers.autocomplete_handler ^
  --hidden-import handlers.datepicker_handler ^
  --hidden-import handlers.popup_search_handler ^
  --hidden-import handlers.file_upload_handler ^
  --exclude-module torch ^
  --exclude-module torchvision ^
  --exclude-module tensorflow ^
  --exclude-module onnxruntime ^
  form_filler.py

echo.
if exist "dist\FormFiller\FormFiller.exe" (
    echo ========================================
    echo   ✓ 打包成功！
    echo ========================================
    echo.
    echo 程序位置：dist\FormFiller\FormFiller.exe
    echo 文件大小：
    for %%A in ("dist\FormFiller\FormFiller.exe") do echo            %%~zA 字节
    echo.
    echo 按任意键查看程序文件夹...
    pause >nul
    explorer "dist"
) else (
    echo ========================================
    echo   ✗ 打包失败
    echo ========================================
    echo 请检查错误信息
    echo.
    pause
)
