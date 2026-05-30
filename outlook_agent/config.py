"""
Outlook 邮件监控 Agent - 配置文件（支持GUI修改）
"""
import os
import json
import logging

logger = logging.getLogger(__name__)

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.expanduser("~"), "outlook_agent_config.json")

# 默认配置
DEFAULT_CONFIG = {
    # 监控的关键字列表
    "keywords": [
        "合同审批",
        "文件合并",
        "PDF合并",
        "附件处理",
        "合并附件",
    ],
    
    # 允许处理的附件类型
    "allowed_extensions": [
        ".pdf",
        ".docx",
        ".doc",
        ".xlsx",
        ".xls",
        ".txt",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".msg",  # Outlook 邮件文件
    ],
    
    # PDFMergeTool.exe 路径（空表示需要用户设置）
    "pdf_merge_tool_path": "",
    
    # 输出目录
    "output_dir": os.path.join(os.path.expanduser("~"), "merged_output"),
    
    # 临时文件目录
    "temp_dir": os.path.join(os.path.expanduser("~"), "outlook_agent_temp"),
    
    # 日志目录
    "log_dir": os.path.join(os.path.expanduser("~"), "outlook_agent_logs"),
    
    # 检查邮件间隔（秒）
    "check_interval": 30,
    
    # 通知显示时间（秒）
    "notification_duration": 10,
    
    # 是否显示通知
    "show_notification": True,
    
    # 是否播放提示音
    "play_sound": True,
    
    # ========== 邮件监控设置 ==========
    # 监控模式: "time" (时间), "count" (数量), "both" (两者结合)
    "monitor_mode": "time",
    
    # 时间监控范围（分钟）- 只处理这个时间范围内的邮件
    "monitor_time_range": 60,
    
    # 数量监控限制 - 最多检查最近多少封邮件
    "monitor_count_limit": 50,
}


def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # 合并默认配置和用户配置
            config = DEFAULT_CONFIG.copy()
            
            # 对于列表类型的配置，如果用户配置为空则使用默认值
            list_fields = ['keywords', 'allowed_extensions']
            for key, value in user_config.items():
                if key in list_fields and (value is None or len(value) == 0):
                    # 空列表使用默认值
                    continue
                config[key] = value
            
            return config
        except Exception as e:
            logger.warning(f"Config load FAILED: {e}")
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.warning(f"Config save FAILED: {e}")
        return False


def get_config():
    """获取当前配置"""
    return load_config()


# 加载配置
CONFIG = load_config()

# 导出配置变量（兼容旧代码）
KEYWORDS = CONFIG.get("keywords", DEFAULT_CONFIG["keywords"])
KEYWORD_MATCH_MODE = "any"
ALLOWED_EXTENSIONS = CONFIG.get("allowed_extensions", DEFAULT_CONFIG["allowed_extensions"])
PDF_MERGE_TOOL_PATH = CONFIG.get("pdf_merge_tool_path", DEFAULT_CONFIG["pdf_merge_tool_path"])
OUTPUT_DIR = CONFIG.get("output_dir", DEFAULT_CONFIG["output_dir"])
TEMP_DIR = CONFIG.get("temp_dir", DEFAULT_CONFIG["temp_dir"])
LOG_DIR = CONFIG.get("log_dir", DEFAULT_CONFIG["log_dir"])
NOTIFICATION_DURATION = CONFIG.get("notification_duration", DEFAULT_CONFIG["notification_duration"])
LOG_LEVEL = "INFO"

# 邮件监控设置
MONITOR_MODE = CONFIG.get("monitor_mode", DEFAULT_CONFIG["monitor_mode"])
MONITOR_TIME_RANGE = CONFIG.get("monitor_time_range", DEFAULT_CONFIG["monitor_time_range"])
MONITOR_COUNT_LIMIT = CONFIG.get("monitor_count_limit", DEFAULT_CONFIG["monitor_count_limit"])
