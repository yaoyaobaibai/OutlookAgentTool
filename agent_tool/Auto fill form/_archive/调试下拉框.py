"""
调试下拉框问题
"""
from playwright.sync_api import sync_playwright
import time

def debug_dropdown():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("\n1. 访问页面...")
        page.goto("https://csmstest.ncs.com.sg/UAT/app/consol_cs/details_pg.aspx")
        page.wait_for_load_state('networkidle')
        
        print("\n2. 填写 Proposal #...")
        page.locator('#ctl00_ContentPlaceHolder1_txtProposalNo').fill('P12345')
        
        print("\n3. 点击 GET CRM INFO...")
        page.locator('#ctl00_ContentPlaceHolder1_btnInfo').click()
        time.sleep(3)
        
        print("\n4. 检查下拉框状态...")
        select_elem = page.locator('#ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode')
        
        # 获取当前选中的 option
        selected = select_elem.locator('option:checked').first
        selected_text = selected.inner_text() if selected.count() > 0 else "N/A"
        selected_value = selected.input_value() if selected.count() > 0 else "N/A"
        
        print(f"   当前选中：text='{selected_text}', value='{selected_value}'")
        
        # 获取所有 options
        options = select_elem.locator('option')
        print(f"   可用选项数量：{options.count()}")
        for i in range(min(5, options.count())):
            opt = options.nth(i)
            print(f"     [{opt.input_value()}] {opt.inner_text()}")
        
        print("\n5. 尝试 select_option('15')...")
        try:
            select_elem.select_option('15')
            print("   ✓ select_option 调用成功")
        except Exception as e:
            print(f"   ✗ select_option 失败：{e}")
        
        time.sleep(2)
        
        # 再次检查
        selected = select_elem.locator('option:checked').first
        selected_text = selected.inner_text() if selected.count() > 0 else "N/A"
        selected_value = selected.input_value() if selected.count() > 0 else "N/A"
        print(f"   选择后：text='{selected_text}', value='{selected_value}'")
        
        print("\n6. 使用 JavaScript 设置...")
        page.evaluate("""() => {
            var elem = document.getElementById('ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode');
            console.log('Element found:', elem !== null);
            if (elem) {
                console.log('Old value:', elem.value);
                elem.value = '15';
                console.log('New value:', elem.value);
                
                // 触发 change 事件
                elem.dispatchEvent(new Event('change', { bubbles: true }));
                console.log('Change event dispatched');
                
                // 尝试 __doPostBack
                if (typeof __doPostBack === 'function') {
                    __doPostBack(elem.id, '');
                    console.log('doPostBack called');
                } else {
                    console.log('__doPostBack not available');
                }
            }
        }""")
        
        time.sleep(3)
        
        # 第三次检查
        selected = select_elem.locator('option:checked').first
        selected_text = selected.inner_text() if selected.count() > 0 else "N/A"
        selected_value = selected.input_value() if selected.count() > 0 else "N/A"
        print(f"   JS 执行后：text='{selected_text}', value='{selected_value}'")
        
        print("\n按回车键退出...")
        input()
        browser.close()

if __name__ == '__main__':
    debug_dropdown()
