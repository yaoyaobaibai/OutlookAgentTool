"""
Form Filler - Multi-workflow GUI application for automated form filling.

This module provides a tkinter GUI that allows users to:
  - Select from available workflows (discovered from workflows/ directory)
  - View dynamic field definitions loaded from the selected workflow config
  - Configure browser, credentials, and data source settings
  - Execute workflows using the WorkflowEngine
  - Manage attachments for upload
  - View real-time execution logs
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import threading
import logging

from workflow_manager import WorkflowManager, WorkflowNotFoundError
from workflow_engine import WorkflowEngine
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

# ==============================================================================
# Attachment Dialog (kept from original for backward compatibility)
# ==============================================================================

class AttachmentDialog:
    """Dialog for adding/editing an attachment entry."""

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

        ttk.Label(main_frame, text="类别:").grid(row=0, column=0, sticky=tk.W, pady=5)
        category_combo = ttk.Combobox(main_frame, textvariable=self.category, width=50, state="readonly")
        category_combo['values'] = (
            "建议书",
            "合同",
            "支持文件",
            "技术规范",
            "财务文件",
            "其他"
        )
        category_combo.grid(row=0, column=1, pady=5, padx=10)

        ttk.Label(main_frame, text="文件:").grid(row=1, column=0, sticky=tk.W, pady=5)
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.file_path, width=45).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="浏览", command=self._browse_file).pack(side=tk.LEFT, padx=5)

        ttk.Label(main_frame, text="描述:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.desc_text = tk.Text(main_frame, width=50, height=5)
        self.desc_text.grid(row=2, column=1, pady=5, padx=10)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=1, pady=20, sticky=tk.E)

        ttk.Button(btn_frame, text="确定", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择附件文件",
            filetypes=[("所有文件", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        if file_path:
            self.file_path.set(file_path)

    def _on_ok(self):
        if not self.category.get().strip():
            messagebox.showerror("错误", "请选择类别")
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


# ==============================================================================
# Attachment Manager (kept from original for backward compatibility)
# ==============================================================================

class AttachmentManager:
    """Manages attachment entries loaded from and persisted to a JSON file."""

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


# ==============================================================================
# Main Application
# ==============================================================================

class FormFillerApp:
    """Multi-workflow form filler GUI application.

    Layout (top to bottom):
      - Workflow selector
      - Login settings (URL, username, password, auto-login)
      - Browser settings (browser type, chrome path)
      - Data source (Excel file selection)
      - Action buttons (Start / Stop)
      - Fields treeview (from workflow config)
      - Attachment management (add/edit/delete)
      - Log panel
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("表单自动填充工具 - 多工作流")
        self.root.geometry("1100x850")

        # Workflow management
        self.workflow_manager = WorkflowManager()
        self.attachment_manager = AttachmentManager()

        # Playwright resources
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None
        self.engine = None
        self.is_running = False

        # Configuration variables
        self.browser_choice = tk.StringVar(value="chrome")
        self.chrome_path = tk.StringVar(
            value=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        self.target_url = tk.StringVar(value="")
        self.excel_path = tk.StringVar(value="")

        # Login variables
        self.username = tk.StringVar(value="")
        self.password = tk.StringVar(value="")
        self.auto_login = tk.BooleanVar(value=True)

        # Current workflow tracking
        self._current_workflow_name = ""

        self._check_backward_compatibility()
        self._create_widgets()
        self._init_workflow_selector()
        self._load_attachments_to_ui()

    # ------------------------------------------------------------------
    # Backward Compatibility
    # ------------------------------------------------------------------

    def _check_backward_compatibility(self):
        """Warn about legacy form_config.json and suggest migration."""
        legacy = "form_config.json"
        if os.path.exists(legacy):
            self._log(
                f"[!] 检测到遗留配置文件 '{legacy}'。"
                f" 建议将字段配置迁移到 workflow JSON 格式。"
            )

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ================================================================
        # 1. Workflow Selector (top)
        # ================================================================
        selector_frame = ttk.Frame(main_frame)
        selector_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(selector_frame, text="工作流:").pack(side=tk.LEFT, padx=5)
        self.workflow_combo = ttk.Combobox(
            selector_frame,
            state="readonly",
            width=60
        )
        self.workflow_combo.pack(side=tk.LEFT, padx=5)
        self.workflow_combo.bind('<<ComboboxSelected>>', self._on_workflow_changed)

        # ================================================================
        # 2. Login Settings
        # ================================================================
        login_frame = ttk.LabelFrame(main_frame, text="登录设置", padding=10)
        login_frame.pack(fill=tk.X, pady=5)

        # Row 0: Login URL
        ttk.Label(login_frame, text="登录网址:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        ttk.Entry(login_frame, textvariable=self.target_url, width=80).grid(
            row=0, column=1, pady=5, padx=5, columnspan=4, sticky=tk.W
        )

        # Row 1: Username / Password / Auto-login
        ttk.Label(login_frame, text="用户名:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        ttk.Entry(login_frame, textvariable=self.username, width=30).grid(
            row=1, column=1, pady=5, padx=5, sticky=tk.W
        )
        ttk.Label(login_frame, text="密码:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(10, 5))
        ttk.Entry(login_frame, textvariable=self.password, show="*", width=30).grid(
            row=1, column=3, pady=5, padx=5, sticky=tk.W
        )
        ttk.Checkbutton(login_frame, text="自动登录", variable=self.auto_login).grid(
            row=1, column=4, pady=5, padx=10
        )

        # ================================================================
        # 3. Browser Settings
        # ================================================================
        settings_frame = ttk.LabelFrame(main_frame, text="浏览器设置", padding=10)
        settings_frame.pack(fill=tk.X, pady=5)

        ttk.Label(settings_frame, text="浏览器:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
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
        browser_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        browser_combo.current(0)

        ttk.Label(settings_frame, text="Chrome 路径 (可选):").grid(
            row=0, column=2, sticky=tk.W, pady=5, padx=(15, 5)
        )
        path_entry = ttk.Entry(settings_frame, textvariable=self.chrome_path, width=45)
        path_entry.grid(row=0, column=3, pady=5, padx=5, sticky=tk.W)
        ttk.Button(settings_frame, text="浏览", command=self._browse_chrome).grid(
            row=0, column=4, pady=5, padx=5
        )

        # ================================================================
        # 4. Data Source (Excel)
        # ================================================================
        excel_frame = ttk.LabelFrame(main_frame, text="数据源", padding=10)
        excel_frame.pack(fill=tk.X, pady=5)

        ttk.Label(excel_frame, text="Excel 文件:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(excel_frame, textvariable=self.excel_path, width=70).pack(side=tk.LEFT, padx=5)
        ttk.Button(excel_frame, text="浏览", command=self._browse_excel).pack(side=tk.LEFT, padx=2)
        ttk.Button(excel_frame, text="清空", command=self._clear_excel).pack(side=tk.LEFT, padx=2)

        # ================================================================
        # 5. Action Buttons (Start / Stop)
        # ================================================================
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=8)

        self.btn_start = ttk.Button(
            btn_frame, text="▶ 启动工作流", command=self._start_execution
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_stop = ttk.Button(
            btn_frame, text="■ 停止", command=self._stop_execution, state=tk.DISABLED
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        # ================================================================
        # 6. Fields Treeview (from workflow config)
        # ================================================================
        field_frame = ttk.LabelFrame(main_frame, text="字段列表", padding=5)
        field_frame.pack(fill=tk.BOTH, expand=False, pady=3)

        columns = ('label', 'selector', 'type', 'required')
        self.tree = ttk.Treeview(field_frame, columns=columns, show='headings', height=8)

        self.tree.heading('label', text='字段名称')
        self.tree.heading('selector', text='CSS 选择器')
        self.tree.heading('type', text='类型')
        self.tree.heading('required', text='必填')

        self.tree.column('label', width=160, minwidth=120)
        self.tree.column('selector', width=380, minwidth=200)
        self.tree.column('type', width=100, minwidth=80)
        self.tree.column('required', width=80, minwidth=60)

        scrollbar_tree = ttk.Scrollbar(field_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_tree.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_tree.pack(side=tk.RIGHT, fill=tk.Y)

        # ================================================================
        # 7. Attachment Management
        # ================================================================
        attach_frame = ttk.LabelFrame(main_frame, text="附件管理", padding=5)
        attach_frame.pack(fill=tk.BOTH, expand=True, pady=3)

        attach_btn_frame = ttk.Frame(attach_frame)
        attach_btn_frame.pack(fill=tk.X, pady=3)

        ttk.Button(attach_btn_frame, text="添加附件", command=self._add_attachment).pack(side=tk.LEFT, padx=3)
        ttk.Button(attach_btn_frame, text="编辑附件", command=self._edit_attachment).pack(side=tk.LEFT, padx=3)
        ttk.Button(attach_btn_frame, text="删除附件", command=self._delete_attachment).pack(side=tk.LEFT, padx=3)

        columns_attach = ('category', 'file', 'description')
        self.attachment_tree = ttk.Treeview(
            attach_frame, columns=columns_attach, show='headings', height=4
        )

        self.attachment_tree.heading('category', text='类别')
        self.attachment_tree.heading('file', text='文件路径')
        self.attachment_tree.heading('description', text='描述')

        self.attachment_tree.column('category', width=140)
        self.attachment_tree.column('file', width=400)
        self.attachment_tree.column('description', width=280)

        scrollbar_attach = ttk.Scrollbar(attach_frame, orient=tk.VERTICAL, command=self.attachment_tree.yview)
        self.attachment_tree.configure(yscrollcommand=scrollbar_attach.set)

        self.attachment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_attach.pack(side=tk.RIGHT, fill=tk.Y)

        self.attachment_tree.bind('<Double-1>', lambda e: self._edit_attachment())

        # ================================================================
        # 8. Log Panel
        # ================================================================
        log_frame = ttk.LabelFrame(main_frame, text="执行日志", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=3)

        log_inner = ttk.Frame(log_frame)
        log_inner.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_inner, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_scrollbar = ttk.Scrollbar(log_inner, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # ------------------------------------------------------------------
    # Workflow Selector
    # ------------------------------------------------------------------

    def _init_workflow_selector(self):
        """Populate the workflow combo box with discovered workflows."""
        workflows = self.workflow_manager.list_workflows()
        if workflows:
            display_names = [w["display_name"] for w in workflows]
            self.workflow_combo['values'] = display_names

            # Restore previously selected workflow
            saved = self.workflow_manager.get_current_workflow()
            if saved:
                for i, w in enumerate(workflows):
                    if w["name"] == saved:
                        self.workflow_combo.current(i)
                        self._on_workflow_changed()
                        break
            else:
                self.workflow_combo.current(0)
                self._on_workflow_changed()
        else:
            self.workflow_combo['values'] = ["(未发现工作流)"]
            self.workflow_combo.current(0)
            self._log("[!] 在 workflows/ 目录下未发现工作流。")

    def _on_workflow_changed(self, event=None):
        """Handle workflow selection change — update all UI elements."""
        workflows = self.workflow_manager.list_workflows()
        idx = self.workflow_combo.current()
        if idx < 0 or idx >= len(workflows):
            return

        workflow = workflows[idx]
        name = workflow["name"]
        display = workflow["display_name"]

        try:
            self.workflow_manager.set_current_workflow(name)
            self._current_workflow_name = name
        except WorkflowNotFoundError as e:
            self._log(f"[!] 工作流错误: {e}")
            return

        # Update start button text to match the workflow
        self.btn_start.config(text=f"▶ 启动: {display}")

        # Reload the UI for the selected workflow
        self._update_ui_for_workflow()

    def _update_ui_for_workflow(self):
        """Update login URL, field list, and attachments for current workflow."""
        name = self._current_workflow_name
        if not name:
            return

        try:
            config = self.workflow_manager.load_workflow(name)
        except (WorkflowNotFoundError, Exception) as e:
            self._log(f"[!] 加载工作流失败 '{name}': {e}")
            return

        # Update login URL
        login_url = config.get("login", {}).get("url", "")
        self.target_url.set(login_url)

        # Reload fields from workflow config
        self._load_fields_from_workflow()

    def _load_fields_from_workflow(self):
        """Load fields from current workflow config into the field treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        fields = self.workflow_manager.get_field_definitions()
        for field in fields:
            self.tree.insert('', tk.END, values=(
                field.label,
                field.selector,
                field.field_type,
                "是" if field.required else "否"
            ))

    # ------------------------------------------------------------------
    # Attachment Management
    # ------------------------------------------------------------------

    def _load_attachments_to_ui(self):
        """Refresh the attachment treeview from the attachment manager."""
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
            messagebox.showwarning("提示", "请先选择要编辑的附件")
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
            messagebox.showwarning("提示", "请先选择要删除的附件")
            return

        if messagebox.askyesno("确认", "确定要删除选中的附件吗？"):
            index = self.attachment_tree.index(selection[0])
            self.attachment_manager.remove_attachment(index)
            self._load_attachments_to_ui()

    # ------------------------------------------------------------------
    # Browser Utilities
    # ------------------------------------------------------------------

    def _browse_chrome(self):
        file_path = filedialog.askopenfilename(
            title="选择 Chrome 浏览器",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")],
            initialdir=r"C:\Program Files"
        )
        if file_path:
            self.chrome_path.set(file_path)

    def _browse_excel(self):
        file_path = filedialog.askopenfilename(
            title="选择 Excel 文件",
            filetypes=[("Excel 文件", "*.xlsx *.xlsm *.xls"), ("所有文件", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        if file_path:
            self.excel_path.set(file_path)

    def _clear_excel(self):
        self.excel_path.set("")

    def _launch_browser(self):
        """Launch Playwright browser based on current settings."""
        self.playwright = sync_playwright().start()

        launch_args = {"headless": False}
        browser_type = self.browser_choice.get()

        if browser_type == "chromium":
            self.browser = self.playwright.chromium.launch(**launch_args)
        else:
            if self.chrome_path.get().strip():
                launch_args["executable_path"] = self.chrome_path.get().strip()
                self._log(f"  使用自定义路径: {self.chrome_path.get().strip()}")
            else:
                launch_args["channel"] = browser_type
                self._log(f"  使用浏览器渠道: {browser_type}")

            self.browser = self.playwright.chromium.launch(**launch_args)

        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    # ------------------------------------------------------------------
    # Value Builder (Excel + attachments)
    # ------------------------------------------------------------------

    def _build_field_values(self, config):
        """Build a dict of field_name -> value from Excel and attachment data.

        First tries to load values from the selected Excel file.
        If no Excel file is provided, returns an empty dict (engine uses
        default values from the workflow config).

        Returns:
            dict: Field values keyed by field label.
        """
        field_values = {}

        excel_path = self.excel_path.get().strip()
        if excel_path and os.path.exists(excel_path):
            try:
                import pandas as pd
                df = pd.read_excel(excel_path)
                if df.empty:
                    self._log("[!] Excel 文件为空 — 未加载任何值。")
                    return field_values

                # First row is treated as field label -> value mapping
                row = df.iloc[0]
                for col_name in df.columns:
                    val = row[col_name]
                    if pd.notna(val):
                        field_values[str(col_name)] = str(val)
                self._log(f"[✓] 已从 Excel 加载 {len(field_values)} 个值。")
            except Exception as e:
                self._log(f"[!] 读取 Excel 失败: {e}")
        else:
            self._log("[i] 未选择 Excel 文件 — 使用默认字段值。")

        # Attachments: add as a special field that the engine can handle
        attachments = self.attachment_manager.get_attachments()
        if attachments:
            field_values["__attachments__"] = attachments
            self._log(f"[i] 包含 {len(attachments)} 个附件")

        return field_values

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _log(self, message):
        """Append a message to the log panel (thread-safe via root.after)."""

        def _append():
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.log_text.configure(state=tk.DISABLED)

        self.root.after(0, _append)

    # ------------------------------------------------------------------
    # Engine Callbacks
    # ------------------------------------------------------------------

    def _on_field_start(self, field_name):
        self._log(f">>> 处理字段: {field_name}")

    def _on_field_end(self, field_name, result):
        status = "✓ 成功" if result.get("success") else "✗ 失败"
        self._log(f"  {field_name}: {status} — {result.get('message', '')}")

    def _on_engine_error(self, field_or_step, error):
        self._log(f"  错误 ({field_or_step}): {error}")

    # ------------------------------------------------------------------
    # Execution Control
    # ------------------------------------------------------------------

    def _start_execution(self):
        """Start the workflow execution in a background thread."""
        if self.is_running:
            messagebox.showwarning("提示", "工作流正在运行中")
            return

        name = self._current_workflow_name
        if not name:
            messagebox.showwarning("提示", "请先选择工作流")
            return

        # Ensure we have workflow config
        try:
            config = self.workflow_manager.load_workflow(name)
        except Exception as e:
            messagebox.showerror("错误", f"加载工作流失败：{e}")
            return

        # Inject the GUI's login URL into the workflow config if provided
        url = self.target_url.get().strip()
        if url:
            if "login" in config and config["login"]:
                config["login"]["url"] = url
            if "navigation" in config and config["navigation"]:
                for step in config["navigation"]:
                    if step.get("action") == "goto":
                        step["url"] = url

        # Check if the workflow has fields (login-only workflows may have none)
        fields = self.workflow_manager.get_field_definitions()
        if not fields:
            self._log("[i] 当前工作流没有表单字段，仅执行登录和导航步骤")

        self._log(f"\n{'='*55}")
        self._log(f"开始执行工作流: {name}")
        self._log(f"{'='*55}\n")

        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)

        # Launch browser and execute in background thread
        self._log("[i] 正在启动浏览器...")
        thread = threading.Thread(
            target=self._run_engine_thread,
            args=(config,),
            daemon=True
        )
        thread.start()

    def _run_engine_thread(self, config):
        """Background thread: launch browser, create engine, execute workflow."""
        try:
            self._launch_browser()
            self._log("[✓] 浏览器启动成功。\n")

            # Create engine
            self.engine = WorkflowEngine(self.page, config)
            self.engine.register_callback("on_field_start", self._on_field_start)
            self.engine.register_callback("on_field_end", self._on_field_end)
            self.engine.register_callback("on_error", self._on_engine_error)

            # Build field values from Excel (if selected)
            field_values = self._build_field_values(config)

            # Execute
            self._log("[i] 正在执行工作流...\n")
            result = self.engine.execute(
                username=self.username.get().strip(),
                password=self.password.get().strip(),
                field_values=field_values
            )

            self.root.after(0, lambda: self._on_execution_complete(result))

        except Exception as e:
            self._log(f"\n[!] 引擎错误: {e}")
            import traceback
            self._log(traceback.format_exc())
            self.root.after(0, lambda: self._on_execution_error(e))
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.btn_stop.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))

    def _on_execution_complete(self, result):
        """Called in the main thread when execution finishes successfully."""
        self._log(f"\n{'='*55}")
        self._log("执行完成。")
        if isinstance(result, dict):
            self._log(f"  总计:  {result.get('total', '?')}")
            self._log(f"  成功:     {result.get('success', '?')}")
            self._log(f"  失败: {result.get('failed', '?')}")
            if result.get("error"):
                self._log(f"  错误:  {result['error']}")
        self._log(f"{'='*55}\n")

        if isinstance(result, dict) and result.get("failed", 0) == 0 and result.get("total", 0) > 0:
            messagebox.showinfo("成功", "工作流执行完成！")
        elif isinstance(result, dict) and result.get("error"):
            messagebox.showerror("错误", f"工作流执行失败：{result['error']}")
        else:
            messagebox.showinfo("信息", "工作流执行完毕（详情请查看日志）。")

    def _on_execution_error(self, error):
        """Called in the main thread on an unhandled execution error."""
        messagebox.showerror("错误", f"执行失败：{error}")

    def _stop_execution(self):
        """Request the engine to stop after the current field."""
        if self.engine and self.is_running:
            self._log("\n[i] 已请求停止 — 将在当前字段处理后停止...\n")
            self.engine.stop()
            self.btn_stop.config(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Cleanup & Main Loop
    # ------------------------------------------------------------------

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()

    def _on_closing(self):
        if self.is_running:
            if not messagebox.askyesno("确认", "工作流正在运行，确定退出吗？"):
                return

        self.is_running = False

        def cleanup():
            try:
                if self.engine:
                    self.engine.stop()
            except Exception:
                pass
            try:
                if self.browser:
                    self.browser.close()
            except Exception:
                pass
            try:
                if self.playwright:
                    self.playwright.stop()
            except Exception:
                pass
            self.root.after(0, self.root.destroy)

        threading.Thread(target=cleanup, daemon=True).start()


# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    app = FormFillerApp()
    app.run()
