# Create Release Package Script
# Usage: Right-click -> Run with PowerShell

param(
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Creating Release Package v$Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Paths — use script location to resolve relative paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")
$releaseDir = Join-Path $projectRoot "release_package"
$pdfMergeExe = Join-Path $projectRoot "pdf_merge_tool\dist\PDFMergeTool.exe"
$outlookExe = Join-Path $projectRoot "outlook_agent\dist\OutlookAgent.exe"

# Create release directory
$versionDir = Join-Path $releaseDir "OutlookAgent_v$Version"
if (Test-Path $versionDir) {
    Remove-Item -Recurse -Force $versionDir
}
New-Item -ItemType Directory -Path $versionDir -Force | Out-Null

Write-Host "[1/4] Copying executables..." -ForegroundColor Yellow

# Copy EXEs
Copy-Item $pdfMergeExe $versionDir -Force
Copy-Item $outlookExe $versionDir -Force

Write-Host "  PDFMergeTool.exe - OK"
Write-Host "  OutlookAgent.exe - OK"

Write-Host ""
Write-Host "[2/4] Creating README..." -ForegroundColor Yellow

# Create README
$readmeContent = @"
# Outlook Agent v$Version
## Outlook 邮件监控 & PDF 合并工具

### 安装说明

1. 将 ``OutlookAgent.exe`` 和 ``PDFMergeTool.exe`` 放在同一目录下
2. 双击运行 ``OutlookAgent.exe``
3. 首次运行会弹出配置窗口，自动检测 PDFMergeTool.exe
4. 确保 Outlook 已打开

### 使用方法

1. 启动 OutlookAgent.exe
2. 程序会自动监控 Outlook 邮件
3. 检测到包含关键字的邮件时，会弹出通知
4. 选择需要合并的附件，点击"确认合并"
5. 合并完成后的 PDF 保存在 ``用户目录\merged_output\``

### 配置文件位置

- 配置文件: ``用户目录\outlook_agent_config.json``
- 输出目录: ``用户目录\merged_output\``
- 临时文件: ``用户目录\outlook_agent_temp\``
- 日志文件: ``用户目录\outlook_agent_logs\``

### 默认监控关键字

- 合同审批
- 文件合并
- PDF合并
- 附件处理
- 合并附件

可在设置窗口中自定义关键字。

### 支持的文件格式

- PDF 文件: .pdf
- Word 文档: .docx, .doc
- Excel 表格: .xlsx, .xls
- 文本文件: .txt
- 图片文件: .png, .jpg, .jpeg, .gif, .bmp

### 系统要求

- Windows 10/11
- Microsoft Outlook (已安装并登录)
- .NET Framework 4.5+

### 常见问题

**Q: 提示无法连接 Outlook**
A: 确保 Outlook 正在运行，并已登录邮箱账户

**Q: 合并失败**
A: 检查日志文件 ``用户目录\outlook_agent_logs\`` 查看详细错误

**Q: 如何修改配置**
A: 右键点击托盘图标，选择"设置"

---
版本: $Version
日期: $(Get-Date -Format 'yyyy-MM-dd')
"@

$readmePath = Join-Path $versionDir "README.txt"
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($readmePath, $readmeContent, $utf8NoBom)

Write-Host "  README.txt - OK"

Write-Host ""
Write-Host "[3/4] Creating batch file..." -ForegroundColor Yellow

# Create batch file
$batchContent = @"
@echo off
echo Starting Outlook Agent...
start "" "%~dp0OutlookAgent.exe"
"@

$batchPath = Join-Path $versionDir "启动.bat"
$batchContent | Out-File -FilePath $batchPath -Encoding ASCII

Write-Host "  启动.bat - OK"

Write-Host ""
Write-Host "[4/4] Creating ZIP package..." -ForegroundColor Yellow

# Create ZIP
$zipPath = Join-Path $releaseDir "OutlookAgent_v$Version.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Compress-Archive -Path "$versionDir\*" -DestinationPath $zipPath -Force

Write-Host "  OutlookAgent_v$Version.zip - OK"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Release Package Created!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Package location: $zipPath" -ForegroundColor White
Write-Host "Contents:" -ForegroundColor White
Write-Host "  - OutlookAgent.exe" -ForegroundColor Gray
Write-Host "  - PDFMergeTool.exe" -ForegroundColor Gray
Write-Host "  - README.txt" -ForegroundColor Gray
Write-Host "  - 启动.bat" -ForegroundColor Gray
Write-Host ""

# Open folder
explorer $versionDir

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
