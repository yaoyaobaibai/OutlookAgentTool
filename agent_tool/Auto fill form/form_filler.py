"""
Form Filler - Multi-workflow GUI application for automated form filling.

This module provides a tkinter GUI that allows users to:
  - Select from available workflows (discovered from workflows/ directory)
  - View dynamic field definitions loaded from the selected workflow config
  - Configure browser, credentials, and data source settings
  - Execute workflows using the WorkflowEngine
  - View real-time execution logs
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import tempfile
import threading
import time
import urllib.request
import logging

from workflow_manager import WorkflowManager, WorkflowNotFoundError
from workflow_engine import WorkflowEngine
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

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
      - Log panel
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("表单自动填充工具 - 多工作流")
        self.root.geometry("1100x850")

        # Workflow management
        self.workflow_manager = WorkflowManager()

        # Playwright resources
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None
        self._edge_proc = None
        self.engine = None
        self.is_running = False

        # Configuration variables
        self.browser_choice = tk.StringVar(value="msedge")
        self.chrome_path = tk.StringVar(
            value=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
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
        browser_combo.current(1)

        ttk.Label(settings_frame, text="浏览器路径 (可选):").grid(
            row=0, column=2, sticky=tk.W, pady=5, padx=(15, 5)
        )
        path_entry = ttk.Entry(settings_frame, textvariable=self.chrome_path, width=45)
        path_entry.grid(row=0, column=3, pady=5, padx=5, sticky=tk.W)
        ttk.Button(settings_frame, text="浏览", command=self._browse_browser).grid(
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
        # 7. Log Panel
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
        """Update login URL and field list for current workflow."""
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
    # Browser Utilities
    # ------------------------------------------------------------------

    def _browse_browser(self):
        edge_dir = r"C:\Program Files (x86)\Microsoft\Edge\Application"
        if not os.path.exists(edge_dir):
            edge_dir = r"C:\Program Files"
        file_path = filedialog.askopenfilename(
            title="选择浏览器程序",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")],
            initialdir=edge_dir
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

    def _find_edge_path(self):
        """Locate the installed Microsoft Edge executable.

        Returns the first existing candidate path, or ``None`` if Edge
        cannot be found anywhere.
        """
        candidates = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\Application\msedge.exe"),
        ]
        for p in candidates:
            if os.path.isfile(p):
                return p
        return None

    def _launch_browser(self):
        """Bare-launch a NEW Edge instance and connect over CDP.

        Playwright's `chromium.launch` injects `--disable-*` automation flags
        that trigger Microsoft's login block, so we launch Edge manually via
        subprocess.Popen with only the minimal debugging flags (same approach
        as recorder.py) and connect over CDP. A FIXED user-data-dir
        (formfiller_edge_profile) keeps the login session across runs.
        """
        self.playwright = sync_playwright().start()

        browser_choice = self.browser_choice.get()
        if browser_choice == "chromium":
            # "chromium" channel has no pre-built launcher — fall through to Playwright launch
            edge_path = None
        else:
            # Prefer the user-specified path, then fall back to a detected Edge install
            edge_path = self.chrome_path.get().strip() or self._find_edge_path()

        if edge_path and os.path.isfile(edge_path):
            cdp_port = 9222
            user_data_dir = os.path.join(tempfile.gettempdir(), "formfiller_edge_profile")
            os.makedirs(user_data_dir, exist_ok=True)

            self._log(f"[i] 正在以裸启动方式打开 Edge: {edge_path}")
            proc = subprocess.Popen(
                [edge_path,
                 f"--remote-debugging-port={cdp_port}",
                 f"--user-data-dir={user_data_dir}",
                 "--no-first-run",
                 "--no-default-browser-check"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            self._edge_proc = proc  # keep reference so we can close it on exit

            # Wait for CDP ready
            ready = False
            for _ in range(30):
                try:
                    urllib.request.urlopen(f"http://localhost:{cdp_port}/json/version", timeout=2)
                    ready = True
                    break
                except Exception:
                    time.sleep(0.5)
            if not ready:
                self._log("[!] Edge CDP 启动超时")
                return

            self._log(f"[✓] Edge 已启动 (端口 {cdp_port})，正在连接...")
            self._log("[i] 首次运行请先在弹出的 Edge 中登录 Acubuy，登录态将保存在 formfiller_edge_profile 中")
            self.browser = self.playwright.chromium.connect_over_cdp(f"http://localhost:{cdp_port}")
            self.context = self.browser.contexts[0] if self.browser.contexts else self.browser.new_context()
            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = self.context.new_page()
            return

        self._log("[!] 未找到 Edge，回退到 Playwright 直接启动")

        # Fallback: legacy Playwright launch path (only when Edge not found
        # or browser_choice is "chromium").
        launch_args = {"headless": False}
        # Chromium-based browsers advertise automation via --enable-automation;
        # removing it helps Microsoft's login policy accept the fresh instance.
        launch_args["ignore_default_args"] = ["--enable-automation"]

        if browser_choice == "chromium":
            self.browser = self.playwright.chromium.launch(**launch_args)
        else:
            if self.chrome_path.get().strip():
                launch_args["executable_path"] = self.chrome_path.get().strip()
                self._log(f"  使用自定义路径: {self.chrome_path.get().strip()}")
            else:
                launch_args["channel"] = browser_choice
                self._log(f"  使用浏览器渠道: {browser_choice}")

            self.browser = self.playwright.chromium.launch(**launch_args)

        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    # ------------------------------------------------------------------
    # Value Builder (Excel)
    # ------------------------------------------------------------------

    def _build_field_values(self, config):
        """Build a dict of field_name -> value from the selected Excel file.

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
                df = pd.read_excel(excel_path, dtype=str)
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

        # --- Auto-construct attachment path from folder + Order value ---
        # Business rule: Excel "Attachment File" holds a FOLDER; the actual file is
        # "<folder>\<Order value>.pdf". Only applied when both fields are present.
        folder = field_values.get("Attachment File", "").strip()
        order_val = field_values.get("Order", "").strip()
        if folder and order_val:
            attachment_path = os.path.join(folder, f"{order_val}.pdf")
            field_values["Attachment File"] = attachment_path
            self._log(f"[i] 附件路径已自动构建: {attachment_path}")
            if not os.path.isfile(attachment_path):
                self._log(f"[!] 附件文件不存在: {attachment_path}")
                self._log("[!] 请确认该文件夹中存在文件名为「<Order值>.pdf」的文件，例如 6000017449.pdf")

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
            self.root.after(0, lambda err=e: self._on_execution_error(err))
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
            # Terminate the bare-launched Edge we spawned — kill the whole tree
            if getattr(self, "_edge_proc", None):
                try:
                    subprocess.run(
                        ["taskkill", "/PID", str(self._edge_proc.pid), "/T", "/F"],
                        capture_output=True,
                        timeout=10,
                    )
                except Exception:
                    try:
                        self._edge_proc.kill()
                    except Exception:
                        pass
                self._edge_proc = None
            self.root.after(0, self.root.destroy)

        threading.Thread(target=cleanup, daemon=True).start()


# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    app = FormFillerApp()
    app.run()
