"""
测试下拉框选择 - 验证 __doPostBack 是否生效
"""
from playwright.sync_api import sync_playwright
import time

def test_currency_dropdown():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("\n访问页面...")
        page.goto("https://csmstest.ncs.com.sg/UAT/app/consol_cs/details_pg.aspx")
        page.wait_for_load_state('networkidle')
        
        # 先填写 Proposal #
        print("\n填写 Proposal #...")
        proposal_input = page.locator('#ctl00_ContentPlaceHolder1_txtProposalNo')
        proposal_input.fill('P12345')
        
        # 点击 GET CRM INFO
        print("点击 GET CRM INFO...")
        crm_btn = page.locator('#ctl00_ContentPlaceHolder1_btnInfo')
        crm_btn.click()
        time.sleep(3)  # 等待 CRM 加载
        
        # 测试下拉框
        print("\n测试 Currency Code 下拉框...")
        currency_select = page.locator('#ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode')
        
        if currency_select.count() > 0:
            print("✓ 找到下拉框")
            
            # 方法 1: 使用 select_option
            print("\n方法 1: 使用 select_option('15')...")
            currency_select.select_option('15')  # 15 = USD
            time.sleep(2)
            
            # 检查当前值
            current_value = currency_select.input_value()
            print(f"当前值：{current_value}")
            
            if current_value == '15':
                print("✓ 成功选择 USD (值=15)")
            else:
                print(f"✗ 选择失败，当前值={current_value}")
            
            # 方法 2: 使用 JavaScript + __doPostBack
            print("\n方法 2: 使用 JavaScript + __doPostBack...")
            page.evaluate("""() => {
                var elem = document.getElementById('ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode');
                if (elem) {
                    elem.value = '15';
                    elem.dispatchEvent(new Event('change', { bubbles: true }));
                    if (typeof __doPostBack === 'function') {
                        __doPostBack(elem.id, '');
                        console.log('doPostBack triggered');
                    }
                }
            }""")
            time.sleep(2)
            
            # 再次检查
            current_value = currency_select.input_value()
            print(f"当前值：{current_value}")
            
            if current_value == '15':
                print("✓ JavaScript 方法成功")
            else:
                print(f"✗ JavaScript 方法失败，当前值={current_value}")
            
            # 检查是否有网络请求（__doPostBack 会触发）
            print("\n等待网络请求...")
            time.sleep(2)
            
        else:
            print("✗ 未找到下拉框")
        
        print("\n按回车键退出...")
        input()
        browser.close()

if __name__ == '__main__':
    test_currency_dropdown()
