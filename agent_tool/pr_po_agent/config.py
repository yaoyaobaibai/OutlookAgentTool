# -*- coding: utf-8 -*-
"""PR/PO Agent - 配置文件"""

# 版本
VERSION = "1.3.4-dev"

# 应用标题
APP_TITLE = "PR/PO 助手"

# 主窗口尺寸
DEFAULT_WINDOW_SIZE = "900x600"
PDF_MERGE_TOOL_PATH = ""

# 字体配置
DEFAULT_FONT = ("Microsoft YaHei", 10)
DEFAULT_FONT_BOLD = ("Microsoft YaHei", 11, "bold")
TITLE_FONT = ("Microsoft YaHei", 28, "bold")
MONITOR_FONT = ("Microsoft YaHei", 9)

# 统计面板默认值
STATS = {
    "pending": 3,
    "processing": 2,
    "completed": 15,
}

# 统计标签
STATS_LABELS = {
    "pending": "待处理",
    "processing": "处理中",
    "completed": "已完成",
}

ATTACHMENT_CATEGORIES = (
    "Proposal Document",
    "Contract",
    "Supporting Document",
    "Technical Specification",
    "Financial Document",
    "Other",
)
EXCEL_ATTACH_COLUMNS = ("Attach_Category", "Attach_Path", "Attach_Description")

# 状态显示
STATUS_DISPLAY = {
    "pending": "待处理",
    "processing": "处理中",
    "completed": "已完成",
}

# 优先级显示
PRIORITY_DISPLAY = {
    "high": "高",
    "medium": "中",
    "low": "低",
}

# 示例任务列表
EXAMPLE_TASKS = [
    {"id": "T-001", "title": "审核 PR #42: 新增用户认证中间件", "status": "pending", "priority": "high"},
    {"id": "T-002", "title": "处理 PO #88: 办公用品采购单", "status": "processing", "priority": "medium"},
    {"id": "T-003", "title": "审批 PR #43: 数据库迁移脚本", "status": "pending", "priority": "high"},
    {"id": "T-004", "title": "核验 PO #89: 供应商合同续签", "status": "completed", "priority": "low"},
    {"id": "T-005", "title": "关闭 PR #40: 登录超时 Bug 修复", "status": "completed", "priority": "medium"},
]

# 按钮与界面文案
UI_TEXT = {
    "task_list_title": "任务列表",
    "settings_btn": "设置",
    "start_monitor_btn": "开始监听",
    "minimize_btn": "最小化到托盘",
    "status_bar_default": "就绪",
    "about_btn": "关于",
    "tray_show": "显示主窗口",
    "tray_exit": "退出",
    "under_dev": "功能开发中",
    "menu_settings": "设置",
    "menu_about": "关于",
    "menu_exit": "退出",
    "save_settings": "保存设置",
    "cancel": "取消",
    "hint_dialog_title": "提示",

    # -- Mail Agent button labels (Chinese) --
    "mail_start_btn": "开始监听",
    "mail_stop_btn": "关闭监听",
    "view_log_btn": "查看日志",
    "open_log_folder_btn": "打开日志目录",

    # -- Mail Agent action feedback messages --
    "action_already_running": "Mail Agent 已在运行中",
    "action_start_success": "Mail Agent 已启动",
    "action_start_failed": "Mail Agent 启动失败: {error}",
    "action_stop_success": "Mail Agent 已停止",

    # -- UI event log entries --
    "log_entry_click_start": "User clicked [开始监听]",
    "log_entry_click_stop": "User clicked [关闭监听]",

    # -- Tray menu log entries --
    "tray_view_log": "查看日志",
    "tray_open_log_folder": "打开日志目录",
}

# 设置对话框四个选项卡
SETTINGS_TABS = {
    "email": "邮件",
    "acubuy": "Acubuy",
    "sharepoint": "SharePoint",
    "ai": "AI 配置",
}

# 主窗口 6 个 Tab 配置 (v1.3.2+: GR-Acubuy 启用, 其他 5 Tab 显示 v1.5.0+ 启用)
MAIN_WINDOW_TABS = [
    # (key, label_chinese, enabled, future_version_msg)
    ("gr_acubuy",    "GR-Acubuy",   True,  None),
    ("tools",        "工具",        True,  None),    # NEW
    ("vendor_in",    "供应商入库",   False, "v1.5.0+"),
    ("pr_po_consume", "PR-PO 消耗",  False, "v1.5.0+"),
    ("po_resale",    "PO 转售",      False, "v1.5.0+"),
    ("contract",     "合同",         False, "v1.5.0+"),
    ("gr_sap",       "GR-SAP",       False, "v1.5.0+"),
]

