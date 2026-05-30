@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Outlook Agent...
python main.py

pause
