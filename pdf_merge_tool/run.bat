@echo off
echo PDF Merge Tool
echo ==============
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo Checking dependencies...
pip install -r requirements.txt -q

echo Starting...
python main.py

pause
