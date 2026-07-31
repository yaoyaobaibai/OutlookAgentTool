# -*- coding: utf-8 -*-
"""
多系统流程自动化 - 主程序 (支持系统切换)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
import threading
import queue
from typing import Dict, List, Any, Optional

from flow_engine import FlowEngine, SystemManager, FlowManager


class MultiSystemFlowApp:
    """
    多系统流程自动化 GUI 应用
    支持：
    - 多系统切换
    - 流程选择
    - 变量配置
    - 执行进度显示
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("多系统流程自动化")
        self.root.geometry("1000x700")
        
        # 基础目录
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 管理器
        self.system_manager = SystemManager(self.base_dir)
        self.flow_manager = FlowManager(self.base_dir)
        self.flow_engine = FlowEngine(self.base_dir)
        
        # 配置
        self.system_config: Optional[Dict[str, Any]] = None
        self.current_system_id: str = ""
        self.current_flow_id: str = ""
        
        # 变量配置
        self.variables: Dict[str, str] = {}
        
        # 执行状态
        self.is_running = False
        self.msg_queue = queue.Queue()
        
        # 创建界面
        self._create_widgets()
        
        # 加载配置
        self._load_config()
        
        # 启动消息处理
        self._process_queue()
    
    def _create_widgets(self):
        """创建所有界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== 顶部：系统和流程选择 =====
        top_frame = ttk.LabelFrame(main_frame, text="流程配置", padding="10")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 第一行：系统选择
        sys_frame = ttk.Frame(top_frame)
        sys_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sys_frame, text="选择系统:", width=12).pack(side=tk.LEFT, padx=5)
        
        self.system_var = tk.StringVar()
        self.system_combo = ttk.Combobox(
            sys_frame,
            textvariable=self.system_var,
            state='readonly',
            width=30
        )
        self.system_combo.pack(side=tk.LEFT, padx=5)
        self.system_combo.bind('<<ComboboxSelected>>', self._on_system_changed)
        
        self.system_info_label = ttk.Label(sys_frame, text="", foreground='blue')
        self.system_info_label.pack(side=tk.LEFT, padx=20)
        
        # 第二行：流程选择
        flow_frame = ttk.Frame(top_frame)
        flow_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(flow_frame, text="选择流程:", width=12).pack(side=tk.LEFT, padx=5)
        
        self.flow_var = tk.StringVar()
        self.flow_combo = ttk.Combobox(
            flow_frame,
            textvariable=self.flow_var,
            state='readonly',
            width=30
        )
        self.flow_combo.pack(side=tk.LEFT, padx=5)
        self.flow_combo.bind('<<ComboboxSelected>>', self._on_flow_selected)
        
        self.flow_desc_label = ttk.Label(flow_frame, text="", foreground='gray')
        self.flow_desc_label.pack(side=tk.LEFT, padx=20)
        
        # ===== 中部：变量配置 =====
        mid_frame = ttk.LabelFrame(main_frame, text="变量配置", padding="10")
        mid_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 变量配置区域 (带滚动条)
        var_canvas = tk.Canvas(mid_frame)
        var_scrollbar = ttk.Scrollbar(mid_frame, orient="vertical", command=var_canvas.yview)
        self.var_scrollable_frame = ttk.Frame(var_canvas)
        
        self.var_scrollable_frame.bind(
            "<Configure>",
            lambda e: var_canvas.configure(scrollregion=var_canvas.bbox("all"))
        )
        
        var_canvas.create_window((0, 0), window=self.var_scrollable_frame, anchor="nw")
        var_canvas.configure(yscrollcommand=var_scrollbar.set)
        
        var_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        var_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 变量配置网格
        self.var_widgets = {}  # 存储变量输入框
        
        # ===== 底部：执行控制 =====
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 进度条
        progress_frame = ttk.Frame(bottom_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="就绪", width=50)
        self.progress_label.pack(side=tk.RIGHT)
        
        # 按钮
        btn_frame = ttk.Frame(bottom_frame)
        btn_frame.pack(fill=tk.X)
        
        self.btn_start = ttk.Button(
            btn_frame,
            text="▶ 开始执行",
            command=self._start_execution,
            width=15
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = ttk.Button(
            btn_frame,
            text="⏹ 停止",
            command=self._stop_execution,
            state=tk.DISABLED,
            width=15
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="📂 打开日志目录",
            command=self._open_log_dir,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="❓ 帮助",
            command=self._show_help,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # ===== 日志区域 =====
        log_frame = ttk.LabelFrame(main_frame, text="执行日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 日志标签颜色
        self.log_text.tag_config('INFO', foreground='black')
        self.log_text.tag_config('WARNING', foreground='orange')
        self.log_text.tag_config('ERROR', foreground='red')
        self.log_text.tag_config('SUCCESS', foreground='green')
    
    def _load_config(self):
        """加载系统配置"""
        try:
            config_path = os.path.join(self.base_dir, 'system_config.json')
            if not os.path.exists(config_path):
                self._log("系统配置文件不存在", 'ERROR')
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                self.system_config = json.load(f)
            
            # 加载系统列表
            systems = self.system_config.get('systems', [])
            system_names = [f"{s.get('icon', '')} {s.get('system_name', '')}" for s in systems]
            self.system_combo['values'] = system_names
            
            if systems:
                self.system_combo.current(0)
                self._on_system_changed(None)
            
            self._log(f"已加载 {len(systems)} 个系统配置", 'INFO')
            
        except Exception as e:
            self._log(f"加载配置失败：{e}", 'ERROR')
    
    def _on_system_changed(self, event):
        """系统切换事件"""
        idx = self.system_combo.current()
        if idx < 0:
            return
        
        system_info = self.system_config['systems'][idx]
        system_id = system_info['system_id']
        self.current_system_id = system_id
        
        # 更新系统信息
        system_file = system_info['file']
        system_path = os.path.join(self.base_dir, 'systems', system_file)
        
        try:
            with open(system_path, 'r', encoding='utf-8') as f:
                system_config = json.load(f)
            
            base_url = system_config.get('base_url', '未配置')
            self.system_info_label.config(text=f"URL: {base_url}")
        except Exception as e:
            self.system_info_label.config(text=f"加载失败：{e}")
        
        # 加载系统配置到引擎
        self.flow_engine.load_system(system_file)
        
        # 更新流程列表 (只显示当前系统的流程)
        flows = [f for f in self.system_config.get('flows', []) if f.get('system_id') == system_id]
        flow_names = [f"{f.get('icon', '')} {f.get('flow_name', '')}" for f in flows]
        self.flow_combo['values'] = flow_names
        
        if flows:
            self.flow_combo.current(0)
            self._on_flow_selected(None)
        else:
            self.flow_combo['values'] = []
            self.flow_var.set("")
        
        self._log(f"切换到系统：{system_config.get('system_name', '')}", 'INFO')
    
    def _on_flow_selected(self, event):
        """流程选择事件"""
        idx = self.flow_combo.current()
        if idx < 0:
            return
        
        flow_info = None
        system_id = self.current_system_id
        flows = [f for f in self.system_config.get('flows', []) if f.get('system_id') == system_id]
        
        if idx < len(flows):
            flow_info = flows[idx]
            self.current_flow_id = flow_info.get('flow_id', '')
        
        # 更新流程描述
        if flow_info:
            desc = flow_info.get('description', '')
            self.flow_desc_label.config(text=desc)
            
            # 加载流程配置
            flow_file = flow_info.get('file', '')
            self.flow_engine.load_flow(flow_file)
            
            # 更新变量配置区域
            self._update_variable_fields(flow_file)
        else:
            self.flow_desc_label.config(text="")
    
    def _update_variable_fields(self, flow_file: str):
        """更新变量配置区域"""
        try:
            # 清空现有变量框
            for widget in self.var_scrollable_frame.winfo_children():
                widget.destroy()
            self.var_widgets = {}
            
            # 读取流程配置
            flow_path = os.path.join(self.base_dir, 'flows', flow_file)
            with open(flow_path, 'r', encoding='utf-8') as f:
                flow_config = json.load(f)
            
            variables = flow_config.get('variables', {})
            
            # 创建变量输入框
            row = 0
            for var_name, default_value in variables.items():
                label = ttk.Label(
                    self.var_scrollable_frame,
                    text=var_name + ":",
                    width=25,
                    anchor='e'
                )
                label.grid(row=row, column=0, sticky=tk.E, pady=5, padx=10)
                
                entry = ttk.Entry(self.var_scrollable_frame, width=50)
                entry.insert(0, str(default_value))
                entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=10)
                
                self.var_widgets[var_name] = entry
                
                row += 1
            
        except Exception as e:
            self._log(f"更新变量配置失败：{e}", 'ERROR')
    
    def _start_execution(self):
        """开始执行流程"""
        if self.is_running:
            messagebox.showwarning("警告", "流程正在执行中")
            return
        
        # 收集变量值
        for var_name, entry in self.var_widgets.items():
            value = entry.get().strip()
            self.flow_engine.set_variable(var_name, value)
        
        # 更新 UI 状态
        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.system_combo.config(state=tk.DISABLED)
        self.flow_combo.config(state=tk.DISABLED)
        
        # 在新线程中执行
        thread = threading.Thread(target=self._execute_thread, daemon=True)
        thread.start()
    
    def _execute_thread(self):
        """执行线程"""
        try:
            self._log("="*50, 'INFO')
            self._log("开始执行流程...", 'INFO')
            
            success = self.flow_engine.execute_flow_async(self.msg_queue)
            
            if success:
                self._log("流程执行完成!", 'SUCCESS')
                self.msg_queue.put(('complete', True, "流程执行成功"))
            else:
                self._log("流程执行失败", 'ERROR')
                self.msg_queue.put(('complete', False, "流程执行失败"))
        
        except Exception as e:
            self._log(f"执行异常：{e}", 'ERROR')
            self.msg_queue.put(('error', str(e)))
        
        finally:
            self.is_running = False
    
    def _stop_execution(self):
        """停止执行"""
        if messagebox.askyesno("确认", "确定要停止当前流程吗？"):
            self.flow_engine.is_running = False
            self._log("用户请求停止", 'WARNING')
    
    def _process_queue(self):
        """处理消息队列"""
        try:
            while True:
                msg = self.msg_queue.get_nowait()
                msg_type = msg[0]
                
                if msg_type == 'step_start':
                    step, total, name = msg[1], msg[2], msg[3]
                    self.progress_label.config(text=f"步骤 [{step}/{total}]: {name}")
                    self.progress_var.set((step - 1) / total * 100)
                    self._log(f"→ 步骤 [{step}/{total}]: {name}", 'INFO')
                
                elif msg_type == 'step_complete':
                    step, total, name, success = msg[1], msg[2], msg[3], msg[4]
                    if success:
                        self._log(f"✓ 步骤完成：{name}", 'SUCCESS')
                    else:
                        self._log(f"✗ 步骤失败：{name}", 'ERROR')
                
                elif msg_type == 'error':
                    error = msg[1]
                    self._log(f"❌ 错误：{error}", 'ERROR')
                
                elif msg_type == 'complete':
                    success, message = msg[1], msg[2]
                    self.progress_var.set(100)
                    
                    if success:
                        self.progress_label.config(text="完成")
                        messagebox.showinfo("成功", message)
                    else:
                        self.progress_label.config(text="失败")
                        messagebox.showerror("失败", message)
                    
                    # 恢复 UI 状态
                    self.btn_start.config(state=tk.NORMAL)
                    self.btn_stop.config(state=tk.DISABLED)
                    self.system_combo.config(state=tk.NORMAL)
                    self.flow_combo.config(state=tk.NORMAL)
        
        except queue.Empty:
            pass
        
        # 继续检查队列
        self.root.after(100, self._process_queue)
    
    def _log(self, message: str, level: str = 'INFO'):
        """添加日志"""
        timestamp = f"[{threading.current_thread().name}] " if threading.current_thread().name != 'MainThread' else ""
        log_entry = f"{timestamp}{message}"
        
        self.log_text.insert(tk.END, log_entry + "\n", level)
        self.log_text.see(tk.END)
    
    def _open_log_dir(self):
        """打开日志目录"""
        log_dir = os.path.join(os.path.expanduser("~"), "FlowAutomation_logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        import subprocess
        subprocess.Popen(f'explorer "{log_dir}"')
    
    def _show_help(self):
        """显示帮助"""
        help_text = """
多系统流程自动化 - 使用说明

1. 选择系统
   - 从下拉列表中选择目标系统 (CSMS, Acubuy, SAP 等)
   - 系统 URL 会显示在右侧

2. 选择流程
   - 选择要执行的流程
   - 流程描述会显示在右侧

3. 配置变量
   - 在变量配置区域填写所需参数
   - 变量来自流程配置

4. 开始执行
   - 点击"开始执行"按钮
   - 观察执行进度和日志

5. 添加新系统
   - 在 systems/ 目录创建系统配置文件
   - 在 system_config.json 中添加系统信息

6. 添加新流程
   - 在 flows/ 目录创建流程配置文件
   - 在 system_config.json 中添加流程信息
"""
        messagebox.showinfo("帮助", help_text)
    
    def run(self):
        """运行应用"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """关闭事件"""
        if self.is_running:
            if not messagebox.askyesno("确认", "流程正在执行，确定要退出吗？"):
                return
        
        self.flow_engine.close_browser()
        self.root.destroy()


if __name__ == '__main__':
    app = MultiSystemFlowApp()
    app.run()
