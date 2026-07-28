from playwright.sync_api import sync_playwright

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

url = "https://csmstest.ncs.com.sg/UAT/login.aspx"

print("正在打开页面...")
p = sync_playwright().start()
browser = p.chromium.launch(executable_path=chrome_path, headless=False)
page = browser.new_page()
page.goto(url)
page.wait_for_load_state('networkidle')

print("\n页面标题:", page.title())

# 推荐的选择器
selectors_to_try = [
    ('input[name="ctl00$ContentPlaceHolder1$TextBox1"]', 'username'),
    ('input[name="ctl00$ContentPlaceHolder1$TextBox2"]', 'password'),
    ('#ctl00_ContentPlaceHolder1_TextBox1', 'username'),
    ('#ctl00_ContentPlaceHolder1_TextBox2', 'password'),
]

for selector, field_name in selectors_to_try:
    try:
        element = page.locator(selector)
        count = element.count()
        print(f"\n选择器：{selector} ({field_name})")
        print(f"  找到元素数量：{count}")
        
        if count > 0:
            element.wait_for(state='visible', timeout=3000)
            element.fill(f'test_{field_name}')
            print(f"  填充测试：成功")
    except Exception as e:
        print(f"  错误：{e}")

print("\n测试完成，浏览器将在 3 秒后关闭...")
import time
time.sleep(3)
browser.close()
p.stop()
print("Done!")