# 设置字段
SETTINGS_FIELDS = {
    "email": [
        ("IMAP 服务器:", "imap_server"),
        ("IMAP 端口:", "imap_port"),
        ("邮箱地址:", "email_address"),
        ("密码:", "email_password"),
    ],
    "acubuy": [
        ("API 地址:", "acubuy_api_url"),
        ("API 密钥:", "acubuy_api_key"),
        ("默认采购员:", "default_buyer"),
    ],
    "sharepoint": [
        ("站点 URL:", "sp_site_url"),
        ("用户名:", "sp_username"),
        ("密码:", "sp_password"),
    ],
    "ai": [
        ("模型名称:", "ai_model"),
        ("API 端点:", "ai_endpoint"),
        ("API 密钥:", "ai_api_key"),
    ],
}

# GR-Acubuy Tab UI 文案 (v1.3.2+)
GR_ACUBUY_UI_TEXT = {
    "today_overview_title":     "今日概览",
    "form_section_title":       "GR 表单",
    "attachments_section_title": "附件",
    "action_section_title":     "操作",
    "status_section_title":     "状态",
    "gr_add_attachment_btn":    "添加附件",
    "gr_save_draft_btn":        "保存草稿",
    "gr_status_disconnected":   "未连接 Acubuy",
    "gr_status_placeholder":    "等待 Acubuy 客户端连接...",
    "gr_no_attachments":        "(暂无附件)",
    "disabled_tab_msg":         "此功能计划在 {version} 启用",
    "stub_action_msg":          "功能开发中 (v1.3.2 UI 骨架)",
    # === Form field labels (Excel column names) ===
    "gr_purchase_order_label":   "采购订单 (Purchase Order):",
    "gr_delivery_note_label":    "送货单 (Delivery Note):",
    "gr_internal_comment_label": "内部备注 (Internal Comment):",
    "gr_quantity_received_label": "收货数量 (Quantity Received):",
    "gr_requestor_label":        "申请人 (Requestor):",
    "gr_approver_2_label":       "审批人 (Approver 2, Min Band E):",
    # === form_data keys (snake_case for AcubuyTaskInput) ===
    "gr_form_key_purchase_order":   "purchase_order",
    "gr_form_key_delivery_note":    "delivery_note",
    "gr_form_key_internal_comment": "internal_comment",
    "gr_form_key_quantity_received": "quantity_received",
    "gr_form_key_requestor":        "requestor",
    "gr_form_key_approver_2":       "approver_2",
    # === Generate Excel button label (NEW) ===
    "gr_generate_excel_btn":     "生成 Excel",
    # === v1.3.2 feedback (T2: precise, persistent, truthful) ===
    "gr_status_in_progress":     "正在生成 Excel…",
    "gr_success_title":          "Excel 生成成功",
    "gr_success_body":           "Excel 已生成：\n{path}\n\n仅生成 Excel，未提交到 Acubuy。",
    "gr_failure_title":          "Excel 生成失败",
    "gr_failure_status":         "生成失败：请查看弹窗详情",
    "gr_success_status_prefix":  "生成成功：",
    "gr_auto_fetch_btn":         "从邮件/附件导入",
    "gr_auto_fetch_stub_msg":    "从邮件/附件自动获取 GR 表单信息（功能开发中）。",
    # === Attachment management (v1.3.3+) ===
    "gr_remove_attachment_btn":     "删除附件",
    "gr_merge_pdfs_btn":           "合并 PDF",
    "gr_attachment_category_label": "分类 (Category):",
    "gr_attachment_file_label":     "文件 (File):",
    "gr_attachment_desc_label":     "备注 (Description):",
    "gr_attachment_dialog_title":   "添加附件",
    "gr_no_pdf_selected_for_merge": "请先选中 ≥2 个 PDF 文件",
    "gr_file_copy_failed_warning":  "以下附件复制失败，请手动放到同目录:\n{paths}\n\nPO 号: {po}\n预期目录: {dir}",
    # === Tools Tab UI text (v1.3.4+) ===
    "tools_tab_title":      "工具",
    "tools_outlook_btn":    "启动 OutlookAgent",
    "tools_pdfmerge_btn":   "启动 PDFMergeTool",
    "tools_formfiller_btn": "启动 FormFiller",
    "tools_status_found":   "✓ 已就绪",
    "tools_status_missing": "✗ 未找到",
    "tools_launch_failed":  "{name} 未找到:\n{path}\n\n请把它放到 PRPOAgent.exe 同目录后重试。",
}

# 确认弹窗
CONFIRM_DIALOG = {
    "title": "确认订单",
    "header": "请确认以下订单信息：",
    "vendor": "供应商:",
    "vendor_name": "示例科技公司",
    "amount": "金额:",
    "amount_value": "￥125,000",
    "terms": "账期:",
    "terms_value": "30 天",
    "confirm_btn": "确认",
    "cancel_btn": "取消",
}

# 单实例锁端口
SINGLE_INSTANCE_PORT = 54321
