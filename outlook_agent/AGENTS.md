# OutlookAgent 子项目指南

## 入口
- main.py → OutlookAgent 类，TKinter 系统托盘 GUI
- build.bat → PyInstaller --onefile --windowed

## 关键文件
- attachment_handler.py → ⚠️ _html_body_to_pdf 双副本之一，修完同步 msg_to_pdf.py
- gui.py → tkinter 确认窗口，EmailConfirmWindow
- merge_launcher.py → 子进程调用 PDFMergeTool.exe --auto
- config.py → JSON 配置，logger.warning 已替换 print
- outlook_monitor.py → Outlook COM 连接，邮件轮询

## 特殊规则
- sys.path.insert 用于动态导入 → PyInstaller 静态分析追踪不到
- 构建时需 --hidden-import=attachment_handler
- 使用 OA 前缀标识日志来源（如 "OA CJK font"）
- __version__ = "1.2.3" 在 main.py 模块级

## 构建
cd agent_tool\outlook_agent
Remove-Item -Force -Recurse dist,build,__pycache__
pyinstaller --onefile --windowed --name "OutlookAgent" --hidden-import=attachment_handler --hidden-import=win32timezone --hidden-import=pythoncom --hidden-import=pywintypes --hidden-import=win10toast --hidden-import=extract_msg --hidden-import=olefile --hidden-import=xhtml2pdf --hidden-import=xhtml2pdf.pisa --collect-all reportlab main.py
