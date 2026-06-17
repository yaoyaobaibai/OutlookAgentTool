"""
Outlook 邮件监控 Agent - 主程序入口
"""
import os
import sys
import time
import logging
import threading
import traceback
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    load_config,
    save_config,
    LOG_DIR
)
from utils.crash_dump import save_crash_dump

from outlook_monitor import OutlookMonitor
from notification import NotificationManager
from attachment_handler import AttachmentHandler
from merge_launcher import MergeLauncher
from gui import show_confirm_dialog, MainWindow

__version__ = "1.2.9"

# 纸张大小映射 (points)
PAGE_SIZES_FOR_HTML = {
    'A3': (841.89, 1190.55),
    'A4': (595.28, 841.89),
    'Letter': (612, 792),
}

# ========== 日志配置 ==========
def setup_logging():
    """配置日志"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    log_file = os.path.join(LOG_DIR, f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    # 创建 handlers 并设置编码
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    stream_handler = logging.StreamHandler()
    
    # Windows 控制台 UTF-8 编码
    if sys.platform == 'win32':
        try:
            import io
            stream_handler.stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except:
            pass
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[file_handler, stream_handler]
    )
    
    return log_file

LOG_FILE = setup_logging()
logger = logging.getLogger(__name__)


# ========== 主控制器 ==========
class OutlookAgent:
    """Outlook 邮件监控 Agent 主控制器"""
    
    def __init__(self):
        """初始化 Agent"""
        logger.info("初始化 Outlook Agent...")
        
        # 动态加载配置
        config = load_config()
        keywords = config.get("keywords", [])
        allowed_extensions = config.get("allowed_extensions", [])
        temp_dir = config.get("temp_dir", "")
        pdf_merge_tool_path = config.get("pdf_merge_tool_path", "")
        output_dir = config.get("output_dir", "")
        
        # 初始化各模块
        self.monitor = OutlookMonitor(keywords, "any")
        self.notifier = NotificationManager()
        self.attachment_handler = AttachmentHandler(temp_dir, allowed_extensions)
        self.merge_launcher = MergeLauncher(pdf_merge_tool_path, output_dir)
        
        # 主窗口
        self.main_window = None
        
        # 运行状态
        self.running = False
        self.current_email = None
        self.current_manual_msg = None
        
        # 错误追踪
        self.error_count = 0
        self.errors = []
        self.start_time = datetime.now()
        
        # 崩溃转储
        self._last_crash_zip = None
        
        # 设置监控回调
        self.monitor.set_email_callback(self.on_new_email)
        
        logger.info("Agent 初始化完成")
    
    def start(self):
        """启动 Agent"""
        logger.info("启动 Outlook Agent...")
        
        # 检查是否首次运行（PDFMergeTool 路径未设置）
        if not self._check_first_run():
            return False
        
        # 同步 launcher 路径（自动检测/手动设置后配置可能已更新）
        config = load_config()
        saved_path = config.get("pdf_merge_tool_path", "")
        if saved_path and saved_path != self.merge_launcher.tool_path:
            self.merge_launcher.tool_path = saved_path
            logger.info(f"已同步 PDFMergeTool 路径: {saved_path}")
        
        # 连接 Outlook
        if not self.monitor.connect():
            logger.error("无法连接到 Outlook，请确保 Outlook 正在运行")
            self._show_error("无法连接到 Outlook", "请确保 Microsoft Outlook 正在运行")
            return False
        
        self.running = True
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        
        logger.info("监控线程已启动")
        
        # 显示主窗口
        self.main_window = MainWindow()
        
        # 设置手动上传 .msg 回调
        self.main_window.set_manual_msg_callback(self._on_manual_msg_file)
        
        self.main_window.show()
        
        return True
    
    def _check_first_run(self) -> bool:
        """检查是否首次运行，如果需要则显示配置向导"""
        config = load_config()
        
        # 优先使用同目录下的 PDFMergeTool.exe
        exe_dir = os.path.dirname(sys.executable)
        auto_path = os.path.join(exe_dir, "PDFMergeTool.exe")
        if os.path.exists(auto_path):
            config['pdf_merge_tool_path'] = auto_path
            save_config(config)
            self.merge_launcher.tool_path = auto_path
            logger.info(f"使用同目录 PDFMergeTool: {auto_path}")
            return True
        
        # 回退到已保存的配置路径
        pdf_merge_tool_path = config.get("pdf_merge_tool_path", "")
        if pdf_merge_tool_path and os.path.exists(pdf_merge_tool_path):
            self.merge_launcher.tool_path = pdf_merge_tool_path
            logger.info(f"使用已配置 PDFMergeTool: {pdf_merge_tool_path}")
            return True
        
        # 未检测到 → 显示配置向导
        return self._show_setup_wizard()
    
    def _show_setup_wizard(self) -> bool:
        """显示首次运行配置向导"""
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        
        root = tk.Tk()
        root.title("Outlook Agent - 首次运行配置")
        root.geometry("500x350")
        root.resizable(False, False)
        
        # 居中
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - 250
        y = (root.winfo_screenheight() // 2) - 175
        root.geometry(f"500x350+{x}+{y}")
        
        frame = ttk.Frame(root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(
            frame, 
            text="欢迎使用 Outlook Agent！",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 10))
        
        # 说明
        ttk.Label(
            frame,
            text="首次运行需要设置 PDFMergeTool.exe 的路径。\n\n请确保 PDFMergeTool.exe 已放置在合适的位置。",
            wraplength=400
        ).pack(pady=(0, 20))
        
        # 路径选择
        path_frame = ttk.LabelFrame(frame, text="PDFMergeTool.exe 路径", padding="10")
        path_frame.pack(fill=tk.X, pady=(0, 20))
        
        path_var = tk.StringVar()
        
        path_entry = ttk.Entry(path_frame, textvariable=path_var, width=50)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def browse():
            file_path = filedialog.askopenfilename(
                title="选择 PDFMergeTool.exe",
                filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
            )
            if file_path:
                path_var.set(file_path)
        
        ttk.Button(path_frame, text="浏览...", command=browse).pack(side=tk.RIGHT)
        
        # 自动检测同目录下的 PDFMergeTool.exe
        exe_dir = os.path.dirname(sys.executable)
        auto_path = os.path.join(exe_dir, "PDFMergeTool.exe")
        if os.path.exists(auto_path):
            path_var.set(auto_path)
            ttk.Label(
                frame,
                text="✓ 已自动检测到 PDFMergeTool.exe",
                foreground='green'
            ).pack(pady=(5, 0))
        
        result = [False]
        
        def on_confirm():
            path = path_var.get().strip()
            if not path:
                messagebox.showwarning("警告", "请选择 PDFMergeTool.exe 的路径")
                return
            if not os.path.exists(path):
                messagebox.showerror("错误", "所选文件不存在")
                return
            
            # 保存配置
            config = load_config()
            config['pdf_merge_tool_path'] = path
            if save_config(config):
                logger.info(f"已保存 PDFMergeTool 路径: {path}")
                result[0] = True
                root.destroy()
            else:
                messagebox.showerror("错误", "保存配置失败")
        
        def on_cancel():
            if messagebox.askyesno("退出", "未完成配置，程序将退出。确定要退出吗？"):
                root.destroy()
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="取消", command=on_cancel).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="确定", command=on_confirm).pack(side=tk.RIGHT)
        
        root.mainloop()
        
        return result[0]
    
    def _monitor_loop(self):
        """监控循环（备用轮询方案）"""
        logger.info("开始轮询监控...")
        
        # 首次立即检查
        try:
            logger.info("首次检查邮件...")
            new_emails = self.monitor.poll_new_emails()
            
            for email_info in new_emails:
                logger.info(f"检测到匹配邮件: {email_info['subject']}")
                self.on_new_email(email_info)
        except Exception as e:
            logger.error(f"首次检查出错: {e}")
        
        while self.running:
            try:
                # 动态读取配置
                from config import load_config
                config = load_config()
                check_interval = config.get("check_interval", 30)
                
                # 更新状态
                if self.main_window:
                    self.main_window.update_status(f"监控中... (下次检查: {check_interval}秒后)")
                
                # 等待指定秒数
                time.sleep(check_interval)
                
                # 轮询新邮件
                logger.info("轮询检查新邮件...")
                new_emails = self.monitor.poll_new_emails()
                
                for email_info in new_emails:
                    logger.info(f"检测到匹配邮件: {email_info['subject']}")
                    self.on_new_email(email_info)
                
            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                time.sleep(10)
    
    def on_new_email(self, email_info: dict):
        """
        新邮件回调
        
        Args:
            email_info: 邮件信息字典
        """
        logger.info(f"收到新邮件: {email_info['subject']}")
        logger.info(f"发件人: {email_info['sender_name']} <{email_info['sender_email']}>")
        logger.info(f"附件数: {len(email_info['attachments'])}")
        
        # 保存当前邮件
        self.current_email = email_info
        
        # 显示通知
        self.notifier.show_email_alert(email_info)
        
        # 增加计数
        if self.main_window:
            self.main_window.increment_count()
        
        # 显示确认窗口（在主线程中，用 after() 避免 tkinter 跨线程崩溃）
        if self.main_window and self.main_window.root:
            self.main_window.root.after(0, lambda ei=email_info: self._show_confirm_window(ei))
    
    def _show_confirm_window(self, email_info: dict):
        """显示确认窗口"""
        show_confirm_dialog(
            email_info,
            on_confirm=self._on_user_confirm,
            on_ignore=self._on_user_ignore
        )
    
    def _on_user_confirm(self, selected_indices: list, page_size: str = 'A4'):
        """
        用户确认回调
        
        Args:
            selected_indices: 选中的附件索引列表
            page_size: 纸张大小（A3/A4/Letter）
        """
        logger.info(f"用户确认合并，选中附件: {selected_indices}, 纸张大小: {page_size}")
        
        if not self.current_email:
            return
        
        # 显示进度窗口
        self._show_progress_window()
        
        try:
            # 更新进度：下载附件
            self._update_progress("正在下载附件...", 10)
            
            downloaded_files = self.attachment_handler.download_attachments(
                self.current_email,
                selected_indices
            )
            
            if not downloaded_files:
                logger.warning("没有下载任何附件")
                self.error_count += 1
                self.errors.append("没有下载任何附件")
                self._close_progress_window()
                self._show_result(False, "没有下载任何附件")
                return
            
            logger.info(f"下载附件成功: {len(downloaded_files)} 个文件")
            self._update_progress(f"已下载 {len(downloaded_files)} 个文件", 30)
            
            # 更新进度：准备合并
            self._update_progress("正在合并文件...", 50)
            
            # 调用合并工具
            success, message = self.merge_launcher.merge_files(downloaded_files, page_size=page_size)
            
            self._update_progress("处理完成", 100)
            
            # 关闭进度窗口
            self._close_progress_window()
            
            # 显示结果
            self._show_result(success, message)
            
            if success:
                logger.info(f"合并成功: {message}")
            else:
                logger.error(f"合并失败: {message}")
                self.error_count += 1
                self.errors.append(f"合并失败: {message}")
            
            # 清理旧的临时文件
            self.attachment_handler.cleanup_temp_files()
            
        except Exception as e:
            logger.error(f"处理附件时出错: {e}")
            traceback.print_exc()
            self.error_count += 1
            self.errors.append(f"处理附件异常: {e}")
            self._close_progress_window()
            self._show_result(False, f"处理出错: {e}")
    
    def _show_progress_window(self):
        """显示进度窗口"""
        import tkinter as tk
        from tkinter import ttk
        
        self.progress_root = tk.Tk()
        self.progress_root.title("合并进度")
        self.progress_root.geometry("400x150")
        self.progress_root.resizable(False, False)
        
        # 居中
        self.progress_root.update_idletasks()
        x = (self.progress_root.winfo_screenwidth() // 2) - 200
        y = (self.progress_root.winfo_screenheight() // 2) - 75
        self.progress_root.geometry(f"400x150+{x}+{y}")
        
        # 进度标签
        self.progress_label = ttk.Label(
            self.progress_root, 
            text="准备中...",
            font=('Arial', 12)
        )
        self.progress_label.pack(pady=20)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(
            self.progress_root,
            mode='determinate',
            length=300
        )
        self.progress_bar.pack(pady=10)
        
        # 取消按钮（禁用）
        self.cancel_btn = ttk.Button(
            self.progress_root,
            text="取消",
            state='disabled'
        )
        self.cancel_btn.pack(pady=10)
        
        self.progress_root.update()
    
    def _update_progress(self, message: str, value: int):
        """更新进度"""
        if hasattr(self, 'progress_root') and self.progress_root:
            self.progress_label.config(text=message)
            self.progress_bar['value'] = value
            self.progress_root.update()
    
    def _close_progress_window(self):
        """关闭进度窗口"""
        if hasattr(self, 'progress_root') and self.progress_root:
            self.progress_root.destroy()
            self.progress_root = None
    
    def _show_result(self, success: bool, message: str):
        """显示结果窗口"""
        import tkinter as tk
        from tkinter import messagebox
        
        # 发送任务栏通知
        if success:
            self.notifier.show_notification(
                "合并成功",
                message,
                duration=5
            )
        else:
            self.notifier.show_notification(
                "合并失败", 
                message,
                duration=10
            )
        
        # 显示弹窗
        root = tk.Tk()
        root.withdraw()
        
        if success:
            messagebox.showinfo("合并完成", message)
        else:
            messagebox.showerror("合并失败", message)
        
        root.destroy()
    
    def _on_user_ignore(self):
        """用户忽略回调"""
        logger.info("用户忽略此邮件")
        self.current_email = None
    
    def _on_manual_msg_file(self, msg_path: str):
        """处理手动上传的 .msg 文件"""
        
        logger.info(f"开始处理手动上传的 .msg 文件: {msg_path}")
        
        # 解析 .msg 文件，获取邮件信息和附件列表
        success, email_info, attachments, error = self.attachment_handler.parse_msg_file(msg_path)
        
        if not success:
            self.error_count += 1
            self.errors.append(f"解析 .msg 文件失败: {error}")
            self._show_error("解析失败", f"无法解析 .msg 文件: {error}")
            return
        
        body_text = email_info.get('body', '').strip() if email_info else ''
        if not attachments and not body_text:
            self.error_count += 1
            self.errors.append(".msg 文件中没有附件和正文")
            self._show_error("无内容", ".msg 文件中没有附件和正文")
            return
        if not attachments:
            logger.info("没有附件，仅提取邮件正文")
            # 添加虚拟附件项，让确认窗口可以显示和选择
            body_len = len(body_text) if body_text else 0
            attachments = [{
                'name': '📧 邮件正文',
                'size': body_len,
                'data': None,
                'is_virtual_body': True,
            }]
        
        logger.info(f"解析成功，发现 {len(attachments)} 个附件")
        
        # 构造类似邮件信息的结构（复用确认窗口）
        fake_email_info = {
            'entry_id': f"manual_{os.path.basename(msg_path)}",
            'subject': email_info.get('subject', '(无主题)'),
            'sender_name': email_info.get('sender', 'Unknown'),
            'sender_email': '',
            'received_time': email_info.get('date', ''),
            'attachments': attachments,
        }
        
        # 保存当前处理的文件路径
        self.current_manual_msg = msg_path
        # 保存邮件信息，供合并时提取正文
        self.current_manual_msg_info = email_info
        
        # 显示确认窗口（与监控邮件相同的流程）
        from gui import show_confirm_dialog
        show_confirm_dialog(
            fake_email_info,
            on_confirm=self._on_manual_msg_confirm,
            on_ignore=self._on_manual_msg_ignore
        )
    
    def _on_manual_msg_confirm(self, selected_indices: list, page_size: str = 'A4'):
        """用户确认手动上传的 .msg 附件选择"""
        import tempfile
        import shutil
        
        logger.info(f"用户确认手动 .msg 附件选择: {selected_indices}, 纸张大小: {page_size}")
        
        if not self.current_manual_msg:
            return
        
        # 显示进度窗口
        self._show_progress_window()
        
        try:
            # 创建临时目录
            temp_dir = tempfile.mkdtemp(prefix="manual_msg_")
            
            # 更新进度：提取附件
            self._update_progress("正在提取附件...", 20)
            
            # 提取选中的附件
            success, extracted_files, error = self.attachment_handler.extract_attachments_from_msg(
                self.current_manual_msg,
                temp_dir,
                selected_indices
            )
            
            # 将主邮件正文作为第一个 PDF（HTML 渲染保留表格和图片）
            if self.current_manual_msg_info and self.current_manual_msg_info.get('body', '').strip():
                body_pdf = os.path.join(temp_dir, "_email_body.pdf")
                body_ok = False
                
                # Try HTML body rendering
                try:
                    import extract_msg
                    msg_obj = extract_msg.Message(self.current_manual_msg)
                    # Check if email has HTML body for rich rendering
                    logger.info(f"htmlBody 长度: {len(msg_obj.htmlBody) if msg_obj.htmlBody else 0}")
                    if msg_obj.htmlBody:
                        logger.info(f"尝试 HTML 渲染...")
                        from attachment_handler import _html_body_to_pdf
                        body_ok = _html_body_to_pdf(msg_obj, body_pdf, temp_dir, page_size=PAGE_SIZES_FOR_HTML.get(page_size))
                        logger.info(f"HTML 渲染结果: {body_ok}")
                    else:
                        logger.info("邮件无 HTML 正文（RTF-only 或纯文本），将使用纯文本渲染")
                    msg_obj.close()
                except Exception as e:
                    logger.warning(f"HTML 正文渲染不可用: {e}")
                
                if not body_ok:
                    # Fallback: plain text
                    body_path = os.path.join(temp_dir, "_email_body.txt")
                    with open(body_path, 'w', encoding='utf-8') as f:
                        f.write(self.current_manual_msg_info['body'])
                    extracted_files.insert(0, body_path)
                else:
                    extracted_files.insert(0, body_pdf)
                logger.info(f"已提取邮件正文")
            
            if not success or not extracted_files:
                self.error_count += 1
                self.errors.append(f"提取附件失败: {error or '没有可提取的内容'}")
                self._close_progress_window()
                self._show_result(False, f"提取附件失败: {error or '没有可提取的内容'}")
                return
            
            logger.info(f"提取到 {len(extracted_files)} 个文件")
            self._update_progress(f"已提取 {len(extracted_files)} 个附件", 40)
            
            # 更新进度：合并文件
            self._update_progress("正在合并为 PDF...", 60)
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"manual_{timestamp}.pdf"
            
            # 调用合并工具
            success, message = self.merge_launcher.merge_files(
                extracted_files, 
                output_filename,
                page_size=page_size
            )
            
            self._update_progress("处理完成", 100)
            
            # 关闭进度窗口
            self._close_progress_window()
            
            # 显示结果
            self._show_result(success, message)
            
            if success:
                logger.info(f"手动处理 .msg 成功: {message}")
                if self.main_window:
                    self.main_window.increment_count()
            else:
                logger.error(f"手动处理 .msg 失败: {message}")
                self.error_count += 1
                self.errors.append(f"手动处理 .msg 合并失败: {message}")
            
            # 清理临时文件
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
                
        except Exception as e:
            logger.error(f"处理手动 .msg 文件失败: {e}")
            traceback.print_exc()
            self.error_count += 1
            self.errors.append(f"处理手动 .msg 异常: {e}")
            self._close_progress_window()
            self._show_result(False, f"处理失败: {e}")
        
        finally:
            self.current_manual_msg = None
    
    def _on_manual_msg_ignore(self):
        """用户忽略手动上传的 .msg"""
        logger.info("用户忽略手动上传的 .msg 文件")
        self.current_manual_msg = None
    
    def stop(self):
        """停止 Agent"""
        logger.info("停止 Outlook Agent...")
        self.running = False
        self.monitor.disconnect()
        
        # 写入会话错误摘要
        self._write_session_summary()
    
    def _write_session_summary(self):
        """写入会话错误摘要到日志目录"""
        try:
            end_time = datetime.now()
            timestamp = end_time.strftime("%Y%m%d_%H%M%S")
            summary_path = os.path.join(LOG_DIR, f"summary_{timestamp}.txt")
            
            emails_processed = self.main_window.email_count if self.main_window else 0
            start_time_str = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f"会话摘要\n")
                f.write(f"{'='*50}\n")
                f.write(f"日志文件: {LOG_FILE}\n")
                f.write(f"开始时间: {start_time_str}\n")
                f.write(f"结束时间: {end_time_str}\n")
                f.write(f"已处理邮件: {emails_processed}\n")
                f.write(f"已匹配邮件: {self.main_window.email_count if self.main_window else 0}\n")
                f.write(f"错误总数: {self.error_count}\n")
                f.write(f"\n错误详情:\n")
                if self.errors:
                    for i, err in enumerate(self.errors, 1):
                        f.write(f"  {i}. {err}\n")
                else:
                    f.write("  无错误\n")
            
            logger.info(f"会话摘要已保存: {summary_path}")
        except Exception as e:
            logger.error(f"写入会话摘要失败: {e}")
    
    def _show_error(self, title: str, message: str):
        """显示错误消息"""
        import tkinter as tk
        from tkinter import messagebox
        
        full_message = message
        if self._last_crash_zip:
            full_message += f"\n\n调试包: {self._last_crash_zip}"
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, full_message)
        root.destroy()


# ========== 程序入口 ==========
def main():
    """主函数"""
    # 加载配置
    config = load_config()
    keywords = config.get("keywords", [])
    pdf_merge_tool_path = config.get("pdf_merge_tool_path", "")
    
    logger.info("="*50)
    logger.info("Outlook 邮件监控 Agent 启动")
    logger.info(f"日志文件: {LOG_FILE}")
    logger.info(f"监控关键字: {keywords}")
    logger.info(f"PDFMergeTool: {pdf_merge_tool_path}")
    logger.info("="*50)
    
    # 检查 PDFMergeTool
    if pdf_merge_tool_path and not os.path.exists(pdf_merge_tool_path):
        logger.warning(f"PDFMergeTool 不存在: {pdf_merge_tool_path}")
        logger.warning("请在设置中配置 PDFMergeTool 路径")
    
    # 创建 Agent
    agent = OutlookAgent()
    
    try:
        # 启动
        agent.start()
    except KeyboardInterrupt:
        logger.info("用户中断")
        agent.stop()
    except Exception as e:
        import traceback as tb
        crash_zip = save_crash_dump(
            error_msg=f"{e}\n{tb.format_exc()}",
            current_log_file=LOG_FILE,
        )
        if crash_zip:
            agent._last_crash_zip = crash_zip
            logger.error(f"程序异常: {e}\n调试包: {crash_zip}")
        else:
            logger.error(f"程序异常: {e}")
            traceback.print_exc()
        agent.stop()
    
    logger.info("程序退出")


if __name__ == '__main__':
    main()
