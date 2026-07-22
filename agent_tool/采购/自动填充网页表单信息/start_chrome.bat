@echo off
echo 正在启动 Chrome (调试模式)...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome-debug-profile"
echo.
echo Chrome 已启动！
echo.
echo 请按以下步骤操作：
echo 1. 在 Chrome 中打开要填充的网页
echo 2. 运行 form_filler.py
echo 3. 勾选"使用已打开的 Chrome 窗口"
echo 4. 点击"启动填充"
echo.
pause
