@echo off
echo Creating Release Package for Outlook Agent v1.2.0
echo.

cd /d "%~dp0"

:: Build both executables
echo Step 1: Building OutlookAgent.exe...
call build.bat

if not exist "dist\OutlookAgent.exe" (
    echo ERROR: Build failed! OutlookAgent.exe not found.
    pause
    exit /b 1
)

echo.
echo Step 1b: Building PDFMergeTool.exe...
pushd "..\pdf_merge_tool"
call build.bat
popd

if not exist "..\pdf_merge_tool\dist\PDFMergeTool.exe" (
    echo ERROR: Build failed! PDFMergeTool.exe not found.
    pause
    exit /b 1
)

:: Create release directory
echo.
echo Step 2: Creating release directory...
if not exist "..\release_package" mkdir "..\release_package"
if not exist "..\release_package\OutlookAgent_v1.2.0" mkdir "..\release_package\OutlookAgent_v1.2.0"

:: Copy files
echo.
echo Step 3: Copying files...
copy /Y "dist\OutlookAgent.exe" "..\release_package\OutlookAgent_v1.2.0\"
copy /Y "..\pdf_merge_tool\dist\PDFMergeTool.exe" "..\release_package\OutlookAgent_v1.2.0\"

:: Create README if not exists
if not exist "..\release_package\OutlookAgent_v1.2.0\README.txt" (
    echo Creating README.txt...
    (
        echo # Outlook Agent v1.2.0
        echo ## Outlook 邮件监控 ^& PDF 合并工具
        echo.
        echo ### 安装说明
        echo 1. 将 OutlookAgent.exe 和 PDFMergeTool.exe 放在同一目录下
        echo 2. 双击运行 OutlookAgent.exe
        echo 3. 首次运行会弹出配置窗口，自动检测 PDFMergeTool.exe
        echo 4. 确保 Outlook 已打开
        echo.
        echo ### 使用方法
        echo **方式一：自动监控**
        echo - 启动 OutlookAgent.exe
        echo - 程序会自动监控 Outlook 邮件
        echo - 检测到包含关键字的邮件时，会弹出通知
        echo.
        echo **方式二：手动上传 .msg 文件**
        echo - 在主界面点击"选择 .msg 文件"按钮
        echo - 选择 Outlook 导出的 .msg 文件
        echo.
        echo ### 系统要求
        echo - Windows 10/11
        echo - Microsoft Outlook (已安装并登录)
    ) > "..\release_package\OutlookAgent_v1.2.0\README.txt"
)

:: Create zip
echo.
echo Step 4: Creating ZIP archive...
powershell -Command "Compress-Archive -Path '..\release_package\OutlookAgent_v1.2.0\*' -DestinationPath '..\release_package\OutlookAgent_v1.2.0.zip' -Force"

echo.
echo ========================================
echo Release package created successfully!
echo Location: ..\release_package\OutlookAgent_v1.2.0.zip
echo ========================================
pause
