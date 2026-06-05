"""
用户交互 GUI - 邮件确认和附件管理窗口
"""
import os
import logging
import threading
from typing import List, Callable, Optional
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

logger = logging.getLogger(__name__)


class EmailConfirmWindow:
    """邮件确认窗口"""
    
    def __init__(self, email_info: dict, on_confirm: Callable, on_ignore: Callable):
        """
        初始化确认窗口
        
        Args:
            email_info: 邮件信息字典
            on_confirm: 确认回调函数
            on_ignore: 忽略回调函数
        """
        self.email_info = email_info
        self.on_confirm = on_confirm
        self.on_ignore = on_ignore
        
        self.root = None
        self.selected_attachments = []
        self.attachment_listbox = None
        # 附件顺序列表：存储原始索引
        self.attachment_order = []
    
    def show(self):
        """显示窗口"""
        self.root = tk.Tk()
        self.root.title("邮件检测 - 请确认")
        self.root.geometry("550x650")
        self.root.resizable(True, True)
        self.root.minsize(500, 550)
        
        # 设置窗口图标（如果有）
        try:
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass
        
        self._create_widgets()
        
        # 窗口居中
        self._center_window()
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.root.mainloop()
    
    def _create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== 邮件信息区域 =====
        info_frame = ttk.LabelFrame(main_frame, text="邮件信息", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 发件人
        ttk.Label(info_frame, text="发件人:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=self.email_info.get('sender_name', '未知')).grid(
            row=0, column=1, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=f"<{self.email_info.get('sender_email', '')}>", 
                 foreground='gray').grid(row=0, column=2, sticky=tk.W, pady=2)
        
        # 接收时间
        ttk.Label(info_frame, text="接收时间:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=2)
        received_time = self.email_info.get('received_time', '')
        if hasattr(received_time, 'strftime'):
            time_str = received_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = str(received_time)
        ttk.Label(info_frame, text=time_str).grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=2)
        
        # 主题
        ttk.Label(info_frame, text="主题:", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=2)
        subject_label = ttk.Label(info_frame, text=self.email_info.get('subject', '(无主题)'))
        subject_label.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=2)
        
        # ===== 附件列表区域（可排序）=====
        attach_frame = ttk.LabelFrame(main_frame, text="附件列表（可拖拽排序，勾选需要处理的附件）", padding="10")
        attach_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 左右布局：列表 + 排序按钮
        list_container = ttk.Frame(attach_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # 附件列表
        list_frame = ttk.Frame(list_container)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建Listbox（可多选）
        self.attachment_listbox = tk.Listbox(
            list_frame, 
            selectmode=tk.MULTIPLE,
            height=8
        )
        self.attachment_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.attachment_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.attachment_listbox.config(yscrollcommand=scrollbar.set)
        
        # 排序按钮（右侧）
        order_btn_frame = ttk.Frame(list_container)
        order_btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        ttk.Button(order_btn_frame, text="↑ 上移", width=8, command=self._move_up).pack(pady=5)
        ttk.Button(order_btn_frame, text="↓ 下移", width=8, command=self._move_down).pack(pady=5)
        ttk.Label(order_btn_frame, text="排序后PDF\n按此顺序生成", foreground='gray', 
                 font=('Arial', 9)).pack(pady=10)
        
        # 初始化附件列表
        attachments = self.email_info.get('attachments', [])
        self.attachment_order = list(range(len(attachments)))  # 原始顺序
        
        if not attachments:
            self.attachment_listbox.insert(tk.END, "无附件")
            self.attachment_listbox.config(state=tk.DISABLED)
        else:
            for i, attachment in enumerate(attachments):
                size = attachment.get('size', 0)
                size_str = self._format_size(size)
                self.attachment_listbox.insert(tk.END, f"{attachment['name']} ({size_str})")
                self.attachment_listbox.selection_set(i)  # 默认全选
        
        # 全选/取消按钮
        btn_frame = ttk.Frame(attach_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="全选", command=self._select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消全选", command=self._deselect_all).pack(side=tk.LEFT, padx=5)
        
        # 纸张大小选择（与全选/取消同行）
        self.selected_page_size = tk.StringVar(value="A3")
        self.page_combo = ttk.Combobox(btn_frame, textvariable=self.selected_page_size, values=["A3", "A4", "Letter"], state="readonly", width=10)
        self.page_combo.pack(side=tk.RIGHT, padx=(0, 5))
        self.page_combo.current(0)  # Set default to first item (A3), preserves user changes
        ttk.Label(btn_frame, text="纸张大小:").pack(side=tk.RIGHT, padx=(0, 5))
        
        # ===== 操作按钮区域 =====
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(
            action_frame, 
            text="打开邮件", 
            command=self._open_email
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            action_frame, 
            text="忽略", 
            command=self._on_ignore
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            action_frame, 
            text="确认合并", 
            command=self._on_confirm,
            style='Accent.TButton'
        ).pack(side=tk.RIGHT, padx=5)
    
    def _center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def _select_all(self):
        """全选"""
        for i in range(self.attachment_listbox.size()):
            self.attachment_listbox.selection_set(i)
    
    def _deselect_all(self):
        """取消全选"""
        self.attachment_listbox.selection_clear(0, tk.END)
    
    def _move_up(self):
        """上移选中的附件"""
        sel = self.attachment_listbox.curselection()
        if not sel:
            return
        pos = sel[0]
        if pos == 0:
            return
        
        # 记录当前勾选状态
        checked = set()
        for i in range(self.attachment_listbox.size()):
            if i in self.attachment_listbox.curselection():
                checked.add(self.attachment_order[i])
        
        # 交换列表项文本
        text = self.attachment_listbox.get(pos)
        self.attachment_listbox.delete(pos)
        self.attachment_listbox.insert(pos - 1, text)
        
        # 交换顺序记录
        self.attachment_order[pos], self.attachment_order[pos - 1] = \
            self.attachment_order[pos - 1], self.attachment_order[pos]
        
        # 恢复勾选状态
        self.attachment_listbox.selection_clear(0, tk.END)
        for i, orig_idx in enumerate(self.attachment_order):
            if orig_idx in checked:
                self.attachment_listbox.selection_set(i)
        
        # 高亮移动的项
        self.attachment_listbox.selection_set(pos - 1)
        self.attachment_listbox.see(pos - 1)
    
    def _move_down(self):
        """下移选中的附件"""
        sel = self.attachment_listbox.curselection()
        if not sel:
            return
        pos = sel[0]
        if pos >= self.attachment_listbox.size() - 1:
            return
        
        # 记录当前勾选状态
        checked = set()
        for i in range(self.attachment_listbox.size()):
            if i in self.attachment_listbox.curselection():
                checked.add(self.attachment_order[i])
        
        # 交换列表项文本
        text = self.attachment_listbox.get(pos)
        self.attachment_listbox.delete(pos)
        self.attachment_listbox.insert(pos + 1, text)
        
        # 交换顺序记录
        self.attachment_order[pos], self.attachment_order[pos + 1] = \
            self.attachment_order[pos + 1], self.attachment_order[pos]
        
        # 恢复勾选状态
        self.attachment_listbox.selection_clear(0, tk.END)
        for i, orig_idx in enumerate(self.attachment_order):
            if orig_idx in checked:
                self.attachment_listbox.selection_set(i)
        
        # 高亮移动的项
        self.attachment_listbox.selection_set(pos + 1)
        self.attachment_listbox.see(pos + 1)
    
    def _open_email(self):
        """打开邮件"""
        try:
            entry_id = self.email_info.get('entry_id')
            if entry_id:
                import pythoncom
                import win32com.client
                
                # 在当前线程初始化 COM
                pythoncom.CoInitialize()
                
                try:
                    outlook = win32com.client.Dispatch("Outlook.Application")
                    namespace = outlook.GetNamespace("MAPI")
                    mail_item = namespace.GetItemFromID(entry_id)
                    mail_item.Display()
                    logger.info("已打开邮件")
                finally:
                    pythoncom.CoUninitialize()
            else:
                messagebox.showwarning("警告", "无法打开邮件：缺少邮件ID")
        except Exception as e:
            logger.error(f"打开邮件失败: {e}")
            messagebox.showerror("错误", f"无法打开邮件: {e}")
    
    def _on_confirm(self):
        """确认按钮"""
        # 获取勾选的列表位置
        sel_positions = list(self.attachment_listbox.curselection())
        
        if not sel_positions:
            messagebox.showwarning("警告", "请至少选择一个附件")
            return
        
        # 按列表顺序获取选中项对应的原始附件索引
        # 遍历所有位置，只保留被勾选的，按列表顺序排列
        self.selected_attachments = []
        for pos in range(self.attachment_listbox.size()):
            if pos in sel_positions:
                orig_idx = self.attachment_order[pos]
                self.selected_attachments.append(orig_idx)
        
        if not self.selected_attachments:
            messagebox.showwarning("警告", "请至少选择一个附件")
            return
        
        logger.info(f"用户确认合并，选中附件（按排序顺序）: {self.selected_attachments}")
        page_size = self.page_combo.get()  # Direct from combobox, bypasses StringVar quirk
        logger.info(f"用户选择纸张大小: {page_size}")
        self.root.destroy()
        
        # 调用确认回调，传入排序后的附件索引列表和纸张大小
        if self.on_confirm:
            self.on_confirm(self.selected_attachments, page_size)
    
    def _on_ignore(self):
        """忽略按钮"""
        logger.info("用户忽略此邮件")
        self.root.destroy()
        
        if self.on_ignore:
            self.on_ignore()
    
    def _on_close(self):
        """关闭窗口"""
        self._on_ignore()


class MainWindow:
    """主窗口（系统托盘和监控状态）"""
    
    def __init__(self):
        self.root = None
        self.status_var = None
        self.email_count = 0
        self.on_manual_msg = None  # 手动上传 .msg 回调
    
    def show(self):
        """显示主窗口"""
        self.root = tk.Tk()
        self.root.title("Outlook 邮件监控 Agent")
        self.root.geometry("450x500")
        self.root.minsize(400, 450)  # 设置最小窗口大小
        self.root.resizable(True, True)
        
        self._create_widgets()
        self._center_window()
        
        self.root.mainloop()
    
    def _create_widgets(self):
        """创建组件"""
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== 标题 =====
        title_label = ttk.Label(
            main_frame, 
            text="📧 Outlook 邮件监控 Agent",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # ===== 状态信息 =====
        status_frame = ttk.LabelFrame(main_frame, text="监控状态", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_var = tk.StringVar(value="正在监控新邮件...")
        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor=tk.W)
        
        self.count_var = tk.StringVar(value="已处理邮件: 0")
        ttk.Label(status_frame, textvariable=self.count_var).pack(anchor=tk.W, pady=(5, 0))
        
        # ===== 配置信息 =====
        config_frame = ttk.LabelFrame(main_frame, text="当前配置", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        from config import load_config
        _cfg = load_config()
        _keywords = _cfg.get("keywords", [])
        _exts = _cfg.get("allowed_extensions", [])
        ttk.Label(config_frame, text=f"监控关键字: {', '.join(_keywords[:3])}...").pack(anchor=tk.W)
        
        ext_str = ', '.join(_exts) if _exts else '未配置'
        ttk.Label(config_frame, text=f"支持附件类型: {ext_str}").pack(anchor=tk.W, pady=(5, 0))
        
        # ===== 手动上传 .msg =====
        msg_frame = ttk.LabelFrame(main_frame, text="手动处理 .msg 文件", padding="10")
        msg_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(msg_frame, text="直接上传 Outlook 导出的 .msg 文件：").pack(anchor=tk.W)
        
        msg_btn_frame = ttk.Frame(msg_frame)
        msg_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(msg_btn_frame, text="📁 选择 .msg 文件", command=self._select_msg_file).pack(side=tk.LEFT)
        ttk.Label(msg_btn_frame, text="（提取附件并合并为PDF）", foreground='gray').pack(side=tk.LEFT, padx=10)
        
        # ===== 操作按钮 =====
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="⚙ 设置", command=self._open_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="打开输出文件夹", command=self._open_output).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="查看日志", command=self._open_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📦 导出诊断包", command=self._export_diagnostics).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="退出", command=self._quit).pack(side=tk.RIGHT, padx=5)
    
    def _center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def update_status(self, status: str):
        """更新状态"""
        if self.status_var:
            self.status_var.set(status)
    
    def increment_count(self):
        """增加处理计数"""
        self.email_count += 1
        if hasattr(self, 'count_var'):
            self.count_var.set(f"已处理邮件: {self.email_count}")
    
    def _select_msg_file(self):
        """选择 .msg 文件"""
        from tkinter import filedialog, messagebox
        import os
        
        logger.info("打开文件选择对话框...")
        
        file_path = filedialog.askopenfilename(
            title="选择 Outlook .msg 文件",
            filetypes=[("Outlook 邮件", "*.msg"), ("所有文件", "*.*")]
        )
        
        logger.info(f"文件选择结果: {file_path}")
        
        if file_path:
            logger.info(f"用户选择 .msg 文件: {file_path}")
            
            # 调用回调处理文件
            if self.on_manual_msg:
                logger.info("调用回调函数...")
                try:
                    self.on_manual_msg(file_path)
                except Exception as e:
                    logger.error(f"回调函数执行失败: {e}")
                    import traceback
                    traceback.print_exc()
                    messagebox.showerror("错误", f"处理文件失败: {e}")
            else:
                logger.warning("回调函数未设置!")
                messagebox.showwarning("警告", "处理程序未初始化，请重启程序")
    
    def set_manual_msg_callback(self, callback):
        """设置手动上传 .msg 回调"""
        self.on_manual_msg = callback
    
    def _open_output(self):
        """打开输出文件夹"""
        from config import OUTPUT_DIR
        import os
        
        try:
            # 确保目录存在
            if not os.path.exists(OUTPUT_DIR):
                os.makedirs(OUTPUT_DIR)
            
            # 打开文件夹
            os.startfile(OUTPUT_DIR)
            logger.info(f"打开输出文件夹: {OUTPUT_DIR}")
        except Exception as e:
            logger.error(f"打开输出文件夹失败: {e}")
            messagebox.showerror("错误", f"无法打开文件夹: {e}")
    
    def _open_logs(self):
        """打开日志文件夹"""
        from config import LOG_DIR
        import os
        
        try:
            # 确保目录存在
            if not os.path.exists(LOG_DIR):
                os.makedirs(LOG_DIR)
            
            # 打开文件夹
            os.startfile(LOG_DIR)
            logger.info(f"打开日志文件夹: {LOG_DIR}")
        except Exception as e:
            logger.error(f"打开日志文件夹失败: {e}")
            messagebox.showerror("错误", f"无法打开文件夹: {e}")
    
    def _export_diagnostics(self):
        """导出诊断包到合并输出目录"""
        import os
        import zipfile
        import shutil
        from datetime import datetime
        from config import LOG_DIR, CONFIG_FILE
        
        try:
            output_base = os.path.join(os.path.expanduser("~"), "merged_output")
            os.makedirs(output_base, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_name = f"OutlookAgent_diagnostic_{timestamp}.zip"
            zip_path = os.path.join(output_base, zip_name)
            
            work_dir = os.path.join(output_base, f"_diag_tmp_{timestamp}")
            os.makedirs(work_dir, exist_ok=True)
            
            try:
                # 1. 收集日志
                if os.path.exists(LOG_DIR):
                    log_dest = os.path.join(work_dir, "logs")
                    os.makedirs(log_dest, exist_ok=True)
                    for fname in os.listdir(LOG_DIR):
                        fpath = os.path.join(LOG_DIR, fname)
                        if os.path.isfile(fpath):
                            try:
                                shutil.copy(fpath, os.path.join(log_dest, fname))
                            except Exception:
                                pass
                
                # 2. 收集配置文件
                if os.path.exists(CONFIG_FILE):
                    shutil.copy(CONFIG_FILE, os.path.join(work_dir, "outlook_agent_config.json"))
                
                # 3. 收集最新的会话摘要
                latest_summary = None
                latest_time = ""
                if os.path.exists(LOG_DIR):
                    for fname in os.listdir(LOG_DIR):
                        if fname.startswith("summary_") and fname.endswith(".txt"):
                            fpath = os.path.join(LOG_DIR, fname)
                            if os.path.isfile(fpath):
                                mtime = os.path.getmtime(fpath)
                                if latest_summary is None or mtime > latest_time:
                                    latest_summary = fpath
                                    latest_time = mtime
                if latest_summary:
                    shutil.copy(latest_summary, os.path.join(work_dir, "latest_summary.txt"))
                
                # 4. 打包为 ZIP
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for root, dirs, files in os.walk(work_dir):
                        for fn in files:
                            full_path = os.path.join(root, fn)
                            arcname = os.path.relpath(full_path, work_dir)
                            zf.write(full_path, arcname)
                
                logger.info(f"诊断包已导出: {zip_path}")
                messagebox.showinfo(
                    "导出成功",
                    f"诊断包已保存到桌面:\n{zip_path}\n\n请将此文件发送给技术支持。"
                )
                
            finally:
                try:
                    shutil.rmtree(work_dir)
                except Exception:
                    pass
                    
        except Exception as e:
            logger.error(f"导出诊断包失败: {e}")
            messagebox.showerror("导出失败", f"无法导出诊断包: {e}")
    
    def _open_settings(self):
        """打开设置窗口"""
        SettingsWindow(self.root)
    
    def _quit(self):
        """退出程序"""
        if messagebox.askokcancel("退出", "确定要退出监控吗？"):
            self.root.quit()
            self.root.destroy()


def show_confirm_dialog(email_info: dict, on_confirm: Callable, on_ignore: Callable):
    """
    显示确认对话框
    
    Args:
        email_info: 邮件信息
        on_confirm: 确认回调
        on_ignore: 忽略回调
    """
    window = EmailConfirmWindow(email_info, on_confirm, on_ignore)
    window.show()


class SettingsWindow:
    """设置窗口"""
    
    def __init__(self, parent=None):
        """初始化设置窗口"""
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("设置 - Outlook 邮件监控 Agent")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # 加载当前配置
        from config import load_config
        self.config = load_config()
        
        self._create_widgets()
        self._center_window()
        
        # 模态窗口
        if parent:
            self.root.transient(parent)
            self.root.grab_set()
        
        self.root.mainloop()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 创建笔记本（选项卡）
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== 基本设置选项卡 =====
        basic_frame = ttk.Frame(notebook, padding="10")
        notebook.add(basic_frame, text="基本设置")
        
        # PDFMergeTool 路径
        path_frame = ttk.LabelFrame(basic_frame, text="PDFMergeTool 路径", padding="10")
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.pdf_tool_var = tk.StringVar(value=self.config.get("pdf_merge_tool_path", ""))
        
        ttk.Label(path_frame, text="PDFMergeTool.exe 路径:").pack(anchor=tk.W)
        
        path_entry_frame = ttk.Frame(path_frame)
        path_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Entry(path_entry_frame, textvariable=self.pdf_tool_var, width=60).pack(
            side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_entry_frame, text="浏览...", command=self._browse_pdf_tool).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(path_frame, text="提示: 这是之前开发的 PDF 合并工具", 
                 foreground="gray").pack(anchor=tk.W, pady=(5, 0))
        
        # 输出目录
        output_frame = ttk.LabelFrame(basic_frame, text="输出目录", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.output_dir_var = tk.StringVar(value=self.config.get("output_dir", ""))
        
        output_entry_frame = ttk.Frame(output_frame)
        output_entry_frame.pack(fill=tk.X)
        
        ttk.Entry(output_entry_frame, textvariable=self.output_dir_var, width=60).pack(
            side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_entry_frame, text="浏览...", command=self._browse_output_dir).pack(side=tk.LEFT, padx=(5, 0))
        
        # 监控设置
        monitor_frame = ttk.LabelFrame(basic_frame, text="监控设置", padding="10")
        monitor_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 检查间隔
        interval_frame = ttk.Frame(monitor_frame)
        interval_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(interval_frame, text="检查邮件间隔:").pack(side=tk.LEFT)
        
        self.interval_var = tk.IntVar(value=self.config.get("check_interval", 30))
        interval_spinbox = ttk.Spinbox(interval_frame, from_=10, to=300, width=8, 
                                       textvariable=self.interval_var)
        interval_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(interval_frame, text="秒").pack(side=tk.LEFT)
        
        # 通知设置
        notify_frame = ttk.Frame(monitor_frame)
        notify_frame.pack(fill=tk.X)
        
        self.show_notify_var = tk.BooleanVar(value=self.config.get("show_notification", True))
        ttk.Checkbutton(notify_frame, text="显示 Windows 通知", 
                       variable=self.show_notify_var).pack(anchor=tk.W)
        
        self.play_sound_var = tk.BooleanVar(value=self.config.get("play_sound", True))
        ttk.Checkbutton(notify_frame, text="播放提示音", 
                       variable=self.play_sound_var).pack(anchor=tk.W)
        
        # 邮件监控模式设置
        mode_frame = ttk.LabelFrame(monitor_frame, text="邮件监控模式", padding="5")
        mode_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.monitor_mode_var = tk.StringVar(value=self.config.get("monitor_mode", "time"))
        
        ttk.Radiobutton(
            mode_frame, 
            text="时间监控（监控最近N分钟内的邮件）", 
            variable=self.monitor_mode_var, 
            value="time"
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            mode_frame, 
            text="数量监控（监控最近N封邮件）", 
            variable=self.monitor_mode_var, 
            value="count"
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            mode_frame, 
            text="两者结合（最近N封 + 时间过滤）", 
            variable=self.monitor_mode_var, 
            value="both"
        ).pack(anchor=tk.W)
        
        # 时间和数量设置
        range_frame = ttk.Frame(mode_frame)
        range_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(range_frame, text="时间范围:").pack(side=tk.LEFT)
        self.time_range_var = tk.IntVar(value=self.config.get("monitor_time_range", 60))
        ttk.Spinbox(range_frame, from_=5, to=1440, width=6, 
                   textvariable=self.time_range_var).pack(side=tk.LEFT, padx=5)
        ttk.Label(range_frame, text="分钟").pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(range_frame, text="数量限制:").pack(side=tk.LEFT)
        self.count_limit_var = tk.IntVar(value=self.config.get("monitor_count_limit", 50))
        ttk.Spinbox(range_frame, from_=10, to=500, width=6, 
                   textvariable=self.count_limit_var).pack(side=tk.LEFT, padx=5)
        ttk.Label(range_frame, text="封").pack(side=tk.LEFT)
        
        # ===== 关键字设置选项卡 =====
        keyword_frame = ttk.Frame(notebook, padding="10")
        notebook.add(keyword_frame, text="监控关键字")
        
        ttk.Label(keyword_frame, text="当邮件主题或正文包含以下关键字时触发提醒:", 
                 wraplength=500).pack(anchor=tk.W, pady=(0, 10))
        
        # 关键字列表
        list_frame = ttk.Frame(keyword_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 列表框
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.keyword_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, height=15)
        self.keyword_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.keyword_listbox.yview)
        
        # 加载现有关键字
        for keyword in self.config.get("keywords", []):
            self.keyword_listbox.insert(tk.END, keyword)
        
        # 按钮区域
        kw_btn_frame = ttk.Frame(list_frame)
        kw_btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        
        # 添加关键字
        add_frame = ttk.Frame(kw_btn_frame)
        add_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.new_keyword_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_keyword_var, width=15).pack(fill=tk.X)
        ttk.Button(add_frame, text="添加", command=self._add_keyword).pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(kw_btn_frame, text="删除选中", command=self._remove_keyword).pack(fill=tk.X, pady=5)
        ttk.Button(kw_btn_frame, text="清空全部", command=self._clear_keywords).pack(fill=tk.X)
        
        # ===== 附件类型选项卡 =====
        ext_frame = ttk.Frame(notebook, padding="10")
        notebook.add(ext_frame, text="附件类型")
        
        ttk.Label(ext_frame, text="允许处理的附件类型:", 
                 wraplength=500).pack(anchor=tk.W, pady=(0, 10))
        
        # 附件类型列表
        ext_list_frame = ttk.Frame(ext_frame)
        ext_list_frame.pack(fill=tk.BOTH, expand=True)
        
        ext_scrollbar = ttk.Scrollbar(ext_list_frame)
        ext_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.ext_listbox = tk.Listbox(ext_list_frame, yscrollcommand=ext_scrollbar.set, 
                                      selectmode=tk.MULTIPLE, height=15)
        self.ext_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ext_scrollbar.config(command=self.ext_listbox.yview)
        
        # 加载所有常见类型，并选中已启用的
        all_extensions = [
            ".pdf", ".docx", ".doc", ".xlsx", ".xls", 
            ".txt", ".png", ".jpg", ".jpeg", ".gif", 
            ".bmp", ".tiff", ".webp", ".rtf", ".csv", ".msg"
        ]
        enabled_exts = self.config.get("allowed_extensions", [])
        
        for ext in all_extensions:
            self.ext_listbox.insert(tk.END, ext)
            if ext in enabled_exts:
                self.ext_listbox.selection_set(tk.END)
        
        ttk.Label(ext_frame, text="提示: 按住 Ctrl 可多选", 
                 foreground="gray").pack(anchor=tk.W, pady=(10, 0))
        
        # ===== 底部按钮 =====
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(bottom_frame, text="保存", command=self._save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text="取消", command=self._cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text="恢复默认", command=self._reset_default).pack(side=tk.LEFT, padx=5)
    
    def _center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _browse_pdf_tool(self):
        """浏览 PDFMergeTool 路径"""
        path = filedialog.askopenfilename(
            title="选择 PDFMergeTool.exe",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        if path:
            self.pdf_tool_var.set(path)
    
    def _browse_output_dir(self):
        """浏览输出目录"""
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.output_dir_var.set(path)
    
    def _add_keyword(self):
        """添加关键字"""
        keyword = self.new_keyword_var.get().strip()
        if keyword:
            # 检查是否已存在
            for i in range(self.keyword_listbox.size()):
                if self.keyword_listbox.get(i) == keyword:
                    messagebox.showwarning("警告", "该关键字已存在")
                    return
            
            self.keyword_listbox.insert(tk.END, keyword)
            self.new_keyword_var.set("")
    
    def _remove_keyword(self):
        """删除选中的关键字"""
        selection = self.keyword_listbox.curselection()
        for index in reversed(selection):
            self.keyword_listbox.delete(index)
    
    def _clear_keywords(self):
        """清空所有关键字"""
        if messagebox.askyesno("确认", "确定要清空所有关键字吗？"):
            self.keyword_listbox.delete(0, tk.END)
    
    def _save_settings(self):
        """保存设置"""
        # 收集关键字（如果为空则使用默认值）
        keywords = []
        for i in range(self.keyword_listbox.size()):
            keywords.append(self.keyword_listbox.get(i))
        
        # 如果没有关键字，使用默认关键字
        if not keywords:
            keywords = ["合同审批", "文件合并", "PDF合并", "附件处理", "合并附件"]
        
        # 收集附件类型（如果为空则使用默认值）
        extensions = []
        for i in self.ext_listbox.curselection():
            extensions.append(self.ext_listbox.get(i))
        
        # 如果没有选中任何类型，使用默认类型
        if not extensions:
            extensions = [".pdf", ".docx", ".doc", ".xlsx", ".xls", 
                         ".txt", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".msg"]
        
        # 更新配置
        self.config["pdf_merge_tool_path"] = self.pdf_tool_var.get()
        self.config["output_dir"] = self.output_dir_var.get()
        self.config["check_interval"] = self.interval_var.get()
        self.config["show_notification"] = self.show_notify_var.get()
        self.config["play_sound"] = self.play_sound_var.get()
        self.config["keywords"] = keywords
        self.config["allowed_extensions"] = extensions
        
        # 邮件监控模式设置
        self.config["monitor_mode"] = self.monitor_mode_var.get()
        self.config["monitor_time_range"] = self.time_range_var.get()
        self.config["monitor_count_limit"] = self.count_limit_var.get()
        
        # 保存到文件
        from config import save_config
        if save_config(self.config):
            messagebox.showinfo("成功", "设置已保存！\n部分设置将在下次启动时生效。")
            self.root.destroy()
        else:
            messagebox.showerror("错误", "保存设置失败")
    
    def _reset_default(self):
        """恢复默认设置"""
        if messagebox.askyesno("确认", "确定要恢复默认设置吗？"):
            from config import DEFAULT_CONFIG
            self.config = DEFAULT_CONFIG.copy()
            
            # 更新界面
            self.pdf_tool_var.set(self.config.get("pdf_merge_tool_path", ""))
            self.output_dir_var.set(self.config.get("output_dir", ""))
            self.interval_var.set(self.config.get("check_interval", 30))
            self.show_notify_var.set(self.config.get("show_notification", True))
            self.play_sound_var.set(self.config.get("play_sound", True))
            
            # 监控模式设置
            self.monitor_mode_var.set(self.config.get("monitor_mode", "time"))
            self.time_range_var.set(self.config.get("monitor_time_range", 60))
            self.count_limit_var.set(self.config.get("monitor_count_limit", 50))
            
            # 更新关键字列表
            self.keyword_listbox.delete(0, tk.END)
            for keyword in self.config.get("keywords", []):
                self.keyword_listbox.insert(tk.END, keyword)
            
            # 更新附件类型选择
            for i in range(self.ext_listbox.size()):
                ext = self.ext_listbox.get(i)
                if ext in self.config.get("allowed_extensions", []):
                    self.ext_listbox.selection_set(i)
                else:
                    self.ext_listbox.selection_clear(i)
    
    def _cancel(self):
        """取消"""
        self.root.destroy()

