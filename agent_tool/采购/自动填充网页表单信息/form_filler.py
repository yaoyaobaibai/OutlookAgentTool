import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import threading
from playwright.sync_api import sync_playwright
import pandas as pd


class ConfigManager:
    def __init__(self, config_file="form_config.json"):
        self.config_file = config_file
        self.fields = []
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.fields = data.get('fields', [])
            except Exception as e:
                print(f"加载配置失败：{e}")
                self.fields = []
        else:
            self.fields = []
    
    def save_config(self):
        data = {'fields': self.fields}
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_field(self, label, selector, value=""):
        self.fields.append({'label': label, 'selector': selector, 'value': value})
        self.save_config()
    
    def update_field(self, index, label, selector, value):
        if 0 <= index < len(self.fields):
            self.fields[index] = {'label': label, 'selector': selector, 'value': value}
            self.save_config()
    
    def remove_field(self, index):
        if 0 <= index < len(self.fields):
            self.fields.pop(index)
            self.save_config()
    
    def get_fields(self):
        return self.fields

class FieldEditorDialog:
    def __init__(self, parent, title, field_data=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.field_data = field_data
        self._create_widgets()
        
        if field_data:
            self.entry_label.insert(0, field_data.get('label', ''))
            self.entry_selector.insert(0, field_data.get('selector', ''))
            self.entry_value.insert(0, field_data.get('value', ''))
        
        self.dialog.wait_window()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="字段名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_label = ttk.Entry(main_frame, width=40)
        self.entry_label.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(main_frame, text="CSS 选择器:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_selector = ttk.Entry(main_frame, width=40)
        self.entry_selector.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(main_frame, text="默认值:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_value = ttk.Entry(main_frame, width=40)
        self.entry_value.grid(row=2, column=1, pady=5, padx=10)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="确定", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _on_ok(self):
        label = self.entry_label.get().strip()
        selector = self.entry_selector.get().strip()
        value = self.entry_value.get().strip()
        
        if not label or not selector:
            messagebox.showerror("错误", "字段名称和 CSS 选择器不能为空")
            return
        
        self.result = {'label': label, 'selector': selector, 'value': value}
        self.dialog.destroy()


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
        category_combo['values'] = (
            "Proposal Document", 
            "Contract", 
            "Supporting Document", 
            "Technical Specification", 
            "Financial Document", 
            "Other"
        )
        category_combo.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(main_frame, text="File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.file_path, width=45).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="浏览", command=self._browse_file).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.desc_text = tk.Text(main_frame, width=50, height=5)
        self.desc_text.grid(row=2, column=1, pady=5, padx=10)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=1, pady=20, sticky=tk.E)
        
        ttk.Button(btn_frame, text="确定", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
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
            'description': self.desc_text.get("1.0", tk.END).strip()
        }
        self.dialog.destroy()

class AttachmentManager:
    def __init__(self, config_file="attachment_config.json"):
        self.config_file = config_file
        self.attachments = []
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.attachments = data.get('attachments', [])
            except Exception as e:
                print(f"加载附件配置失败：{e}")
                self.attachments = []
        else:
            self.attachments = []
    
    def save_config(self):
        data = {'attachments': self.attachments}
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_attachment(self, category, file_path, description=""):
        self.attachments.append({
            'category': category,
            'file_path': file_path,
            'description': description
        })
        self.save_config()
    
    def update_attachment(self, index, category, file_path, description):
        if 0 <= index < len(self.attachments):
            self.attachments[index] = {
                'category': category,
                'file_path': file_path,
                'description': description
            }
            self.save_config()
    
    def remove_attachment(self, index):
        if 0 <= index < len(self.attachments):
            self.attachments.pop(index)
            self.save_config()
    
    def get_attachments(self):
        return self.attachments


class FormFillerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("表单自动填充工具 - Create Proposal Group")
        self.root.geometry("1000x750")
        
        self.config_manager = ConfigManager()
        self.attachment_manager = AttachmentManager()
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None
        self.is_running = False
        self.browser_choice = tk.StringVar(value="chrome")
        self.chrome_path = tk.StringVar(value=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        self.target_url = tk.StringVar(value="")
        self.excel_path = tk.StringVar(value="")
        
        # 登录信息
        self.username = tk.StringVar(value="")
        self.password = tk.StringVar(value="")
        self.auto_login = tk.BooleanVar(value=True)
        
        self._create_widgets()
        self._load_fields_to_ui()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 登录信息区域
        login_frame = ttk.LabelFrame(main_frame, text="登录信息", padding=10)
        login_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(login_frame, text="用户名:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(login_frame, textvariable=self.username, width=30).grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(login_frame, text="密码:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(login_frame, textvariable=self.password, show="*", width=30).grid(row=0, column=3, pady=5, padx=5, sticky=tk.W)
        
        ttk.Checkbutton(login_frame, text="自动登录", variable=self.auto_login).grid(row=0, column=4, pady=5, padx=20)
        
        # URL 和浏览器设置
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_frame, text="登录网址:").pack(side=tk.LEFT, padx=5)
        url_entry = ttk.Entry(url_frame, textvariable=self.target_url, width=60)
        url_entry.pack(side=tk.LEFT, padx=5)
        
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="浏览器:").pack(side=tk.LEFT, padx=5)
        
        browser_combo = ttk.Combobox(
            settings_frame, 
            textvariable=self.browser_choice,
            values=[
                ("chrome", "Google Chrome"),
                ("msedge", "Microsoft Edge"),
                ("chromium", "Chromium (需下载)")
            ],
            state="readonly",
            width=30
        )
        browser_combo.pack(side=tk.LEFT, padx=5)
        browser_combo.current(0)
        
        ttk.Label(settings_frame, text="Chrome 路径 (可选):").pack(side=tk.LEFT, padx=20)
        path_entry = ttk.Entry(settings_frame, textvariable=self.chrome_path, width=50)
        path_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(settings_frame, text="浏览", command=self._browse_chrome).pack(side=tk.LEFT, padx=5)
        
        excel_frame = ttk.Frame(main_frame)
        excel_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(excel_frame, text="Excel 文件:").pack(side=tk.LEFT, padx=5)
        self.entry_excel = ttk.Entry(excel_frame, textvariable=self.excel_path, width=60)
        self.entry_excel.pack(side=tk.LEFT, padx=5)
        ttk.Button(excel_frame, text="浏览", command=self._browse_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(excel_frame, text="清空", command=self._clear_excel).pack(side=tk.LEFT, padx=5)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.btn_start = ttk.Button(btn_frame, text="启动填充", command=self._start_filling)
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="添加字段", command=self._add_field).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="编辑字段", command=self._edit_field).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除字段", command=self._delete_field).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="刷新字段", command=self._refresh_fields).pack(side=tk.LEFT, padx=5)
        
        # 附件管理区域
        attachment_frame = ttk.LabelFrame(main_frame, text="附件上传管理", padding=10)
        attachment_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        attach_btn_frame = ttk.Frame(attachment_frame)
        attach_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(attach_btn_frame, text="添加附件", command=self._add_attachment).pack(side=tk.LEFT, padx=5)
        ttk.Button(attach_btn_frame, text="编辑附件", command=self._edit_attachment).pack(side=tk.LEFT, padx=5)
        ttk.Button(attach_btn_frame, text="删除附件", command=self._delete_attachment).pack(side=tk.LEFT, padx=5)
        
        columns_attach = ('category', 'file', 'description')
        self.attachment_tree = ttk.Treeview(attachment_frame, columns=columns_attach, show='headings', height=6)
        
        self.attachment_tree.heading('category', text='Category')
        self.attachment_tree.heading('file', text='File Path')
        self.attachment_tree.heading('description', text='Description')
        
        self.attachment_tree.column('category', width=150)
        self.attachment_tree.column('file', width=400)
        self.attachment_tree.column('description', width=300)
        
        scrollbar_attach = ttk.Scrollbar(attachment_frame, orient=tk.VERTICAL, command=self.attachment_tree.yview)
        self.attachment_tree.configure(yscrollcommand=scrollbar_attach.set)
        
        self.attachment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_attach.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.attachment_tree.bind('<Double-1>', lambda e: self._edit_attachment())
        
        # 加载附件列表
        self._load_attachments_to_ui()
        
        columns = ('label', 'selector', 'value')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
        
        self.tree.heading('label', text='字段名称')
        self.tree.heading('selector', text='CSS 选择器')
        self.tree.heading('value', text='默认值')
        
        self.tree.column('label', width=150)
        self.tree.column('selector', width=300)
        self.tree.column('value', width=300)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<Double-1>', lambda e: self._edit_field())
    
    def _browse_chrome(self):
        file_path = filedialog.askopenfilename(
            title="选择 Chrome 浏览器",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
            initialdir=r"C:\Program Files"
        )
        if file_path:
            self.chrome_path.set(file_path)
    
    def _browse_excel(self):
        file_path = filedialog.askopenfilename(
            title="选择 Excel 文件",
            filetypes=[("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        if file_path:
            self.excel_path.set(file_path)
    
    def _clear_excel(self):
        self.excel_path.set("")
    
    def _load_fields_to_ui(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for field in self.config_manager.get_fields():
            self.tree.insert('', tk.END, values=(
                field['label'],
                field['selector'],
                field['value']
            ))
    
    def _refresh_fields(self):
        self.config_manager.load_config()
        self._load_fields_to_ui()
    
    def _add_field(self):
        dialog = FieldEditorDialog(self.root, "添加字段")
        if dialog.result:
            self.config_manager.add_field(
                dialog.result['label'],
                dialog.result['selector'],
                dialog.result['value']
            )
            self._load_fields_to_ui()
    
    def _edit_field(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要编辑的字段")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        field_data = {
            'label': values[0],
            'selector': values[1],
            'value': values[2] if len(values) > 2 else ''
        }
        
        dialog = FieldEditorDialog(self.root, "编辑字段", field_data)
        if dialog.result:
            index = self.tree.index(selection[0])
            self.config_manager.update_field(
                index,
                dialog.result['label'],
                dialog.result['selector'],
                dialog.result['value']
            )
            self._load_fields_to_ui()
    
    def _delete_field(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要删除的字段")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的字段吗？"):
            index = self.tree.index(selection[0])
            self.config_manager.remove_field(index)
            self._load_fields_to_ui()
    
    def _load_attachments_to_ui(self):
        for item in self.attachment_tree.get_children():
            self.attachment_tree.delete(item)
        
        for attachment in self.attachment_manager.get_attachments():
            self.attachment_tree.insert('', tk.END, values=(
                attachment['category'],
                attachment['file_path'],
                attachment['description']
            ))
    
    def _add_attachment(self):
        dialog = AttachmentDialog(self.root, "添加附件")
        if dialog.result:
            self.attachment_manager.add_attachment(
                dialog.result['category'],
                dialog.result['file_path'],
                dialog.result['description']
            )
            self._load_attachments_to_ui()
    
    def _edit_attachment(self):
        selection = self.attachment_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的附件")
            return
        
        item = self.attachment_tree.item(selection[0])
        values = item['values']
        attachment_data = {
            'category': values[0],
            'file_path': values[1],
            'description': values[2] if len(values) > 2 else ''
        }
        
        dialog = AttachmentDialog(self.root, "编辑附件", attachment_data)
        if dialog.result:
            index = self.attachment_tree.index(selection[0])
            self.attachment_manager.update_attachment(
                index,
                dialog.result['category'],
                dialog.result['file_path'],
                dialog.result['description']
            )
            self._load_attachments_to_ui()
    
    def _delete_attachment(self):
        selection = self.attachment_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的附件")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的附件吗？"):
            index = self.attachment_tree.index(selection[0])
            self.attachment_manager.remove_attachment(index)
            self._load_attachments_to_ui()
    
    def _start_filling(self):
        if self.is_running:
            messagebox.showwarning("提示", "填充任务正在运行中")
            return
        
        fields = self.config_manager.get_fields()
        if not fields:
            messagebox.showwarning("提示", "请先添加要填充的字段")
            return
        
        excel_path = self.excel_path.get().strip()
        if excel_path:
            try:
                fields = self._load_excel_values(fields, excel_path)
            except Exception as e:
                messagebox.showerror("错误", f"读取 Excel 失败：{e}")
                return
        
        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self._fill_form, args=(fields,), daemon=True)
        thread.start()
    
    def _load_excel_values(self, fields, excel_path):
        df = pd.read_excel(excel_path)
        
        field_labels = {field['label']: field for field in fields}
        
        for _, row in df.iterrows():
            for col_name in df.columns:
                if col_name in field_labels:
                    value = row[col_name]
                    if pd.notna(value):
                        field_labels[col_name]['value'] = str(value)
                    else:
                        field_labels[col_name]['value'] = ""
        
        return fields
    
    def _fill_form(self, fields):
        try:
            self.playwright = sync_playwright().start()
            
            launch_args = {"headless": False}
            browser_type = self.browser_choice.get()
            
            if browser_type == "chromium":
                self.browser = self.playwright.chromium.launch(**launch_args)
            else:
                if self.chrome_path.get():
                    launch_args["executable_path"] = self.chrome_path.get()
                    print(f"使用指定路径：{self.chrome_path.get()}")
                else:
                    launch_args["channel"] = browser_type
                    print(f"使用浏览器：{browser_type}")
                
                self.browser = self.playwright.chromium.launch(**launch_args)
            
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            
            target_url = self.target_url.get().strip()
            if target_url:
                print(f"正在访问：{target_url}")
                self.page.goto(target_url)
                self.page.wait_for_load_state('networkidle')
                print("页面加载完成")
            else:
                print("未指定网址，请手动导航")
                self.page.wait_for_load_state('networkidle')
            
            self.page.wait_for_load_state('networkidle')
            
            # 如果启用了自动登录，执行登录操作
            if self.auto_login.get() and self.username.get().strip() and self.password.get().strip():
                print("\n正在执行自动登录...")
                try:
                    # 尝试查找并填写登录表单
                    # 常见的登录表单选择器
                    login_selectors = [
                        'input[name="username"]',
                        'input[name="userName"]',
                        'input[id="username"]',
                        'input[type="text"]',
                    ]
                    
                    password_selectors = [
                        'input[name="password"]',
                        'input[name="passwd"]',
                        'input[id="password"]',
                        'input[type="password"]',
                    ]
                    
                    submit_selectors = [
                        'input[type="submit"]',
                        'button[type="submit"]',
                        'button:has-text("Login")',
                        'button:has-text("Sign In")',
                        'input[value="Login"]',
                        'input[value="Sign In"]',
                    ]
                    
                    # 填写用户名
                    username_filled = False
                    for selector in login_selectors:
                        try:
                            username_field = self.page.locator(selector).first
                            if username_field.count() > 0:
                                username_field.fill(self.username.get().strip())
                                print(f"已填写用户名 (使用选择器：{selector})")
                                username_filled = True
                                break
                        except:
                            continue
                    
                    if not username_filled:
                        print("⚠️ 未找到用户名输入框，请手动登录")
                        self.page.wait_for_timeout(5000)
                    
                    # 填写密码
                    password_filled = False
                    for selector in password_selectors:
                        try:
                            password_field = self.page.locator(selector).first
                            if password_field.count() > 0:
                                password_field.fill(self.password.get().strip())
                                print(f"已填写密码 (使用选择器：{selector})")
                                password_filled = True
                                break
                        except:
                            continue
                    
                    if not password_filled:
                        print("⚠️ 未找到密码输入框")
                    
                    # 点击登录按钮
                    submit_clicked = False
                    for selector in submit_selectors:
                        try:
                            submit_btn = self.page.locator(selector).first
                            if submit_btn.count() > 0:
                                submit_btn.click()
                                print(f"已点击登录按钮 (使用选择器：{selector})")
                                submit_clicked = True
                                break
                        except:
                            continue
                    
                    if submit_clicked:
                        print("等待登录完成...")
                        self.page.wait_for_load_state('networkidle')
                        self.page.wait_for_timeout(2000)
                        print("登录完成")
                    else:
                        print("⚠️ 未找到登录按钮，请手动点击")
                        self.page.wait_for_timeout(3000)
                        
                except Exception as e:
                    print(f"登录过程出错：{e}")
                    print("请手动完成登录")
                    self.page.wait_for_timeout(5000)
            else:
                if not self.auto_login.get():
                    print("自动登录已禁用，请手动登录")
                elif not self.username.get().strip() or not self.password.get().strip():
                    print("用户名或密码为空，请手动登录")
                print("等待用户手动登录...")
                self.page.wait_for_timeout(5000)
            
            # 导航到 Create Proposal Group 页面
            print("\n正在导航到 Create Proposal Group 页面...")
            try:
                # 方法 1: 直接访问 URL
                create_pg_url = "https://csmstest.ncs.com.sg/UAT/app/consol_cs/details_pg.aspx"
                print(f"访问：{create_pg_url}")
                self.page.goto(create_pg_url)
                self.page.wait_for_load_state('networkidle')
                print("已到达 Create Proposal Group 页面")
            except Exception as e:
                print(f"导航失败：{e}")
                print("请手动导航到 Create Proposal Group 页面")
                self.page.wait_for_timeout(5000)
            
            # 等待页面完全加载
            self.page.wait_for_selector('#ctl00_ContentPlaceHolder1_txtProposalNo', state='visible', timeout=15000)
            print("Create Proposal Group 页面加载完成")
            
            # ========================================
            # 特殊字段处理（需要特殊操作的字段）
            # ========================================
            
            # 1. 处理 Proposal # 和 GET CRM INFO 按钮
            proposal_no_field = None
            for field in fields:
                if field['label'] == 'Proposal #':
                    proposal_no_field = field
                    break
            
            if proposal_no_field:
                print("\n>>> 步骤 1: 填写 Proposal # 并点击 GET CRM INFO")
                try:
                    # 填写 Proposal #
                    elem = self.page.locator(proposal_no_field['selector'])
                    if elem.count() > 0:
                        elem.wait_for(state='visible', timeout=5000)
                        elem.fill('')
                        elem.fill(proposal_no_field['value'])
                        print(f"  已填写 Proposal #: {proposal_no_field['value']}")
                        
                        # 点击 GET CRM INFO 按钮
                        crm_btn = self.page.locator('#ctl00_ContentPlaceHolder1_btnInfo')
                        if crm_btn.count() > 0:
                            print("  正在点击 GET CRM INFO 按钮...")
                            crm_btn.click()
                            
                            # 等待 CRM 数据加载完成（等待 Loading 消失）
                            print("  等待 CRM 数据加载...")
                            try:
                                # 等待 Loading 动画出现然后消失
                                self.page.wait_for_selector('#ctl00_ContentPlaceHolder1_upgProject', state='visible', timeout=5000)
                                self.page.wait_for_selector('#ctl00_ContentPlaceHolder1_upgProject', state='hidden', timeout=15000)
                                print("  ✓ CRM 数据加载完成")
                            except Exception as e:
                                print(f"  等待 CRM 加载：{e}")
                                self.page.wait_for_timeout(3000)
                        else:
                            print("  ⚠️ 未找到 GET CRM INFO 按钮")
                except Exception as e:
                    print(f"  ✗ 处理 Proposal # 失败：{e}")
            
            # 2. 处理 Date of Award（点击蓝色按钮，在打开的 Cal.aspx 页面中选择日期）
            date_award_field = None
            for field in fields:
                if field['label'] == 'Date of Award':
                    date_award_field = field
                    break
            
            if date_award_field:
                print("\n>>> 步骤 2: 选择 Date of Award")
                try:
                    # 处理日期格式（可能是 Excel 的 datetime 格式）
                    date_value = date_award_field['value']  # 可能是 "2026-07-22 00:00:00" 或 "01/15/2024"
                    
                    # 尝试解析日期
                    try:
                        # 如果是 Excel 的 datetime 格式
                        if '-' in date_value and ':' in date_value:
                            date_str = date_value.split(' ')[0]  # 取日期部分 "2026-07-22"
                            date_parts = date_str.split('-')
                            year, month, day = date_parts
                        elif '/' in date_value:
                            # 已经是 MM/DD/YYYY 格式
                            parts = date_value.split('/')
                            if len(parts) == 3:
                                month, day, year = parts
                            else:
                                raise ValueError("日期格式错误")
                        else:
                            # 尝试直接使用
                            month, day, year = '01', '01', '2024'
                        
                        print(f"  解析后的日期：{year}-{month}-{day}")
                        
                        # 直接填写日期到输入框（更可靠的方式）
                        date_input = self.page.locator('#ctl00_ContentPlaceHolder1_dtDateofAward_txtDate')
                        if date_input.count() > 0:
                            date_input.fill(f"{month}/{day}/{year}")
                            print(f"  ✓ 已填写日期：{month}/{day}/{year}")
                            
                            # 触发 change 事件
                            date_input.dispatch_event('change')
                            self.page.wait_for_timeout(500)
                        else:
                            print("  ✗ 未找到日期输入框")
                            
                    except Exception as e:
                        print(f"  ✗ 日期解析失败：{e}")
                        print(f"     原始值：{date_value}")
                        
                except Exception as e:
                    print(f"  ✗ 处理 Date of Award 失败：{e}")
            
            # 3. 处理 Priming Project Manager（弹窗搜索）
            pm_field = None
            for field in fields:
                if 'Project Manager' in field['label'] or 'Priming Project Manager' in field['label']:
                    pm_field = field
                    break
            
            if pm_field:
                print("\n>>> 步骤 3: 选择 Priming Project Manager")
                try:
                    login_id = pm_field['value']
                    if not login_id or not login_id.strip():
                        print("  ✗ LoginID 为空，跳过")
                    else:
                        # 查找放大镜按钮
                        pm_search_btn = self.page.locator('#ctl00_ContentPlaceHolder1_ucEmpSearch_txtUserName').first
                        
                        if pm_search_btn.count() > 0:
                            print(f"  点击搜索按钮，LoginID: {login_id}")
                            
                            # 点击按钮（不等待 popup，因为可能是 iframe 或新窗口）
                            pm_search_btn.click()
                            self.page.wait_for_timeout(2000)
                            
                            # 等待弹窗出现（尝试多种方式）
                            popup = None
                            
                            # 方式 1: 检查是否有 popup
                            try:
                                popup = self.page.wait_for_event('popup', timeout=3000)
                                print("  ✓ 弹窗已打开 (popup)")
                            except:
                                # 方式 2: 可能是 iframe
                                try:
                                    iframe = self.page.frame_locator('iframe[name*="popup"], iframe[id*="popup"]').first
                                    if iframe.count() > 0:
                                        popup = iframe
                                        print("  ✓ 弹窗已打开 (iframe)")
                                except:
                                    pass
                            
                            # 如果找不到弹窗，直接在主页面操作
                            if popup is None:
                                print("  ⚠️ 未检测到弹窗，在主页面查找...")
                                popup = self.page
                            
                            popup.wait_for_load_state('networkidle')
                            
                            # 在弹窗中输入 LoginID
                            login_input = popup.locator('#txtOAID')
                            if login_input.count() > 0:
                                login_input.fill(login_id)
                                print(f"  ✓ 已输入 LoginID: {login_id}")
                                
                                # 点击 Search 按钮
                                search_btn = popup.locator('input[type="submit"][value*="Search"]').first
                                if search_btn.count() > 0:
                                    search_btn.click()
                                    print("  ✓ 已点击 Search 按钮")
                                    popup.wait_for_timeout(2000)
                                    
                                    # 选择第一个结果
                                    first_row = popup.locator('table tr:nth-child(2)').first
                                    if first_row.count() > 0:
                                        first_row.click()
                                        print("  ✓ 已点击第一个搜索结果")
                                        
                                        # 点击 Select 按钮
                                        select_btn = popup.locator('input[type="submit"][value*="Select"]').first
                                        if select_btn.count() > 0:
                                            select_btn.click()
                                            print("  ✓ 已点击 Select 按钮")
                                            self.page.wait_for_timeout(1000)
                                        else:
                                            print("  ⚠️ 未找到 Select 按钮")
                                    else:
                                        print("  ✗ 未找到搜索结果")
                                else:
                                    print("  ✗ 未找到 Search 按钮")
                            else:
                                print("  ✗ 未找到 LoginID 输入框")
                                # 打印页面内容调试
                                try:
                                    content = popup.content()
                                    print(f"  页面内容预览：{content[:500]}")
                                except:
                                    pass
                        else:
                            print("  ✗ 未找到 Project Manager 搜索按钮")
                except Exception as e:
                    print(f"  ✗ 处理 Project Manager 失败：{e}")
                    import traceback
                    print(f"     错误详情：{traceback.format_exc()}")
            
            # ========================================
            # 处理其他普通字段
            # ========================================
            print("\n>>> 步骤 4: 填充其他表单字段")
            
            for field in fields:
                if self.is_running:
                    selector = field['selector']
                    value = field['value']
                    label = field['label']
                    
                    # 跳过已经特殊处理的字段
                    if label in ['Proposal #', 'Date of Award', 'Priming Project Manager']:
                        continue
                    
                    try:
                        element = self.page.locator(selector)
                        count = element.count()
                        
                        if count == 0:
                            print(f"跳过字段 '{label}' - 未找到元素 (选择器：{selector})")
                            continue
                        
                        element.wait_for(state='visible', timeout=5000)
                        
                        # 判断元素类型并处理
                        try:
                            tag_name = element.evaluate('el => el.tagName.toLowerCase()')
                            print(f"  处理字段 '{label}' ({tag_name}): {value}")
                            
                            if tag_name == 'select':
                                # 下拉框处理
                                print(f"    → 使用 select_option 选择：{value}")
                                try:
                                    element.select_option(value)
                                    print(f"  ✓ 已选择：{value}")
                                except Exception as e:
                                    print(f"  ⚠️ select_option 失败：{e}")
                                    # 尝试使用 JavaScript
                                    element.evaluate(f'el => {{ el.value = "{value}"; el.dispatchEvent(new Event("change")); }}')
                                    print(f"  ✓ 使用 JavaScript 设置成功")
                            elif selector.startswith('file:'):
                                # 文件上传处理
                                file_path = value
                                if os.path.exists(file_path):
                                    print(f"    → 上传文件：{file_path}")
                                    element.set_input_files(file_path)
                                    print(f"  ✓ 已上传文件")
                                else:
                                    print(f"  ✗ 文件不存在：{file_path}")
                            elif tag_name == 'input' or tag_name == 'textarea':
                                # 普通输入框处理
                                element.fill('')
                                element.fill(value)
                                print(f"  ✓ 已填充")
                            else:
                                # 其他元素类型，尝试点击或填充
                                try:
                                    element.fill('')
                                    element.fill(value)
                                    print(f"  ✓ 已填充")
                                except Exception as e:
                                    print(f"  ⚠️ 尝试填充失败：{e}")
                        except Exception as e:
                            print(f"  ✗ 处理字段失败：{e}")
                            # 尝试直接使用 JavaScript 设置值
                            try:
                                element.evaluate(f'el => {{ el.value = "{value}"; el.dispatchEvent(new Event("change")); }}')
                                print(f"  ✓ 使用 JavaScript 设置值成功")
                            except Exception as e2:
                                print(f"  ✗ JavaScript 设置值也失败：{e2}")
                        
                        self.page.wait_for_timeout(200)
                        
                    except Exception as e:
                        print(f"跳过字段 '{label}' - 错误：{e}")
            
            # 处理附件上传
            attachments = self.attachment_manager.get_attachments()
            if attachments:
                print(f"\n>>> 步骤 5: 处理 {len(attachments)} 个附件...")
                
                # 滚动到附件上传区域
                try:
                    attach_section = self.page.locator('fieldset').filter(has_text='Attachment').first
                    if attach_section.count() > 0:
                        attach_section.scroll_into_view_if_needed()
                        self.page.wait_for_timeout(800)
                        print("  已滚动到附件上传区域")
                except Exception as e:
                    print(f"  滚动到附件区域：{e}")
                
                for i, attachment in enumerate(attachments, 1):
                    print(f"\n  {'='*50}")
                    print(f"  处理附件 {i}:")
                    print(f"    文件路径：{attachment['file_path']}")
                    print(f"    Category: {attachment['category']}")
                    print(f"    Description: {attachment['description']}")
                    print(f"  {'='*50}")
                    
                    try:
                        # 1. 选择 Category（下拉框）
                        print(f"\n  [1/3] 选择 Category: {attachment['category']}")
                        category_found = False
                        
                        # 尝试多种选择器策略
                        category_patterns = [
                            f"select[id*='ddlAttachmentCategory_{i}']",
                            f"select[name*='AttachmentCategory_{i}']",
                            f"select[name*='category_{i}']",
                            f"select[id*='Category_{i}']",
                            # 更通用的选择器
                            f"select:nth-of-type({i})",
                            f"select[id*='Attachment_{i}']",
                        ]
                        
                        # 先尝试精确定位
                        for pattern in category_patterns:
                            try:
                                cat_elem = self.page.locator(pattern).first
                                if cat_elem.count() > 0:
                                    print(f"    找到 Category 下拉框：{pattern}")
                                    cat_elem.select_option(attachment['category'])
                                    print(f"    ✓ 已选择 Category: {attachment['category']}")
                                    category_found = True
                                    break
                            except Exception as e:
                                pass
                        
                        # 如果精确定位失败，尝试使用文本查找
                        if not category_found:
                            try:
                                # 查找包含 "Category" 标签
                                labels = self.page.locator('label')
                                for j in range(labels.count()):
                                    label = labels.nth(j)
                                    text = label.inner_text().lower()
                                    if 'category' in text:
                                        # 查找标签后面的下拉框
                                        cat_elem = label.locator('xpath=following::select[1]').first
                                        if cat_elem.count() > 0:
                                            cat_elem.select_option(attachment['category'])
                                            print(f"    ✓ 已选择 Category: {attachment['category']}")
                                            category_found = True
                                            break
                            except Exception as e:
                                print(f"    文本查找失败：{e}")
                        
                        if not category_found:
                            print(f"    ⚠️ 未找到 Category 下拉框，尝试所有 select 元素")
                            # 最后尝试：查找所有 select 元素
                            all_selects = self.page.locator('select')
                            for j in range(all_selects.count()):
                                sel = all_selects.nth(j)
                                try:
                                    sel.select_option(attachment['category'])
                                    print(f"    ✓ 在第 {j+1} 个 select 中成功选择")
                                    category_found = True
                                    break
                                except:
                                    continue
                        
                        # 2. 上传文件
                        print(f"\n  [2/3] 上传文件...")
                        file_found = False
                        
                        file_patterns = [
                            f"input[type='file'][id*='FileUpload_{i}']",
                            f"input[type='file'][name*='file_{i}']",
                            f"input[type='file'][id*='Attachment_{i}']",
                            f"input[type='file']:nth-of-type({i})",
                        ]
                        
                        for pattern in file_patterns:
                            try:
                                file_elem = self.page.locator(pattern).first
                                if file_elem.count() > 0:
                                    print(f"    找到文件上传框：{pattern}")
                                    if os.path.exists(attachment['file_path']):
                                        file_elem.set_input_files(attachment['file_path'])
                                        print(f"    ✓ 已上传文件：{attachment['file_path']}")
                                        file_found = True
                                    else:
                                        print(f"    ✗ 文件不存在：{attachment['file_path']}")
                                    break
                            except Exception as e:
                                pass
                        
                        if not file_found:
                            print(f"    ⚠️ 未找到文件上传框")
                        
                        # 3. 填写 Description
                        print(f"\n  [3/3] 填写 Description...")
                        desc_found = False
                        
                        desc_patterns = [
                            f"textarea[id*='txtAttachmentDesc_{i}']",
                            f"textarea[name*='AttachmentDesc_{i}']",
                            f"textarea[name*='desc_{i}']",
                            f"textarea[id*='Description_{i}']",
                            f"textarea:nth-of-type({i})",
                        ]
                        
                        for pattern in desc_patterns:
                            try:
                                desc_elem = self.page.locator(pattern).first
                                if desc_elem.count() > 0:
                                    print(f"    找到 Description 输入框：{pattern}")
                                    desc_elem.fill(attachment['description'])
                                    print(f"    ✓ 已填写 Description")
                                    desc_found = True
                                    break
                            except Exception as e:
                                pass
                        
                        if not desc_found:
                            print(f"    ⚠️ 未找到 Description 输入框")
                        
                        self.page.wait_for_timeout(500)
                        
                    except Exception as e:
                        print(f"    ✗ 处理附件 {i} 失败：{e}")
                        import traceback
                        print(f"       错误详情：{traceback.format_exc()}")
                
                print(f"\n{'='*50}")
                print("附件处理完成")
                print(f"{'='*50}")
            else:
                print("\n>>> 没有附件需要上传")
            
            print("\n表单填充完成，未执行提交操作")
            
            self.root.after(0, lambda: messagebox.showinfo("成功", "表单填充完成！"))
            
        except Exception as e:
            import traceback
            error_msg = f"填充失败：{str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        if self.is_running:
            if not messagebox.askyesno("确认", "填充任务正在运行，确定要退出吗？"):
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


if __name__ == "__main__":
    app = FormFillerApp()
    app.run()
