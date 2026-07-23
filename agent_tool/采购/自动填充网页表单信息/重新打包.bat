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
  form_filler.py ^
  --name FormFiller ^
  --onefile ^
  --console ^
  --add-data "form_config.json;." ^
  --add-data "attachment_config.json;." ^
  --hidden-import pandas ^
  --hidden-import openpyxl ^
  --hidden-import playwright

echo.
if exist "dist\FormFiller.exe" (
    echo ========================================
    echo   ✓ 打包成功！
    echo ========================================
    echo.
    echo 程序位置：dist\FormFiller.exe
    echo 文件大小：
    for %%A in ("dist\FormFiller.exe") do echo            %%~zA 字节
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
