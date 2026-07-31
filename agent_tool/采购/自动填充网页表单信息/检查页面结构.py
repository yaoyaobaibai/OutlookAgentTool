"""
检查页面实际结构和行为
"""
from playwright.sync_api import sync_playwright
import time

def inspect_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("\n1. 访问页面...")
        page.goto("https://csmstest.ncs.com.sg/UAT/app/consol_cs/details_pg.aspx")
        page.wait_for_load_state('networkidle')
        
        print("\n2. 填写 Proposal #...")
        page.locator('#ctl00_ContentPlaceHolder1_txtProposalNo').fill('OPP-111239')
        
        print("\n3. 点击 GET CRM INFO...")
        page.locator('#ctl00_ContentPlaceHolder1_btnInfo').click()
        time.sleep(5)  # 等待 CRM 加载
        
        print("\n4. 检查 Currency Code 下拉框的 HTML...")
        
        # 获取完整的 select 元素 HTML
        html = page.locator('#ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode').evaluate('el => el.outerHTML')
        print("\nSelect 元素 HTML:")
        print(html[:1000])  # 打印前 1000 字符
        
        # 检查 onchange 属性
        onchange = page.locator('#ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode').get_attribute('onchange')
        print(f"\nonchange 属性：{onchange}")
        
        # 检查 __doPostBack 是否存在
        has_do_postback = page.evaluate('typeof __doPostBack === "function"')
        print(f"\n__doPostBack 函数存在：{has_do_postback}")
        
        print("\n5. 尝试点击下拉框看是否能打开...")
        currency_select = page.locator('#ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode')
        
        # 尝试点击
        currency_select.click()
        time.sleep(2)
        
        # 检查是否有下拉菜单出现
        dropdown = page.locator('select option[selected]')
        selected = dropdown.first
        if selected.count() > 0:
            print(f"当前选中：{selected.inner_text()}")
        
        print("\n6. 尝试直接选择选项...")
        # 直接选择 USD (value=15)
        try:
            currency_select.select_option('15')
            print("✓ select_option 调用成功")
            time.sleep(2)
            
            # 检查值
            val = currency_select.input_value()
            print(f"当前值：{val}")
            
            # 检查选中的文本
            selected_opt = currency_select.locator('option:checked').first
            if selected_opt.count() > 0:
                print(f"选中项：{selected_opt.inner_text()}")
            
        except Exception as e:
            print(f"✗ 错误：{e}")
        
        print("\n按回车键退出...")
        input()
        browser.close()

if __name__ == '__main__':
    inspect_page()
