from playwright.sync_api import sync_playwright

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

print("=" * 50, flush=True)
print("Playwright Chrome 浏览器测试", flush=True)
print("=" * 50, flush=True)

print(f"\nChrome 路径：{chrome_path}", flush=True)
print("\n正在测试...", flush=True)

try:
    p = sync_playwright().start()
    
    print("  → 启动浏览器...", flush=True)
    browser = p.chromium.launch(
        executable_path=chrome_path,
        headless=False
    )
    print("  → 浏览器启动成功", flush=True)
    
    print("  → 打开新页面...", flush=True)
    page = browser.new_page()
    
    print("  → 访问百度...", flush=True)
    page.goto("https://www.baidu.com")
    
    print("  → 等待页面加载...", flush=True)
    page.wait_for_load_state('networkidle')
    
    title = page.title()
    print(f"  → 页面标题：{title}", flush=True)
    
    browser.close()
    p.stop()
    
    print("\n✓ Chrome 测试成功！", flush=True)
    
except Exception as e:
    print(f"\n✗ Chrome 测试失败：{e}", flush=True)
    import traceback
    traceback.print_exc()

input("\n按回车键退出...")
