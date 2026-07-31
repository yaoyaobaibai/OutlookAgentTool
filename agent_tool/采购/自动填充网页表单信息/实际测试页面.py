"""
实际访问页面测试填写流程
"""
from playwright.sync_api import sync_playwright
import time

def test_real_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("\n" + "="*60)
        print("步骤 1: 访问登录页面")
        print("="*60)
        page.goto("https://csmstest.ncs.com.sg/UAT/login.aspx")
        page.wait_for_load_state('networkidle')
        print("✓ 页面已加载")
        
        print("\n" + "="*60)
        print("步骤 2: 手动登录（请在这一步手动输入用户名密码）")
        print("="*60)
        print("\n请在打开的浏览器中手动登录...")
        print("登录后按回车键继续...")
        input()
        
        print("\n" + "="*60)
        print("步骤 3: 导航到 Create Proposal Group")
        print("="*60)
        page.goto("https://csmstest.ncs.com.sg/UAT/app/consol_cs/details_pg.aspx")
        page.wait_for_load_state('networkidle')
        print("✓ 已到达 Create Proposal Group 页面")
        
        print("\n" + "="*60)
        print("步骤 4: 填写 Proposal # 并点击 GET CRM INFO")
        print("="*60)
        proposal_input = page.locator('#ctl00_ContentPlaceHolder1_txtProposalNo')
        if proposal_input.count() > 0:
            proposal_input.fill('OPP-111239')
            print("✓ 已填写 Proposal #")
            
            crm_btn = page.locator('#ctl00_ContentPlaceHolder1_btnInfo')
            if crm_btn.count() > 0:
                crm_btn.click()
                print("✓ 已点击 GET CRM INFO")
                print("等待 CRM 数据加载...")
                time.sleep(5)
        
        print("\n" + "="*60)
        print("步骤 5: 测试 Currency Code 下拉框")
        print("="*60)
        
        # 获取下拉框
        currency_select = page.locator('#ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode')
        
        if currency_select.count() > 0:
            print("✓ 找到 Currency Code 下拉框")
            
            # 检查当前值
            current = currency_select.input_value()
            print(f"  当前值：{current}")
            
            # 获取所有选项
            options = currency_select.locator('option')
            print(f"  可用选项：{options.count()} 个")
            for i in range(min(10, options.count())):
                opt = options.nth(i)
                print(f"    [{opt.input_value()}] {opt.inner_text()}")
            
            print("\n尝试方法 1: select_option('15')...")
            try:
                currency_select.select_option('15')
                time.sleep(2)
                new_val = currency_select.input_value()
                print(f"  结果值：{new_val}")
                if new_val == '15':
                    print("  ✓ 成功")
                else:
                    print("  ✗ 失败")
            except Exception as e:
                print(f"  ✗ 错误：{e}")
            
            print("\n按回车键尝试方法 2（JavaScript）...")
            input()
            
            print("\n尝试方法 2: JavaScript + __doPostBack...")
            result = page.evaluate("""() => {
                var elem = document.getElementById('ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode');
                if (!elem) return 'Element not found';
                
                var oldVal = elem.value;
                elem.value = '15';
                
                console.log('Old value:', oldVal, 'New value:', elem.value);
                
                if (oldVal !== elem.value) {
                    elem.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    if (typeof __doPostBack === 'function') {
                        __doPostBack(elem.id, '');
                        return 'Success - doPostBack called';
                    }
                    return 'Success - no doPostBack';
                }
                return 'Value not changed';
            }""")
            print(f"  结果：{result}")
            time.sleep(3)
            
            # 检查最终值
            final_val = currency_select.input_value()
            print(f"  最终值：{final_val}")
            
        else:
            print("✗ 未找到 Currency Code 下拉框")
        
        print("\n" + "="*60)
        print("测试完成")
        print("="*60)
        print("\n按回车键退出...")
        input()
        browser.close()

if __name__ == '__main__':
    test_real_page()
