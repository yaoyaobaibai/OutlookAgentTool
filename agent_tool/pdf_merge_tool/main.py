"""PDF 合并工具 - GUI 主程序"""
import os
import sys
import argparse
import threading
import queue
import logging
import traceback
import uuid
from datetime import datetime
from pathlib import Path

# ========== 全局 UTF-8 输出（防中文崩 cp1252）==========
import io
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding='utf-8', errors='replace'
    )
from typing import List, Optional

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from converters import txt_to_pdf, image_to_pdf, word_to_pdf, excel_to_pdf, merge_pdfs
from utils import get_file_type, get_temp_dir, cleanup_temp_files, add_page_numbers

__version__ = "1.2.6"

# 纸张大小映射
PAGE_SIZES = {
    'A3': (841.89, 1190.55),
    'A4': (595.28, 841.89),
    'Letter': (612, 792),
}

# ========== 日志配置 ==========
def setup_logging():
    """配置日志系统"""
    # 日志文件路径：用户桌面或临时目录
    log_dir = os.path.join(os.path.expanduser("~"), "PDFMergeTool_logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    # 配置日志
    stream_handler = logging.StreamHandler(sys.stdout)
    # 确保控制台输出使用 UTF-8，避免中文 Windows GBK 乱码
    if sys.stdout and hasattr(sys.stdout, 'buffer'):
        try:
            import io
            stream_handler.stream = io.TextIOWrapper(
                sys.stdout.buffer, encoding='utf-8', errors='replace'
            )
        except Exception:
            pass
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            stream_handler
        ]
    )
    
    return log_file

# 初始化日志
LOG_FILE = setup_logging()
logger = logging.getLogger(__name__)
logger.info(f"程序启动，日志文件: {LOG_FILE}")


