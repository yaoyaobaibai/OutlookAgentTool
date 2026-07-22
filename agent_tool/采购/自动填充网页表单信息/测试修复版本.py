"""
测试修复版本的简化脚本
用于验证 4 个关键问题的修复：
1. Selling Price Currency Code 下拉框
2. Date of Award 日期选择器
3. Priming Project Manager 弹窗搜索
4. 附件上传
"""

from playwright.sync_api import sync_playwright
import time

def test_currency_dropdown():
    """测试 1: 下拉框选择"""
    print("\n" + "="*60)
    print("测试 1: Selling Price Currency Code 下拉框")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 访问测试页面
        page.goto("https://csmstest.ncs.com.sg/UAT/app/consol_cs/details_pg.aspx")
        page.wait_for_load_state('networkidle')
        
        # 先填写 Proposal # 并点击 GET CRM INFO
        proposal_input = page.locator('#ctl00_ContentPlaceHolder1_txtProposalNo')
        if proposal_input.count() > 0:
            proposal_input.fill('P12345')
            print("✓ 已填写 Proposal #")
            
            crm_btn = page.locator('#ctl00_ContentPlaceHolder1_btnInfo')
            if crm_btn.count() > 0:
                crm_btn.click()
                print("✓ 已点击 GET CRM INFO")
                time.sleep(3)  # 等待 CRM 加载
        
        # 测试下拉框
        currency_select = page.locator('#ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode')
        if currency_select.count() > 0:
            tag_name = currency_select.evaluate('el => el.tagName.toLowerCase()')
            print(f"元素类型：{tag_name}")
            
            if tag_name == 'select':
                currency_select.select_option('USD')
                print("✓ 成功选择 USD")
            else:
                print(f"✗ 不是 select 元素，类型：{tag_name}")
        else:
            print("✗ 未找到 Currency Code 下拉框")
        
        time.sleep(3)
        browser.close()

def test_date_picker():
    """测试 2: 日期选择器"""
    print("\n" + "="*60)
    print("测试 2: Date of Award 日期选择器")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto("https://csmstest.ncs.com.sg/UAT/app/consol_cs/details_pg.aspx")
        page.wait_for_load_state('networkidle')
        
        # 点击日期选择按钮
        date_btn = page.locator('#ctl00_ContentPlaceHolder1_dtDateofAward_btnCall')
        if date_btn.count() > 0:
            print("✓ 找到日期选择按钮")
            
            with page.expect_popup() as popup_info:
                date_btn.click()
                print("✓ 已点击按钮，等待弹窗...")
            
            cal_page = popup_info.value
            cal_page.wait_for_load_state('networkidle')
            print("✓ 日历页面已打开")
            
            # 查找年份选择框
            year_select = cal_page.locator('select[id*="ddlYear"]').first
            if year_select.count() > 0:
                print("✓ 找到年份选择框")
                year_select.select_option('2024')
                print("✓ 已选择 2024 年")
            
            # 查找月份选择框
            month_select = cal_page.locator('select[id*="ddlMonth"]').first
            if month_select.count() > 0:
                print("✓ 找到月份选择框")
                month_select.select_option('01')
                print("✓ 已选择 01 月")
            
            # 查找日期（例如 15 号）
            day_link = cal_page.locator('a:text("15")').first
            if day_link.count() > 0:
                day_link.click()
                print("✓ 已点击 15 号")
            else:
                print("✗ 未找到日期 15")
        else:
            print("✗ 未找到日期选择按钮")
        
        time.sleep(3)
        browser.close()

def test_project_manager():
    """测试 3: Project Manager 弹窗搜索"""
    print("\n" + "="*60)
    print("测试 3: Priming Project Manager 弹窗搜索")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto("https://csmstest.ncs.com.sg/UAT/app/consol_cs/details_pg.aspx")
        page.wait_for_load_state('networkidle')
        
        # 查找放大镜按钮
        pm_btn = page.locator('input[id*="ucEmpSearch"][id*="txtUserName"]').first
        if pm_btn.count() == 0:
            pm_btn = page.locator('input[id*="txtUserName"]').first
        
        if pm_btn.count() > 0:
            print("✓ 找到 Project Manager 搜索按钮")
            
            with page.expect_popup() as popup_info:
                pm_btn.click()
                print("✓ 已点击按钮，等待弹窗...")
            
            popup = popup_info.value
            popup.wait_for_load_state('networkidle')
            print("✓ 搜索弹窗已打开")
            
            # 输入 LoginID
            login_input = popup.locator('#txtOAID')
            if login_input.count() > 0:
                login_input.fill('lin.zu')
                print("✓ 已输入 LoginID: lin.zu")
                
                # 点击 Search
                search_btn = popup.locator('input[type="submit"][value*="Search"]').first
                if search_btn.count() > 0:
                    search_btn.click()
                    print("✓ 已点击 Search 按钮")
                    popup.wait_for_timeout(2000)
                    
                    # 查找第一个结果
                    first_row = popup.locator('table tr:nth-child(2)').first
                    if first_row.count() > 0:
                        first_row.click()
                        print("✓ 已点击第一个结果")
                        
                        # 点击 Select
                        select_btn = popup.locator('input[type="submit"][value*="Select"]').first
                        if select_btn.count() > 0:
                            select_btn.click()
                            print("✓ 已点击 Select 按钮")
                        else:
                            print("✗ 未找到 Select 按钮")
                    else:
                        print("✗ 未找到搜索结果")
                else:
                    print("✗ 未找到 Search 按钮")
            else:
                print("✗ 未找到 LoginID 输入框")
        else:
            print("✗ 未找到 Project Manager 搜索按钮")
        
        time.sleep(3)
        browser.close()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("FormFiller v1.3 修复版本测试")
    print("="*60)
    print("\n请选择要测试的项目：")
    print("1. 测试 Currency Code 下拉框")
    print("2. 测试 Date of Award 日期选择器")
    print("3. 测试 Project Manager 弹窗搜索")
    print("4. 运行所有测试")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == '1':
        test_currency_dropdown()
    elif choice == '2':
        test_date_picker()
    elif choice == '3':
        test_project_manager()
    elif choice == '4':
        test_currency_dropdown()
        test_date_picker()
        test_project_manager()
    else:
        print("无效的选项")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
