# -*- coding: utf-8 -*-
"""
多系统表单工具 - 启动器
支持多系统切换（CSMS, Acubuy, SAP 等）
启动对应的专用程序
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import subprocess
import sys
from datetime import datetime


class SystemLauncher:
    """多系统启动器"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("多系统表单工具 - 启动器")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        # 基础目录
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 配置
        self.systems = []
        self.flows = []
        self.current_system = None
        self.current_flow = None
        
        # 加载配置
        self._load_config()
        
        # 创建界面
        self._create_widgets()
        
        # 日志
        self._log("启动器已就绪")
    
    def _load_config(self):
        """加载系统和流程配置"""
        # 加载系统配置
        system_config_path = os.path.join(self.base_dir, 'system_config.json')
        if os.path.exists(system_config_path):
            try:
                with open(system_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.systems = config.get('systems', [])
                    self.flows = config.get('flows', [])
                self._log(f"已加载 {len(self.systems)} 个系统，{len(self.flows)} 个流程")
            except Exception as e:
                self._log(f"加载配置失败：{e}")
                messagebox.showerror("错误", f"加载系统配置失败:\n{e}")
        else:
            self._log("警告：system_config.json 不存在")
            # 创建默认配置
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认系统配置"""
        default_config = {
            "version": "1.0",
            "systems": [
                {
                    "system_id": "csms",
                    "system_name": "CSMS",
                    "file": "systems/csms.json",
                    "icon": "🏢",
                    "description": "Contract & Supplier Management System",
                    "programs": {
                        "proposal": "auto_create_proposal.py",
                        "form": "form_filler.py"
                    }
                },
                {
                    "system_id": "acubuy",
                    "system_name": "Acubuy",
                    "file": "systems/acubuy.json",
                    "icon": "🛒",
                    "description": "Procurement Management System",
                    "programs": {
                        "form": "form_filler.py"
                    }
                },
                {
                    "system_id": "sap",
                    "system_name": "SAP",
                    "file": "systems/sap.json",
                    "icon": "📊",
                    "description": "SAP ERP System",
                    "programs": {
                        "form": "form_filler.py"
                    }
                }
            ],
            "flows": []
        }
        
        try:
            with open(os.path.join(self.base_dir, 'system_config.json'), 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            self._log("已创建默认系统配置")
            self.systems = default_config["systems"]
        except Exception as e:
            self._log(f"创建默认配置失败：{e}")
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== 标题 =====
        title_label = ttk.Label(
            main_frame,
            text="🚀 多系统表单工具",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(
            main_frame,
            text="选择系统和流程，启动对应的程序",
            font=('Arial', 10)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # ===== 系统选择区域 =====
        system_frame = ttk.LabelFrame(main_frame, text="1️⃣ 选择系统", padding=15)
        system_frame.pack(fill=tk.X, pady=10)
        
        self.system_var = tk.StringVar()
        system_names = [f"{s.get('icon', '')} {s.get('system_name', '')}" for s in self.systems]
        
        self.system_combo = ttk.Combobox(
            system_frame,
            textvariable=self.system_var,
            values=system_names,
            state='readonly',
            width=40,
            font=('Arial', 11)
        )
        self.system_combo.pack(pady=10)
        self.system_combo.bind('<<ComboboxSelected>>', self._on_system_changed)
        
        if self.systems:
            self.system_combo.current(0)
            self._on_system_changed(None)
        
        # 系统信息
        self.system_info_text = tk.Text(system_frame, height=4, width=60, state=tk.DISABLED, bg='#f0f0f0')
        self.system_info_text.pack(pady=10)
        
        # ===== 流程选择区域 =====
        flow_frame = ttk.LabelFrame(main_frame, text="2️⃣ 选择流程", padding=15)
        flow_frame.pack(fill=tk.X, pady=10)
        
        self.flow_var = tk.StringVar()
        self.flow_combo = ttk.Combobox(
            flow_frame,
            textvariable=self.flow_var,
            state='readonly',
            width=40,
            font=('Arial', 11)
        )
        self.flow_combo.pack(pady=10)
        self.flow_combo.bind('<<ComboboxSelected>>', self._on_flow_selected)
        
        # 流程描述
        self.flow_desc_label = ttk.Label(flow_frame, text="", foreground='gray', wraplength=500)
        self.flow_desc_label.pack(pady=5)
        
        # ===== 程序选择区域 =====
        program_frame = ttk.LabelFrame(main_frame, text="3️⃣ 选择程序", padding=15)
        program_frame.pack(fill=tk.X, pady=10)
        
        self.program_var = tk.StringVar(value="auto")
        
        program_container = ttk.Frame(program_frame)
        program_container.pack()
        
        self.radio_proposal = ttk.Radiobutton(
            program_container,
            text="📄 提案创建 (auto_create_proposal.py)",
            variable=self.program_var,
            value="proposal"
        )
        self.radio_proposal.pack(anchor=tk.W, pady=5)
        
        self.radio_form = ttk.Radiobutton(
            program_container,
            text="📝 表单填写 (form_filler.py)",
            variable=self.program_var,
            value="form"
        )
        self.radio_form.pack(anchor=tk.W, pady=5)
        
        self.radio_auto = ttk.Radiobutton(
            program_container,
            text="⚙️ 自动推荐",
            variable=self.program_var,
            value="auto"
        )
        self.radio_auto.pack(anchor=tk.W, pady=5)
        
        self.radio_auto.invoke()  # 默认选中自动
        
        # ===== 启动按钮 =====
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        self.btn_launch = ttk.Button(
            btn_frame,
            text="🚀 启动程序",
            command=self._launch,
            width=20
        )
        self.btn_launch.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame,
            text="📂 打开配置目录",
            command=self._open_config_dir,
            width=15
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame,
            text="❓ 帮助",
            command=self._show_help,
            width=10
        ).pack(side=tk.LEFT, padx=10)
        
        # ===== 日志区域 =====
        log_frame = ttk.LabelFrame(main_frame, text="📋 日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, width=70, state=tk.DISABLED, bg='#f5f5f5', font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 日志标签
        self.log_text.tag_config('INFO', foreground='black')
        self.log_text.tag_config('WARNING', foreground='orange')
        self.log_text.tag_config('ERROR', foreground='red')
        self.log_text.tag_config('SUCCESS', foreground='green')
    
    def _on_system_changed(self, event):
        """系统选择变更"""
        idx = self.system_combo.current()
        if idx < 0 or idx >= len(self.systems):
            return
        
        self.current_system = self.systems[idx]
        system_name = self.current_system.get('system_name', '')
        system_desc = self.current_system.get('description', '')
        system_id = self.current_system.get('system_id', '')
        
        # 更新系统信息
        self.system_info_text.config(state=tk.NORMAL)
        self.system_info_text.delete(1.0, tk.END)
        self.system_info_text.insert(tk.END, f"系统：{system_name}\n")
        self.system_info_text.insert(tk.END, f"ID: {system_id}\n")
        self.system_info_text.insert(tk.END, f"说明：{system_desc}\n")
        self.system_info_text.config(state=tk.DISABLED)
        
        # 更新流程列表
        system_flows = [f for f in self.flows if f.get('system_id') == system_id]
        flow_names = [f"{f.get('icon', '')} {f.get('flow_name', '')}" for f in system_flows]
        self.flow_combo['values'] = flow_names
        
        if system_flows:
            self.flow_combo.current(0)
            self._on_flow_selected(None)
        else:
            self.flow_combo['values'] = []
            self.flow_var.set("")
            self.flow_desc_label.config(text="")
        
        # 更新程序选项
        programs = self.current_system.get('programs', {})
        if 'proposal' not in programs:
            self.radio_proposal.config(state=tk.DISABLED)
        else:
            self.radio_proposal.config(state=tk.NORMAL)
        
        self._log(f"已选择系统：{system_name}")
    
    def _on_flow_selected(self, event):
        """流程选择变更"""
        idx = self.flow_combo.current()
        if idx < 0:
            return
        
        system_id = self.current_system.get('system_id', '') if self.current_system else ''
        system_flows = [f for f in self.flows if f.get('system_id') == system_id]
        
        if idx < len(system_flows):
            self.current_flow = system_flows[idx]
            flow_desc = self.current_flow.get('description', '')
            self.flow_desc_label.config(text=flow_desc)
    
    def _launch(self):
        """启动程序"""
        if not self.current_system:
            messagebox.showwarning("警告", "请先选择系统")
            return
        
        # 确定要启动的程序
        program = self._determine_program()
        if not program:
            messagebox.showwarning("警告", "无法确定要启动的程序")
            return
        
        # 检查程序是否存在
        program_path = os.path.join(self.base_dir, program)
        if not os.path.exists(program_path):
            messagebox.showerror("错误", f"程序不存在:\n{program}")
            return
        
        # 启动程序
        try:
            self._log(f"启动程序：{program}")
            subprocess.Popen([sys.executable, program], cwd=self.base_dir)
            self._log(f"✓ 程序已启动：{program}", 'SUCCESS')
            
            # 最小化启动器窗口
            self.root.iconify()
            
        except Exception as e:
            self._log(f"启动失败：{e}", 'ERROR')
            messagebox.showerror("错误", f"启动程序失败:\n{e}")
    
    def _determine_program(self):
        """确定要启动的程序"""
        program_choice = self.program_var.get()
        
        if program_choice == 'auto':
            # 自动推荐
            if self.current_flow:
                flow_id = self.current_flow.get('flow_id', '')
                if 'proposal' in flow_id.lower() or 'create_proposal' in flow_id:
                    return 'auto_create_proposal.py'
            return 'form_filler.py'
        
        elif program_choice == 'proposal':
            return 'auto_create_proposal.py'
        
        elif program_choice == 'form':
            return 'form_filler.py'
        
        return None
    
    def _open_config_dir(self):
        """打开配置目录"""
        systems_dir = os.path.join(self.base_dir, 'systems')
        if not os.path.exists(systems_dir):
            os.makedirs(systems_dir)
        
        subprocess.Popen(f'explorer "{systems_dir}"')
        self._log("已打开系统配置目录")
    
    def _show_help(self):
        """显示帮助"""
        help_text = """
🚀 多系统表单工具 - 使用说明

1️⃣ 选择系统
   - 从下拉列表中选择目标系统
   - 查看系统信息和说明

2️⃣ 选择流程
   - 根据系统自动过滤流程
   - 查看流程描述

3️⃣ 选择程序
   - 自动推荐：根据流程自动选择
   - 提案创建：启动 auto_create_proposal.py
   - 表单填写：启动 form_filler.py

4️⃣ 启动程序
   - 点击"启动程序"按钮
   - 启动器最小化到任务栏

📂 配置目录
   - 点击"打开配置目录"
   - 编辑系统配置文件

⚙️ 添加新系统
   1. 在 systems/ 目录创建系统配置文件
   2. 编辑 system_config.json 添加系统信息
   3. 重启启动器

📋 日志
   - 所有操作记录在下方日志区
   - 绿色表示成功，红色表示错误
"""
        messagebox.showinfo("帮助", help_text)
    
    def _log(self, message, level='INFO'):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def run(self):
        """运行启动器"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出启动器吗？"):
            self.root.destroy()


if __name__ == '__main__':
    app = SystemLauncher()
    app.run()