class PDFMergeTool:
    """PDF 合并工具 GUI 类"""
    
    SUPPORTED_EXTENSIONS = {
        '文本文件': '*.txt',
        'PDF 文件': '*.pdf',
        '图片文件': '*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp',
        'Word 文档': '*.docx *.doc',
        'Excel 表格': '*.xlsx *.xls',
        'Outlook 邮件': '*.msg',
        '压缩包': '*.zip',
    }
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PDF 合并工具")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # 文件列表
        self.files: List[str] = []
        self.temp_pdf_files: List[str] = []
        
        # 消息队列（用于线程间通信）
        self.msg_queue = queue.Queue()
        
        # 纸张大小选择
        self.page_size_var = tk.StringVar(value="A4")
        
        # 创建界面
        self._create_widgets()
        
        # 启动消息处理
        self._process_queue()
    
    def _create_widgets(self):
        """创建所有界面组件"""
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== 文件列表区域 =====
        list_frame = ttk.LabelFrame(main_frame, text="文件列表", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 文件列表（带滚动条）
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.file_listbox = tk.Listbox(
            list_container,
            selectmode=tk.EXTENDED,
            height=15
        )
        
        scrollbar_y = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar_x = ttk.Scrollbar(list_container, orient=tk.HORIZONTAL, command=self.file_listbox.xview)
        
        self.file_listbox.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 文件操作按钮
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="添加文件", command=self._add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="添加文件夹", command=self._add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="移除选中", command=self._remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空列表", command=self._clear_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="上移", command=self._move_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="下移", command=self._move_down).pack(side=tk.LEFT, padx=5)
        
        # ===== 选项区域 =====
        options_frame = ttk.LabelFrame(main_frame, text="选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 添加页码选项
        self.add_page_numbers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="添加页码",
            variable=self.add_page_numbers_var
        ).pack(side=tk.LEFT, padx=10)
        
        # 页码位置
        ttk.Label(options_frame, text="页码位置:").pack(side=tk.LEFT, padx=(20, 5))
        self.page_number_position = ttk.Combobox(
            options_frame,
            values=['bottom-center', 'bottom-left', 'bottom-right', 'top-center'],
            width=15,
            state='readonly'
        )
        self.page_number_position.set('bottom-center')
        self.page_number_position.pack(side=tk.LEFT, padx=5)
        
        # 纸张大小
        ttk.Label(options_frame, text="纸张大小:").pack(side=tk.LEFT, padx=(20, 5))
        self.page_size_combo = ttk.Combobox(
            options_frame,
            textvariable=self.page_size_var,
            values=['A3', 'A4', 'Letter'],
            width=8,
            state='readonly'
        )
        self.page_size_combo.pack(side=tk.LEFT, padx=5)
        
        # 合并邮件附件选项
        self.include_msg_attachments_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="合并邮件附件",
            variable=self.include_msg_attachments_var
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        # ===== 输出文件区域 =====
        output_frame = ttk.LabelFrame(main_frame, text="输出", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="输出文件:").pack(side=tk.LEFT, padx=5)
        self.output_path_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "merged.pdf"))
        ttk.Entry(output_frame, textvariable=self.output_path_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="浏览...", command=self._browse_output).pack(side=tk.LEFT, padx=5)
        
        # ===== 进度条区域 =====
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10))
        
        self.status_label = ttk.Label(progress_frame, text="就绪", width=40)
        self.status_label.pack(side=tk.RIGHT)
        
        # ===== 底部按钮 =====
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X)
        
        # 左侧：查看日志按钮
        ttk.Button(
            bottom_frame,
            text="查看日志",
            command=self._open_log_folder
        ).pack(side=tk.LEFT, padx=5)
        
        # 右侧：开始和退出按钮
        ttk.Button(
            bottom_frame,
            text="开始合并",
            command=self._start_merge
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            bottom_frame,
            text="退出",
            command=self._on_closing
        ).pack(side=tk.RIGHT, padx=5)
    
    def _add_files(self):
        """添加文件到列表"""
        # 构建文件类型过滤器
        filetypes = [('所有支持的格式', ' '.join(self.SUPPORTED_EXTENSIONS.values()))]
        for name, ext in self.SUPPORTED_EXTENSIONS.items():
            filetypes.append((name, ext))
        filetypes.append(('所有文件', '*.*'))
        
        files = filedialog.askopenfilenames(filetypes=filetypes)
        
        for file_path in files:
            if file_path not in self.files:
                self.files.append(file_path)
                self.file_listbox.insert(tk.END, os.path.basename(file_path))
        
        # 如果添加了 .msg 文件，自动切换纸张大小为 A3
        has_msg = any(f.lower().endswith('.msg') for f in self.files)
        if has_msg:
            self.page_size_var.set("A3")
    
    def _add_folder(self):
        """添加文件夹中的所有支持文件"""
        folder = filedialog.askdirectory(title="选择文件夹")
        if not folder:
            return
        
        added = 0
        skipped = 0
        try:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if not os.path.isfile(file_path):
                    continue
                # 检查是否为支持的格式
                file_type = get_file_type(file_path)
                if file_type is None:
                    skipped += 1
                    continue
                # 去重（与 _add_files 一致）
                if file_path not in self.files:
                    self.files.append(file_path)
                    self.file_listbox.insert(tk.END, filename)
                    added += 1
                else:
                    skipped += 1
        except Exception as e:
            messagebox.showerror("错误", f"读取文件夹失败:\n{e}")
            return
        
        # 提示结果
        messagebox.showinfo("导入完成", f"已添加 {added} 个文件，跳过 {skipped} 个")
        
        # 如果添加了 .msg 文件，自动切换纸张大小为 A3
        has_msg = any(f.lower().endswith('.msg') for f in self.files)
        if has_msg:
            self.page_size_var.set("A3")
    
    def _remove_selected(self):
        """移除选中的文件"""
        selection = self.file_listbox.curselection()
        for index in reversed(selection):
            self.files.pop(index)
            self.file_listbox.delete(index)
    
    def _clear_list(self):
        """清空文件列表"""
        self.files.clear()
        self.file_listbox.delete(0, tk.END)
    
    def _move_up(self):
        """上移选中项"""
        selection = self.file_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        for index in selection:
            # 交换位置
            self.files[index], self.files[index - 1] = self.files[index - 1], self.files[index]
            
            # 更新列表显示
            item = self.file_listbox.get(index)
            self.file_listbox.delete(index)
            self.file_listbox.insert(index - 1, item)
            
            # 重新选中
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(index - 1)
    
    def _move_down(self):
        """下移选中项"""
        selection = self.file_listbox.curselection()
        if not selection or selection[-1] == len(self.files) - 1:
            return
        
        for index in reversed(selection):
            # 交换位置
            self.files[index], self.files[index + 1] = self.files[index + 1], self.files[index]
            
            # 更新列表显示
            item = self.file_listbox.get(index)
            self.file_listbox.delete(index)
            self.file_listbox.insert(index + 1, item)
            
            # 重新选中
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(index + 1)
    
    def _browse_output(self):
        """选择输出文件路径"""
        path = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[('PDF 文件', '*.pdf')],
            initialfile=os.path.basename(self.output_path_var.get())
        )
        if path:
            self.output_path_var.set(path)
    
    def _open_log_folder(self):
        """打开日志文件夹"""
        log_dir = os.path.join(os.path.expanduser("~"), "PDFMergeTool_logs")
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 打开文件夹
        import subprocess
        subprocess.Popen(f'explorer "{log_dir}"')
        
        logger.info(f"打开日志文件夹: {log_dir}")
    
    def _start_merge(self):
        """开始合并（在新线程中执行）"""
        if not self.files:
            messagebox.showwarning("警告", "请先添加要合并的文件")
            return
        
        output_path = self.output_path_var.get()
        if not output_path:
            messagebox.showwarning("警告", "请选择输出文件路径")
            return
        
        # 禁用按钮
        self._set_ui_enabled(False)
        
        # 重置进度
        self.progress_var.set(0)
        self.status_label.config(text="正在处理...")
        
        # 在新线程中执行合并
        page_size = self.page_size_var.get()
        thread = threading.Thread(
            target=self._merge_worker,
            args=(self.files.copy(), output_path, page_size),
            daemon=True
        )
        thread.start()
    
    def _merge_worker(self, files: List[str], output_path: str, page_size: str = 'A4'):
        """合并工作线程"""
        try:
            logger.info(f"开始合并任务，文件数: {len(files)}")
            logger.info(f"输出路径: {output_path}")
            logger.info(f"输入文件: {files}")
            
            page_pts = PAGE_SIZES.get(page_size, PAGE_SIZES['A4'])
            logger.info(f'Selected page size: {page_size} ({page_pts[0]:.0f}x{page_pts[1]:.0f} pts)')
            
            temp_dir = get_temp_dir()
            logger.info(f"临时目录: {temp_dir}")
            
            temp_pdf_files = []
            failed_files = []
            failed_count = 0
            total_steps = len(files) + 2  # 转换 + 合并 + 页码
            current_step = 0
            
            # 转换每个文件为 PDF
            for i, file_path in enumerate(files):
                file_type = get_file_type(file_path)
                temp_pdf = os.path.join(temp_dir, f"temp_{uuid.uuid4().hex[:8]}.pdf")
                
                logger.info(f"处理文件 [{i+1}/{len(files)}]: {file_path}, 类型: {file_type}")
                
                success = False
                error_msg = ""
                
                self.msg_queue.put(('status', f"转换中: {os.path.basename(file_path)}"))
                
                if file_type == 'pdf':
                    # 直接使用 PDF 文件
                    temp_pdf_files.append(file_path)
                    success = True
                    logger.info(f"PDF 文件直接添加: {file_path}")
                
                elif file_type == 'text':
                    success = txt_to_pdf(file_path, temp_pdf, page_size=page_pts)
                    if success:
                        temp_pdf_files.append(temp_pdf)
                        logger.info(f"TXT 转换成功: {temp_pdf}")
                    else:
                        error_msg = f"TXT 转换失败: {os.path.basename(file_path)}"
                        logger.error(error_msg)
                
                elif file_type == 'image':
                    success = image_to_pdf([file_path], temp_pdf, page_size=page_pts)
                    if success:
                        temp_pdf_files.append(temp_pdf)
                        logger.info(f"图片转换成功: {temp_pdf}")
                    else:
                        error_msg = f"图片转换失败: {os.path.basename(file_path)}"
                        logger.error(error_msg)
                
                elif file_type == 'word':
                    success, error = word_to_pdf(file_path, temp_pdf, page_size=page_pts)
                    if success:
                        temp_pdf_files.append(temp_pdf)
                        logger.info(f"Word 转换成功: {temp_pdf}")
                    else:
                        error_msg = error or f"Word 转换失败: {os.path.basename(file_path)}"
                        logger.error(f"Word 转换失败: {error}")
                
                elif file_type == 'excel':
                    success, error = excel_to_pdf(file_path, temp_dir, page_size=page_pts)
                    if success:
                        # Excel 转换输出文件名可能不同
                        base_name = os.path.splitext(os.path.basename(file_path))[0]
                        excel_pdf = os.path.join(temp_dir, f"{base_name}.pdf")
                        if os.path.exists(excel_pdf):
                            temp_pdf_files.append(excel_pdf)
                            logger.info(f"Excel 转换成功: {excel_pdf}")
                        else:
                            success = False
                            error_msg = "Excel PDF 输出文件未找到"
                            logger.error(error_msg)
                    else:
                        error_msg = error or f"Excel 转换失败: {os.path.basename(file_path)}"
                        logger.error(f"Excel 转换失败: {error}")
                
                elif file_type == 'msg':
                    # .msg 文件：提取附件并转换为 PDF（不包含邮件信息页）
                    from converters.msg_to_pdf import msg_to_pdf
                    success, error = msg_to_pdf(file_path, temp_pdf, include_info_page=False, page_size=page_pts,
                                                include_attachments=self.include_msg_attachments_var.get())
                    if success:
                        temp_pdf_files.append(temp_pdf)
                        logger.info(f"MSG 转换成功: {temp_pdf}")
                    else:
                        error_msg = error or f"MSG 转换失败: {os.path.basename(file_path)}"
                        logger.error(f"MSG 转换失败: {error}")
                
                else:
                    error_msg = f"不支持的文件类型: {os.path.basename(file_path)}"
                    logger.error(error_msg)
                
                # ── ZIP 文件处理 ──
                if file_type == 'zip':
                    from converters.zip_handler import extract_from_zip
                    success, extracted_files, error = extract_from_zip(file_path, temp_dir)
                    if success:
                        for extracted_file in extracted_files:
                            if extracted_file not in files:
                                files.append(extracted_file)
                                logger.info(f"Added from ZIP: {os.path.basename(extracted_file)}")
                    else:
                        error_msg = error or f"ZIP 解压失败: {os.path.basename(file_path)}"
                        logger.error(error_msg)
                        success = False
                
                if not success:
                    logger.error(f"文件转换失败 [{os.path.basename(file_path)}]: {error_msg}")
                    failed_files.append(os.path.basename(file_path))
                    failed_count += 1
                    # Auto-save crash dump
                    try:
                        from utils.crash_dump import save_crash_dump
                        crash_zip = save_crash_dump(error_msg, current_log_file=LOG_FILE, temp_dir=temp_dir)
                        if crash_zip:
                            error_msg += f"\n\n调试包已保存: {crash_zip}"
                    except Exception:
                        pass
                    self.msg_queue.put(('warning', f"跳过失败文件: {os.path.basename(file_path)}"))
                    current_step += 1
                    self.msg_queue.put(('progress', current_step / total_steps * 100))
                    continue
                
                current_step += 1
                self.msg_queue.put(('progress', current_step / total_steps * 100))
            
            if failed_count > 0:
                failed_list = "\n".join(f"  • {f}" for f in failed_files)
                logger.warning(f"部分文件转换失败 ({failed_count}/{len(files)}):\n{failed_list}")
            
            if not temp_pdf_files:
                logger.error("所有文件转换均失败，没有可合并的 PDF 文件")
                self.msg_queue.put(('error', "所有文件转换均失败，没有可合并的 PDF 文件"))
                return
            
            # 合并所有 PDF
            logger.info("开始合并 PDF...")
            self.msg_queue.put(('status', "正在合并 PDF..."))

            # Verify all PDF files still exist before merging
            for f in temp_pdf_files:
                if not os.path.exists(f):
                    logger.error(f"合并前文件丢失: {f}")

            merged_pdf = os.path.join(temp_dir, "merged_temp.pdf")
            success, error = merge_pdfs(temp_pdf_files, merged_pdf)
            
            if not success:
                logger.error(f"PDF 合并失败: {error}")
                self.msg_queue.put(('error', error or "PDF 合并失败"))
                return
            
            logger.info(f"PDF 合并成功: {merged_pdf}")
            
            current_step += 1
            self.msg_queue.put(('progress', current_step / total_steps * 100))
            
            # 添加页码（如果需要）
            if self.add_page_numbers_var.get():
                logger.info("开始添加页码...")
                self.msg_queue.put(('status', "正在添加页码..."))
                
                position = self.page_number_position.get()
                success = add_page_numbers(merged_pdf, output_path, position=position)
                
                if not success:
                    logger.warning("页码添加失败，使用无页码版本")
                    # 页码添加失败，使用无页码版本
                    import shutil
                    shutil.copy(merged_pdf, output_path)
                    self.msg_queue.put(('warning', "页码添加失败，已保存无页码版本"))
                else:
                    logger.info(f"页码添加成功: {output_path}")
            else:
                # 直接复制到输出路径
                import shutil
                shutil.copy(merged_pdf, output_path)
                logger.info(f"文件复制成功: {output_path}")
            
            # 完成
            logger.info(f"任务完成！输出文件: {output_path}")
            self.msg_queue.put(('progress', 100))
            self.msg_queue.put(('success', f"合并完成！\n输出文件: {output_path}"))
        
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"处理失败: {str(e)}\n{error_detail}")
            error_msg = f"处理失败: {str(e)}"
            try:
                from utils.crash_dump import save_crash_dump
                crash_zip = save_crash_dump(error_detail, current_log_file=LOG_FILE, temp_dir=temp_dir)
                if crash_zip:
                    error_msg += f"\n\n调试包已保存: {crash_zip}"
            except Exception:
                pass
            error_msg += f"\n\n日志文件: {LOG_FILE}"
            self.msg_queue.put(('error', error_msg))
        
        finally:
            # 清理临时文件（保留最终输出）
            # cleanup_temp_files()  # 可选：是否立即清理
            pass
    
    def _process_queue(self):
        """处理消息队列（在主线程中更新 UI）"""
        try:
            while True:
                msg_type, msg_data = self.msg_queue.get_nowait()
                
                if msg_type == 'status':
                    self.status_label.config(text=msg_data)
                
                elif msg_type == 'progress':
                    self.progress_var.set(msg_data)
                
                elif msg_type == 'error':
                    full_msg = (
                        "=" * 50 + "\n"
                        f"合并失败\n"
                        "=" * 50 + "\n\n"
                        f"{msg_data}"
                    )
                    messagebox.showerror("合并失败", full_msg)
                    logger.error(f"显示错误: {msg_data}")
                    self._set_ui_enabled(True)
                    self.status_label.config(text="处理失败")
                
                elif msg_type == 'warning':
                    messagebox.showwarning("警告", msg_data)
                    logger.warning(msg_data)
                
                elif msg_type == 'success':
                    messagebox.showinfo("成功", msg_data)
                    self._set_ui_enabled(True)
                    self.status_label.config(text="完成")
        
        except queue.Empty:
            pass
        
        # 继续检查队列
        self.root.after(100, self._process_queue)
    
    def _set_ui_enabled(self, enabled: bool):
        """启用/禁用界面元素"""
        state = tk.NORMAL if enabled else tk.DISABLED
        
        for widget in self.root.winfo_children():
            self._set_widgets_state(widget, enabled)
    
    def _set_widgets_state(self, widget, enabled: bool):
        """递归设置组件状态"""
        state = tk.NORMAL if enabled else tk.DISABLED
        
        try:
            widget.config(state=state)
        except tk.TclError:
            pass
        
        for child in widget.winfo_children():
            self._set_widgets_state(child, enabled)
    
    def _on_closing(self):
        """关闭窗口时的清理工作"""
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            cleanup_temp_files()
            self.root.destroy()


