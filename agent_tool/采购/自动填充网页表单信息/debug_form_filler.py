import sys
import traceback

print("脚本开始执行...", flush=True)

try:
    import tkinter as tk
    print("✓ tkinter 导入成功", flush=True)
except Exception as e:
    print(f"✗ tkinter 导入失败：{e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

try:
    from tkinter import ttk, messagebox
    print("✓ tkinter 组件导入成功", flush=True)
except Exception as e:
    print(f"✗ tkinter 组件导入失败：{e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

try:
    import json
    import os
    import threading
    print("✓ 标准库导入成功", flush=True)
except Exception as e:
    print(f"✗ 标准库导入失败：{e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright
    print("✓ playwright 导入成功", flush=True)
except Exception as e:
    print(f"✗ playwright 导入失败：{e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

print("\n开始创建 GUI...", flush=True)

try:
    root = tk.Tk()
    root.title("表单自动填充工具 - 调试模式")
    root.geometry("400x300")
    
    label = ttk.Label(root, text="GUI 启动成功！", font=("Arial", 16))
    label.pack(pady=50)
    
    info = ttk.Label(root, text="如果看到这个窗口，说明 tkinter 正常工作")
    info.pack()
    
    def close_app():
        root.destroy()
        print("GUI 已关闭", flush=True)
    
    root.protocol("WM_DELETE_WINDOW", close_app)
    
    print("GUI 窗口已创建，正在运行主循环...", flush=True)
    root.mainloop()
    print("主循环结束", flush=True)
    
except Exception as e:
    print(f"\n✗ GUI 创建失败：{e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

print("\n脚本执行完毕", flush=True)
