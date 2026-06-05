@echo off
echo Building Outlook Agent...
echo.

cd /d "%~dp0"

pyinstaller --onefile --windowed --name "OutlookAgent" --hidden-import=win32timezone --hidden-import=pythoncom --hidden-import=pywintypes --hidden-import=win10toast --hidden-import=extract_msg --hidden-import=olefile --hidden-import=xhtml2pdf --hidden-import=xhtml2pdf.pisa --collect-all reportlab main.py

echo.
echo Build complete!
echo Executable is in: dist\OutlookAgent.exe
pause