def merge_files_silent(files: List[str], output_path: str, add_page_nums: bool = True, page_position: str = 'bottom-center', page_size: str = 'A4') -> tuple[bool, str]:
    """
    静默合并文件（无 GUI）
    
    Args:
        files: 文件路径列表
        output_path: 输出文件路径
        add_page_nums: 是否添加页码
        page_position: 页码位置
        page_size: 纸张大小（A3/A4/Letter）
    
    Returns:
        (是否成功, 消息)
    """
    try:
        logger.info(f"开始静默合并，文件数: {len(files)}")
        logger.info(f"输出路径: {output_path}")
        
        page_pts = PAGE_SIZES.get(page_size, PAGE_SIZES['A4'])
        
        temp_dir = get_temp_dir()
        logger.info(f"临时目录: {temp_dir}")
        
        # Phase 0: Build complete file list (expand ZIPs upfront so we know all files)
        all_files = list(files)
        i = 0
        while i < len(all_files):
            fp = all_files[i]
            if not os.path.exists(fp):
                return False, f"文件不存在: {fp}"
            ft = get_file_type(fp)
            if ft == 'zip':
                from converters.zip_handler import extract_from_zip
                success, extracted_files, error = extract_from_zip(fp, temp_dir)
                if not success:
                    return False, error or f"ZIP 解压失败: {os.path.basename(fp)}"
                for ef in extracted_files:
                    if ef not in all_files:
                        all_files.append(ef)
                        logger.info(f"Added from ZIP: {os.path.basename(ef)}")
            i += 1
        
        total = len(all_files)
        logger.info(f"开始转换，总文件数（含 ZIP 内文件）: {total}")
        
        # Phase 1: Parallel conversion with ThreadPoolExecutor
        logger.info(f"[已转换 0/{total}] 文件处理中...")
        
        temp_pdf_files = [None] * total  # placeholder list for ordered results
        word_excel_queue = []  # (index, file_path, file_type, temp_pdf_path)
        skipped_count = 0
        failed_files = []
        failed_count = 0
        
        import concurrent.futures
        
        def convert_in_thread(idx, fp, ft):
            """Thread-safe conversion for non-COM file types (TXT/Image/msg)"""
            temp_pdf = os.path.join(temp_dir, f"temp_{uuid.uuid4().hex[:8]}.pdf")
            logger.info(f"处理文件 [{idx+1}/{total}]: {fp}, 类型: {ft}")
            
            if ft == 'text':
                ok = txt_to_pdf(fp, temp_pdf, page_size=page_pts)
                if ok:
                    return (idx, temp_pdf, None)
                else:
                    return (idx, None, f"TXT 转换失败: {os.path.basename(fp)}")
            elif ft == 'image':
                ok = image_to_pdf([fp], temp_pdf, page_size=page_pts)
                if ok:
                    return (idx, temp_pdf, None)
                else:
                    return (idx, None, f"图片转换失败: {os.path.basename(fp)}")
            elif ft == 'msg':
                from converters.msg_to_pdf import msg_to_pdf
                ok, err = msg_to_pdf(fp, temp_pdf, include_info_page=False, page_size=page_pts,
                                   include_attachments=True)
                if ok:
                    if os.path.exists(temp_pdf):
                        return (idx, temp_pdf, None)
                    else:
                        # No attachments - skip gracefully
                        logger.info(f"MSG 文件无附件，跳过: {os.path.basename(fp)}")
                        return (idx, None, 'SKIPPED')
                else:
                    return (idx, None, err or f"MSG 转换失败: {os.path.basename(fp)}")
            else:
                return (idx, None, f"不支持的文件类型: {os.path.basename(fp)}")
        
        # Submit non-COM conversions to thread pool (3 workers)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}
            for idx, fp in enumerate(all_files):
                ft = get_file_type(fp)
                if ft == 'pdf':
                    temp_pdf_files[idx] = fp
                    logger.info(f"PDF 文件直接添加: {fp}")
                elif ft in ('word', 'excel'):
                    temp_pdf = os.path.join(temp_dir, f"temp_{uuid.uuid4().hex[:8]}.pdf")
                    word_excel_queue.append((idx, fp, ft, temp_pdf))
                elif ft == 'zip':
                    continue  # Already extracted in Phase 0
                elif ft is not None:
                    futures[executor.submit(convert_in_thread, idx, fp, ft)] = idx
                else:
                    logger.error(f"不支持的文件类型: {os.path.basename(fp)}")
                    failed_files.append(os.path.basename(fp))
                    failed_count += 1
            
            # Collect thread pool results
            for future in concurrent.futures.as_completed(futures):
                idx, temp_pdf, error = future.result()
                if temp_pdf is not None:
                    temp_pdf_files[idx] = temp_pdf
                elif error == 'SKIPPED':
                    skipped_count += 1
                else:
                    logger.error(error)
                    failed_files.append(os.path.basename(all_files[idx]))
                    failed_count += 1
        
        # Phase 2: Word/Excel conversions sequentially in main thread (COM requires STA)
        for idx, fp, ft, temp_pdf in word_excel_queue:
            logger.info(f"处理文件 [{idx+1}/{total}]: {fp}, 类型: {ft}")
            if ft == 'word':
                ok, err = word_to_pdf(fp, temp_pdf, page_size=page_pts)
                if ok:
                    temp_pdf_files[idx] = temp_pdf
                else:
                    error_msg = err or f"Word 转换失败: {os.path.basename(fp)}"
                    logger.error(error_msg)
                    failed_files.append(os.path.basename(fp))
                    failed_count += 1
                    continue
            elif ft == 'excel':
                ok, err = excel_to_pdf(fp, temp_dir, page_size=page_pts)
                if ok:
                    base_name = os.path.splitext(os.path.basename(fp))[0]
                    excel_pdf = os.path.join(temp_dir, f"{base_name}.pdf")
                    if os.path.exists(excel_pdf):
                        temp_pdf_files[idx] = excel_pdf
                    else:
                        error_msg = "Excel PDF 输出文件未找到"
                        logger.error(error_msg)
                        failed_files.append(os.path.basename(fp))
                        failed_count += 1
                        continue
                else:
                    error_msg = err or f"Excel 转换失败: {os.path.basename(fp)}"
                    logger.error(error_msg)
                    failed_files.append(os.path.basename(fp))
                    failed_count += 1
                    continue
        
        # Progress complete
        logger.info(f"[已转换 {total}/{total}] 文件处理中...")
        
        # Filter out None entries (skipped .msg files with no attachments)
        temp_pdf_files = [f for f in temp_pdf_files if f is not None]
        
        if not temp_pdf_files:
            return False, "没有可合并的 PDF 文件"
        
        # 合并所有 PDF
        logger.info("开始合并 PDF...")
        merged_pdf = os.path.join(temp_dir, "merged_temp.pdf")
        success, error = merge_pdfs(temp_pdf_files, merged_pdf)
        
        if not success:
            logger.error(f"PDF 合并失败: {error}")
            return False, error or "PDF 合并失败"
        
        logger.info(f"PDF 合并成功: {merged_pdf}")
        
        # 添加页码（如果需要）
        if add_page_nums:
            logger.info("开始添加页码...")
            success = add_page_numbers(merged_pdf, output_path, position=page_position)
            
            if not success:
                logger.warning("页码添加失败，使用无页码版本")
                import shutil
                shutil.copy(merged_pdf, output_path)
            else:
                logger.info(f"页码添加成功: {output_path}")
        else:
            import shutil
            shutil.copy(merged_pdf, output_path)
            logger.info(f"文件复制成功: {output_path}")
        
        # 完成
        success_msg = output_path
        parts = []
        if skipped_count > 0:
            parts.append(f"跳过 {skipped_count} 个无附件邮件")
        if failed_count > 0:
            parts.append(f"{failed_count} 个文件转换失败")
        if parts:
            success_msg += " (" + ", ".join(parts) + ")"
        logger.info(f"任务完成！输出文件: {success_msg}")
        return True, success_msg
    
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.error(f"处理失败: {str(e)}\n{error_detail}")
        error_msg = f"处理失败: {str(e)}"
        try:
            from utils.crash_dump import save_crash_dump
            crash_zip = save_crash_dump(error_detail, current_log_file=LOG_FILE, temp_dir=temp_dir)
            if crash_zip:
                error_msg += f" | 调试包: {crash_zip}"
        except Exception:
            pass
        return False, error_msg


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='PDF 合并工具')
    parser.add_argument('--files', nargs='+', help='要合并的文件列表')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--auto', action='store_true', help='自动合并模式（不显示 GUI）')
    parser.add_argument('--no-page-numbers', action='store_true', help='不添加页码')
    parser.add_argument('--page-position', default='bottom-center', 
                       choices=['bottom-center', 'bottom-left', 'bottom-right', 'top-center'],
                       help='页码位置')
    parser.add_argument('--page-size', choices=['A3','A4','Letter'], default='A4', help='输出纸张大小')
    return parser.parse_args()


def main():
    """主函数"""
    # 强制 stderr 使用 UTF-8，避免中文 Windows GBK 乱码
    # （当被 OutlookAgent 作为子进程调用时，merge_launcher 期望 UTF-8）
    if sys.stderr and hasattr(sys.stderr, 'buffer'):
        try:
            import io
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding='utf-8', errors='replace'
            )
        except Exception:
            pass
    
    args = parse_args()
    
    # 自动合并模式
    if args.auto and args.files:
        # 确定输出路径
        if args.output:
            output_path = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(os.path.expanduser("~"), f"merged_{timestamp}.pdf")
        
        # 执行合并
        success, message = merge_files_silent(
            files=args.files,
            output_path=output_path,
            add_page_nums=not args.no_page_numbers,
            page_position=args.page_position,
            page_size=args.page_size
        )
        
        if success:
            logger.info(f"Success: {message}")
            sys.exit(0)
        else:
            logger.error(f"Failed: {message}")
            sys.exit(1)
    
    # GUI 模式
    root = tk.Tk()
    
    # 设置窗口图标（如果有）
    try:
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    app = PDFMergeTool(root)
    root.protocol("WM_DELETE_WINDOW", app._on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()

