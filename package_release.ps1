# Outlook Agent Release Package Script
# Usage: powershell -ExecutionPolicy Bypass -File package_release.ps1

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Outlook Agent - Release Packaging" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$outlookExe = Join-Path $scriptDir "outlook_agent\dist\OutlookAgent.exe"
$pdfMergeExe = Join-Path $scriptDir "pdf_merge_tool\dist\PDFMergeTool.exe"

# Step 1: Check exes
Write-Host "[1/4] Checking build outputs..." -ForegroundColor Yellow
if (-not (Test-Path $outlookExe)) {
    Write-Host "  ERROR: OutlookAgent.exe not found. Run outlook_agent\build.bat first." -ForegroundColor Red
    pause
    exit 1
}
if (-not (Test-Path $pdfMergeExe)) {
    Write-Host "  ERROR: PDFMergeTool.exe not found. Run pdf_merge_tool\build.bat first." -ForegroundColor Red
    pause
    exit 1
}
Write-Host "  OK: OutlookAgent.exe" -ForegroundColor Green
Write-Host "  OK: PDFMergeTool.exe" -ForegroundColor Green

# Step 2: Create release directory
Write-Host ""
Write-Host "[2/4] Creating release directory..." -ForegroundColor Yellow
$releaseDir = Join-Path $scriptDir "release_package"
if (Test-Path $releaseDir) {
    Remove-Item -Recurse -Force $releaseDir
}
$outDir = Join-Path $releaseDir "OutlookAgent"
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
Write-Host "  OK: $outDir" -ForegroundColor Green

# Step 3: Copy files
Write-Host ""
Write-Host "[3/4] Copying files..." -ForegroundColor Yellow
Copy-Item $outlookExe $outDir -Force
Copy-Item $pdfMergeExe $outDir -Force
Write-Host "  OK: OutlookAgent.exe" -ForegroundColor Green
Write-Host "  OK: PDFMergeTool.exe" -ForegroundColor Green

# Step 4: Copy README
Write-Host ""
Write-Host "[4/4] Copying README..." -ForegroundColor Yellow
$readmeSource = Join-Path $scriptDir "OutlookAgent_v1.1.1_release\README.txt"
$readmePath = Join-Path $outDir "README.txt"
if (Test-Path $readmeSource) {
    Copy-Item $readmeSource $readmePath -Force
    Write-Host "  OK: README.txt (Chinese)" -ForegroundColor Green
} else {
    Write-Host "  WARNING: README source not found, skipping" -ForegroundColor Yellow
}

# Create ZIP with password (using 7-Zip)
Write-Host ""
Write-Host "Creating password-protected ZIP..." -ForegroundColor Yellow
$zipPath = Join-Path $releaseDir "OutlookAgent.zip"
$sevenZip = "C:\Program Files\7-Zip\7z.exe"
if (-not (Test-Path $sevenZip)) {
    $sevenZip = "C:\Program Files (x86)\ManageEngine\UEMS_Agent\bin\7z.exe"
}
if (Test-Path $sevenZip) {
    Push-Location $outDir
    & $sevenZip a -tzip -p123456 -y "$zipPath" . 2>&1 | Out-Null
    Pop-Location
    Write-Host "  OK: $zipPath (password: 123456)" -ForegroundColor Green
} else {
    Write-Host "  WARNING: 7-Zip not found, creating standard ZIP" -ForegroundColor Yellow
    Compress-Archive -Path "$outDir\*" -DestinationPath $zipPath -Force
    Write-Host "  OK: $zipPath (no password)" -ForegroundColor Green
}

# Done
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Packaging complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Release folder: $outDir" -ForegroundColor Cyan
Write-Host "ZIP archive:    $zipPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "User steps:" -ForegroundColor White
Write-Host "  1. Unzip OutlookAgent.zip" -ForegroundColor White
Write-Host "  2. Double-click OutlookAgent.exe" -ForegroundColor White
Write-Host ""
pause
