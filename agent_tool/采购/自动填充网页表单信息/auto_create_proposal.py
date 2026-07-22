import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from playwright.sync_api import sync_playwright, expect
import threading
import os
from datetime import datetime


class AutoCreateProposalApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Create Proposal Group 自动化工具")
        self.root.geometry("900x700")
        
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None
        self.is_running = False
        
        # 配置变量
        self.browser_choice = tk.StringVar(value="chrome")
        self.chrome_path = tk.StringVar(value=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        self.login_url = tk.StringVar(value="")
        
        # 登录信息
        self.username = tk.StringVar(value="")
        self.password = tk.StringVar(value="")
        
        # Proposal 信息
        self.proposal_number = tk.StringVar(value="")
        self.crm_info_loaded = tk.BooleanVar(value=False)
        self.cust_ref_no = tk.StringVar(value="")
        self.proposal_value = tk.StringVar(value="")
        self.currency_code = tk.StringVar(value="")
        self.date_of_award = tk.StringVar(value="")
        self.priming_project_manager_id = tk.StringVar(value="")
        
        # 附件信息 - 支持多个附件
        self.attachments = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建带滚动条的画布
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 1. 浏览器设置
        settings_frame = ttk.LabelFrame(scrollable_frame, text="浏览器设置", padding=10)
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="登录网址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        url_entry = ttk.Entry(settings_frame, textvariable=self.login_url, width=80)
        url_entry.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(settings_frame, text="浏览器:").grid(row=1, column=0, sticky=tk.W, pady=5)
        browser_combo = ttk.Combobox(
            settings_frame, 
            textvariable=self.browser_choice,
            values=[("chrome", "Google Chrome"), ("msedge", "Microsoft Edge"), ("chromium", "Chromium")],
            state="readonly",
            width=30
        )
        browser_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        browser_combo.current(0)
        
        ttk.Label(settings_frame, text="Chrome 路径:").grid(row=2, column=0, sticky=tk.W, pady=5)
        path_entry = ttk.Entry(settings_frame, textvariable=self.chrome_path, width=60)
        path_entry.grid(row=2, column=1, pady=5, padx=10)
        ttk.Button(settings_frame, text="浏览", command=self._browse_chrome).grid(row=2, column=2, pady=5, padx=5)
        
        # 2. 登录信息
        login_frame = ttk.LabelFrame(scrollable_frame, text="登录信息", padding=10)
        login_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(login_frame, text="用户名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(login_frame, textvariable=self.username, width=40).grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(login_frame, text="密码:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(login_frame, textvariable=self.password, show="*").grid(row=1, column=1, pady=5, padx=10)
        
        # 3. Proposal 信息
        proposal_frame = ttk.LabelFrame(scrollable_frame, text="Proposal 信息", padding=10)
        proposal_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(proposal_frame, text="*Proposal #:", foreground="red").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(proposal_frame, textvariable=self.proposal_number, width=40).grid(row=0, column=1, pady=5, padx=10)
        ttk.Button(proposal_frame, text="GET CRM INFO", command=self._load_crm_info).grid(row=0, column=2, pady=5, padx=5)
        
        ttk.Label(proposal_frame, text="CRM 信息加载状态:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.crm_status_label = ttk.Label(proposal_frame, text="未加载", foreground="gray")
        self.crm_status_label.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(proposal_frame, text="*Cust Ref. No:", foreground="red").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(proposal_frame, textvariable=self.cust_ref_no, width=40).grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(proposal_frame, text="*Proposal/Contract Value:", foreground="red").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(proposal_frame, textvariable=self.proposal_value, width=40).grid(row=3, column=1, pady=5, padx=10)
        
        ttk.Label(proposal_frame, text="*Selling Price Currency Code:", foreground="red").grid(row=4, column=0, sticky=tk.W, pady=5)
        currency_combo = ttk.Combobox(proposal_frame, textvariable=self.currency_code, width=38, state="readonly")
        currency_combo['values'] = ("USD", "EUR", "CNY", "GBP", "JPY", "AUD", "CAD", "CHF", "HKD", "SGD", "KRW", "INR", "BRL", "MXN", "ZAR")
        currency_combo.grid(row=4, column=1, pady=5, padx=10)
        
        ttk.Label(proposal_frame, text="*Date of Award:", foreground="red").grid(row=5, column=0, sticky=tk.W, pady=5)
        date_frame = ttk.Frame(proposal_frame)
        date_frame.grid(row=5, column=1, sticky=tk.W, pady=5)
        ttk.Entry(date_frame, textvariable=self.date_of_award, width=25).grid(row=0, column=0)
        ttk.Button(date_frame, text="📅 选择日期", command=self._select_date).grid(row=0, column=1, padx=5)
        
        ttk.Label(proposal_frame, text="*Priming Project Manager:", foreground="red").grid(row=6, column=0, sticky=tk.W, pady=5)
        pm_frame = ttk.Frame(proposal_frame)
        pm_frame.grid(row=6, column=1, sticky=tk.W, pady=5)
        ttk.Entry(pm_frame, textvariable=self.priming_project_manager_id, width=25).grid(row=0, column=0)
        ttk.Button(pm_frame, text="🔍 搜索", command=self._search_project_manager).grid(row=0, column=1, padx=5)
        
        # 4. 附件管理
        attachment_frame = ttk.LabelFrame(scrollable_frame, text="附件管理", padding=10)
        attachment_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 附件列表
        columns = ('category', 'file', 'description')
        self.attachment_tree = ttk.Treeview(attachment_frame, columns=columns, show='headings', height=8)
        self.attachment_tree.heading('category', text='Category')
        self.attachment_tree.heading('file', text='File Path')
        self.attachment_tree.heading('description', text='Description')
        self.attachment_tree.column('category', width=150)
        self.attachment_tree.column('file', width=300)
        self.attachment_tree.column('description', width=300)
        self.attachment_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 附件操作按钮
        attach_btn_frame = ttk.Frame(attachment_frame)
        attach_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(attach_btn_frame, text="添加附件", command=self._add_attachment).pack(side=tk.LEFT, padx=5)
        ttk.Button(attach_btn_frame, text="编辑附件", command=self._edit_attachment).pack(side=tk.LEFT, padx=5)
        ttk.Button(attach_btn_frame, text="删除附件", command=self._delete_attachment).pack(side=tk.LEFT, padx=5)
        
        # 5. 控制按钮
        control_frame = ttk.Frame(scrollable_frame)
        control_frame.pack(fill=tk.X, pady=20)
        
        self.btn_start = ttk.Button(control_frame, text="🚀 开始执行自动化流程", command=self._start_automation)
        self.btn_start.pack(side=tk.LEFT, padx=5, pady=10)
        
        ttk.Button(control_frame, text="停止", command=self._stop_automation).pack(side=tk.LEFT, padx=5, pady=10)
        
        # 日志区域
        log_frame = ttk.LabelFrame(scrollable_frame, text="执行日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=15, width=100, state=tk.DISABLED)
        scrollbar_log = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar_log.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_log.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _browse_chrome(self):
        file_path = filedialog.askopenfilename(
            title="选择 Chrome 浏览器",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
            initialdir=r"C:\Program Files"
        )
        if file_path:
            self.chrome_path.set(file_path)
    
    def _log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _load_crm_info(self):
        if not self.proposal_number.get().strip():
            messagebox.showwarning("警告", "请先输入 Proposal #")
            return
        
        self._log(f"正在加载 CRM 信息 for Proposal #: {self.proposal_number.get()}")
        # 这里可以添加实际的 CRM 加载逻辑
        # 目前只是标记为已加载
        self.crm_info_loaded.set(True)
        self.crm_status_label.config(text="已加载 ✓", foreground="green")
        messagebox.showinfo("提示", "CRM 信息加载完成！\n（实际使用时请实现具体的 CRM 加载逻辑）")
    
    def _select_date(self):
        # 创建一个简单的日期选择对话框
        date_dialog = tk.Toplevel(self.root)
        date_dialog.title("选择日期")
        date_dialog.transient(self.root)
        date_dialog.grab_set()
        
        ttk.Label(date_dialog, text="选择 Award Date:").pack(pady=10)
        
        # 年份选择
        year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(date_dialog, textvariable=year_var, width=10)
        year_combo['values'] = [str(y) for y in range(2020, 2031)]
        year_combo.pack(pady=5)
        
        # 月份选择
        month_var = tk.StringVar(value=str(datetime.now().month).zfill(2))
        month_combo = ttk.Combobox(date_dialog, textvariable=month_var, width=10)
        month_combo['values'] = [str(m).zfill(2) for m in range(1, 13)]
        month_combo.pack(pady=5)
        
        # 日期选择
        day_var = tk.StringVar(value=str(datetime.now().day).zfill(2))
        day_combo = ttk.Combobox(date_dialog, textvariable=day_var, width=10)
        day_combo['values'] = [str(d).zfill(2) for d in range(1, 32)]
        day_combo.pack(pady=5)
        
        def on_select():
            date = f"{month_var.get()}/{day_var.get()}/{year_var.get()}"
            self.date_of_award.set(date)
            self._log(f"选择日期：{date}")
            date_dialog.destroy()
        
        ttk.Button(date_dialog, text="确定", command=on_select).pack(pady=10)
        ttk.Button(date_dialog, text="取消", command=date_dialog.destroy).pack(pady=5)
    
    def _search_project_manager(self):
        if not self.priming_project_manager_id.get().strip():
            messagebox.showwarning("警告", "请先输入 LoginID")
            return
        
        self._log(f"正在搜索 Project Manager: {self.priming_project_manager_id.get()}")
        # 模拟搜索和选择第一个结果
        messagebox.showinfo("提示", "在实际实现中，这里会：\n1. 弹出搜索窗口\n2. 输入 LoginID\n3. 点击 Search\n4. 选择第一个结果并点击 Select")
        self._log("Project Manager 选择完成（模拟）")
    
    def _add_attachment(self):
        dialog = AttachmentDialog(self.root, "添加附件")
        if dialog.result:
            self.attachments.append(dialog.result)
            self.attachment_tree.insert('', tk.END, values=(
                dialog.result['category'],
                dialog.result['file_path'],
                dialog.result['description']
            ))
            self._log(f"添加附件：{dialog.result['file_path']}")
    
    def _edit_attachment(self):
        selection = self.attachment_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的附件")
            return
        
        item = self.attachment_tree.item(selection[0])
        values = item['values']
        current_data = {
            'category': values[0],
            'file_path': values[1],
            'description': values[2]
        }
        
        dialog = AttachmentDialog(self.root, "编辑附件", current_data)
        if dialog.result:
            index = self.attachment_tree.index(selection[0])
            self.attachments[index] = dialog.result
            self.attachment_tree.delete(selection[0])
            self.attachment_tree.insert('', index, values=(
                dialog.result['category'],
                dialog.result['file_path'],
                dialog.result['description']
            ))
            self._log(f"更新附件：{dialog.result['file_path']}")
    
    def _delete_attachment(self):
        selection = self.attachment_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的附件")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的附件吗？"):
            index = self.attachment_tree.index(selection[0])
            self.attachments.pop(index)
            self.attachment_tree.delete(selection[0])
            self._log("删除附件")
    
    def _start_automation(self):
        if self.is_running:
            messagebox.showwarning("警告", "自动化流程正在运行中")
            return
        
        # 验证必填字段
        if not self.login_url.get().strip():
            messagebox.showerror("错误", "请输入登录网址")
            return
        
        if not self.username.get().strip() or not self.password.get().strip():
            messagebox.showerror("错误", "请输入用户名和密码")
            return
        
        if not self.proposal_number.get().strip():
            messagebox.showerror("错误", "请输入 Proposal #")
            return
        
        if not self.cust_ref_no.get().strip():
            messagebox.showerror("错误", "请输入 Cust Ref. No")
            return
        
        if not self.proposal_value.get().strip():
            messagebox.showerror("错误", "请输入 Proposal/Contract Value")
            return
        
        if not self.currency_code.get().strip():
            messagebox.showerror("错误", "请选择 Selling Price Currency Code")
            return
        
        if not self.date_of_award.get().strip():
            messagebox.showerror("错误", "请选择 Date of Award")
            return
        
        if not self.priming_project_manager_id.get().strip():
            messagebox.showerror("错误", "请输入 Priming Project Manager LoginID")
            return
        
        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._run_automation, daemon=True)
        thread.start()
    
    def _stop_automation(self):
        if self.is_running:
            if messagebox.askyesno("确认", "确定要停止自动化流程吗？"):
                self.is_running = False
                self._log("用户请求停止自动化流程...")
        else:
            self._log("自动化流程未运行")
    
    def _run_automation(self):
        try:
            self._log("=" * 60)
            self._log("开始执行自动化流程")
            self._log("=" * 60)
            
            # 启动浏览器
            self._log("正在启动浏览器...")
            self.playwright = sync_playwright().start()
            
            launch_args = {"headless": False}
            browser_type = self.browser_choice.get()
            
            if browser_type == "chromium":
                self.browser = self.playwright.chromium.launch(**launch_args)
            else:
                if self.chrome_path.get():
                    launch_args["executable_path"] = self.chrome_path.get()
                    self._log(f"使用 Chrome 路径：{self.chrome_path.get()}")
                else:
                    launch_args["channel"] = browser_type
                
                self.browser = self.playwright.chromium.launch(**launch_args)
            
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            
            # 步骤 1: 登录页面
            self._log("步骤 1: 访问登录页面...")
            self.page.goto(self.login_url.get().strip())
            self.page.wait_for_load_state('networkidle')
            self._log("登录页面加载完成")
            
            # 等待用户手动登录（因为登录页面可能有验证码或其他安全机制）
            self._log("请输入用户名和密码进行登录...")
            messagebox.showinfo("提示", "请手动完成登录操作，然后点击确定继续")
            
            # 步骤 2: 导航到 PROJECT COST SHEET > Create Proposal Group
            self._log("步骤 2: 导航到 PROJECT COST SHEET > Create Proposal Group...")
            
            # 点击 PROJECT COST SHEET 菜单（根据 HTML 结构，这是第二个菜单项，索引为 1）
            try:
                # 找到 PROJECT COST SHEET 菜单项并点击
                project_cost_menu = self.page.locator('td:has-text("PROJECT COST SHEET")').first
                if project_cost_menu.count() > 0:
                    project_cost_menu.click()
                    self.page.wait_for_timeout(500)
                    self._log("已点击 PROJECT COST SHEET 菜单")
                else:
                    self._log("⚠️ 未找到 PROJECT COST SHEET 菜单，请手动点击")
            except Exception as e:
                self._log(f"点击 PROJECT COST SHEET 菜单失败：{e}")
            
            # 点击 Create Proposal Group 子菜单
            try:
                create_pg_link = self.page.locator('text=Create Proposal Group').first
                if create_pg_link.count() > 0:
                    create_pg_link.click()
                    self.page.wait_for_load_state('networkidle')
                    self._log("已点击 Create Proposal Group")
                else:
                    self._log("⚠️ 未找到 Create Proposal Group 链接，请手动点击")
            except Exception as e:
                self._log(f"点击 Create Proposal Group 失败：{e}")
            
            # 等待页面加载完成
            self.page.wait_for_selector('#ctl00_ContentPlaceHolder1_txtProposalNo', state='visible', timeout=10000)
            self._log("Create Proposal Group 页面加载完成")
            
            # 步骤 3: 填写 Proposal # 并点击 GET CRM INFO
            self._log("步骤 3: 填写 Proposal # 并点击 GET CRM INFO...")
            proposal_no_field = self.page.locator('#ctl00_ContentPlaceHolder1_txtProposalNo')
            proposal_no_field.fill(self.proposal_number.get().strip())
            self._log(f"已填写 Proposal #: {self.proposal_number.get()}")
            
            # 点击 GET CRM INFO 按钮
            crm_btn = self.page.locator('#ctl00_ContentPlaceHolder1_btnInfo')
            crm_btn.click()
            self._log("已点击 GET CRM INFO 按钮")
            
            # 等待 CRM 信息加载完成（等待 Loading 消失）
            try:
                self.page.wait_for_selector('#ctl00_ContentPlaceHolder1_upgProject', state='hidden', timeout=15000)
                self._log("CRM 信息加载完成")
            except Exception as e:
                self._log(f"等待 CRM 加载超时：{e}")
            
            # 步骤 4: 填写其他字段
            self._log("步骤 4: 填写其他字段...")
            
            # 填写 Cust Ref. No
            cust_ref_field = self.page.locator('#ctl00_ContentPlaceHolder1_txtCustRefNo')
            cust_ref_field.fill(self.cust_ref_no.get().strip())
            self._log(f"已填写 Cust Ref. No: {self.cust_ref_no.get()}")
            
            # 填写 Proposal/Contract Value
            contract_value_field = self.page.locator('#ctl00_ContentPlaceHolder1_txtContractValue')
            contract_value_field.fill(self.proposal_value.get().strip())
            self._log(f"已填写 Proposal/Contract Value: {self.proposal_value.get()}")
            
            # 选择 Selling Price Currency Code
            currency_field = self.page.locator('#ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode')
            currency_field.select_option(self.currency_code.get().strip())
            self._log(f"已选择 Currency Code: {self.currency_code.get()}")
            
            # 步骤 5: 选择 Date of Award
            self._log("步骤 5: 选择 Date of Award...")
            date_field = self.page.locator('#ctl00_ContentPlaceHolder1_dtDateofAward_txtDate')
            date_field.fill(self.date_of_award.get().strip())
            self._log(f"已填写 Date of Award: {self.date_of_award.get()}")
            
            # 步骤 6: 选择 Priming Project Manager
            self._log("步骤 6: 选择 Priming Project Manager...")
            
            # 等待弹窗并处理
            try:
                # 点击放大镜按钮（需要先找到 PM 输入框并点击）
                pm_button = self.page.locator('input[id*="txtUserName"]')
                if pm_button.count() == 0:
                    # 如果没有直接找到，尝试其他方式
                    pm_button = self.page.locator('button:has-text("Search")').first
                
                # 设置预期弹窗
                with self.page.expect_popup() as popup_info:
                    pm_button.click()
                
                popup = popup_info.value
                self._log("员工搜索弹窗已打开")
                
                # 在弹窗中输入 LoginID
                login_id_field = popup.locator('#txtOAID')
                login_id_field.fill(self.priming_project_manager_id.get().strip())
                self._log(f"已输入 LoginID: {self.priming_project_manager_id.get()}")
                
                # 点击 Search 按钮
                search_btn = popup.locator('input[type="submit"][value*="Search"]')
                search_btn.click()
                self._log("已点击 Search 按钮")
                
                # 等待搜索结果
                popup.wait_for_load_state('networkidle')
                
                # 选择第一个结果并点击 Select
                first_result = popup.locator('table tr').nth(1)  # 第一行通常是表头，所以选第二行
                if first_result.count() > 0:
                    first_result.click()
                    self._log("已选择第一个搜索结果")
                
                # 点击 Select 按钮
                select_btn = popup.locator('input[type="submit"][value*="Select"]')
                if select_btn.count() > 0:
                    select_btn.click()
                    self._log("已点击 Select 按钮")
                else:
                    # 如果没有 Select 按钮，可能点击行就自动选择了
                    self._log("点击行后自动选择")
                
                # 等待弹窗关闭
                self.page.wait_for_timeout(1000)
                
            except Exception as e:
                self._log(f"选择 Project Manager 失败：{e}")
                self._log("⚠️ 请手动选择 Project Manager")
            
            # 步骤 7: 上传附件（如果 create pg.html 页面有附件上传功能）
            # 注意：根据提供的 HTML，当前页面没有显示附件上传区域
            # 如果实际页面有附件上传，需要根据实际 HTML 添加代码
            if self.attachments:
                self._log("步骤 7: 上传附件...")
                for i, attachment in enumerate(self.attachments, 1):
                    self._log(f"  处理附件 {i}: {attachment['file_path']}")
                    self._log(f"    Category: {attachment['category']}")
                    self._log(f"    Description: {attachment['description']}")
                    # 注意：实际页面中附件上传的 HTML 结构需要根据实际情况添加
                    self._log(f"    ⚠️ 附件上传功能需要根据实际页面 HTML 添加代码")
            else:
                self._log("步骤 7: 没有附件需要上传")
            
            # 步骤 8: 点击 Create 按钮
            self._log("步骤 8: 点击 Create 按钮...")
            create_btn = self.page.locator('#ctl00_ContentPlaceHolder1_btnInsert')
            self._log("⚠️ 请在确认所有信息无误后，手动点击 Create 按钮")
            # 如果需要自动点击，取消下面这行的注释
            # create_btn.click()
            # self._log("已点击 Create 按钮")
            
            self._log("=" * 60)
            self._log("自动化流程执行完成！")
            self._log("=" * 60)
            
            self.root.after(0, lambda: messagebox.showinfo("完成", "自动化流程执行完成！\n\n请检查页面上的信息，确认无误后手动点击 Create 按钮。"))
            
        except Exception as e:
            import traceback
            error_msg = f"自动化流程失败：{str(e)}\n\n{traceback.format_exc()}"
            self._log(error_msg)
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        if self.is_running:
            if not messagebox.askyesno("确认", "自动化流程正在运行，确定要退出吗？"):
                return
        
        self.is_running = False
        
        def cleanup():
            try:
                if self.browser:
                    self.browser.close()
                if self.playwright:
                    self.playwright.stop()
            except Exception as e:
                print(f"清理资源时出错：{e}")
            finally:
                self.root.after(0, self.root.destroy)
        
        import threading
        threading.Thread(target=cleanup, daemon=True).start()


class AttachmentDialog:
    def __init__(self, parent, title, attachment_data=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.attachment_data = attachment_data
        
        self.category = tk.StringVar(value="")
        self.file_path = tk.StringVar(value="")
        self.description = tk.StringVar(value="")
        
        self._create_widgets()
        
        if attachment_data:
            self.category.set(attachment_data.get('category', ''))
            self.file_path.set(attachment_data.get('file_path', ''))
            self.description.set(attachment_data.get('description', ''))
        
        self.dialog.wait_window()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Category:").grid(row=0, column=0, sticky=tk.W, pady=5)
        category_combo = ttk.Combobox(main_frame, textvariable=self.category, width=50, state="readonly")
        category_combo['values'] = ("Proposal Document", "Contract", "Supporting Document", "Technical Specification", "Financial Document", "Other")
        category_combo.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(main_frame, text="File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.file_path, width=45).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="浏览", command=self._browse_file).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=5)
        desc_text = tk.Text(main_frame, width=50, height=5)
        desc_text.grid(row=2, column=1, pady=5, padx=10)
        
        def set_desc():
            self.description.set(desc_text.get("1.0", tk.END).strip())
        
        ttk.Button(main_frame, text="确定", command=lambda: [set_desc(), self._on_ok()]).grid(row=3, column=1, pady=20, sticky=tk.E)
        ttk.Button(main_frame, text="取消", command=self.dialog.destroy).grid(row=3, column=1, pady=20, sticky=tk.W, padx=10)
    
    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择附件文件",
            filetypes=[("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        if file_path:
            self.file_path.set(file_path)
    
    def _on_ok(self):
        if not self.category.get().strip():
            messagebox.showerror("错误", "请选择 Category")
            return
        
        if not self.file_path.get().strip():
            messagebox.showerror("错误", "请选择文件")
            return
        
        if not os.path.exists(self.file_path.get()):
            messagebox.showerror("错误", "文件不存在")
            return
        
        self.result = {
            'category': self.category.get().strip(),
            'file_path': self.file_path.get().strip(),
            'description': self.description.get().strip()
        }
        self.dialog.destroy()


if __name__ == "__main__":
    app = AutoCreateProposalApp()
    app.run()
