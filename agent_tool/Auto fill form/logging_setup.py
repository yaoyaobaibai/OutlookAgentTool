"""FormFiller 日志配置模块。

提供：
- configure_logging(): 配置 root logger，写日期分文件日志到程序目录下的 logs 文件夹（utf-8）
- cleanup_old_logs(): 删除超过 N 天的旧日志文件
- GuiLogBridge: 将 Python logging 记录桥接到 GUI 日志区（可注入 sink）
"""

import glob
import logging
import os
import re
import sys
import time
from datetime import datetime
from typing import Callable, Optional

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def mask_value(value, visible: int = 2) -> str:
    """脱敏日志值：保留前 visible 字符 + ***，邮箱保留域名。
    jo***@gmail.com / 12*** / (empty) / (none)
    同时截断超长值（>200 字符）并转义换行。"""
    if value is None:
        return "(none)"
    s = str(value)
    if not s:
        return "(empty)"
    # 先按原始长度截断，再转义换行，最后脱敏（保证每行一条、不泄漏长值）
    if len(s) > 200:
        s = s[:200] + "…"
    s = s.replace("\r\n", "\\n").replace("\n", "\\n")
    if "@" in s:
        local, _, domain = s.partition("@")
        return local[:visible] + "***@" + domain
    return s[:visible] + "***" if len(s) > visible else s


def mask_message(message: str) -> str:
    """脱敏诊断消息：只遮蔽第一个单引号包裹的字段值，保留其余内容（选择器、上下文）。

    处理器返回的 message 形如 `Filled 'Alice' into '#name'`，其中第一个引号段是
    字段值（敏感），后续引号段是选择器（诊断必需，不遮蔽）。
    - "Filled 'Alice' into '#name'" -> "Filled 'Al***' into '#name'"
    - "Selected 'PO0147739' from autocomplete '#sel'" -> "Selected 'PO***' from autocomplete '#sel'"
    - 无引号包裹的值时原样返回（如 "Element not found: #x"）。
    """
    if not message:
        return message
    m = re.search(r"'([^']*)'", message)
    if not m:
        return message
    masked = mask_value(m.group(1))
    return message[: m.start()] + "'" + masked + "'" + message[m.end():]


def _default_log_dir() -> str:
    """返回程序所在目录下的 logs 子目录（打包 exe 时用 exe 所在目录）。"""
    if getattr(sys, "frozen", False):
        # PyInstaller 打包: sys.executable 是 exe 真实路径
        base = os.path.dirname(sys.executable)
    else:
        # 开发模式: 脚本所在目录
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "logs")


def configure_logging(
    log_dir: Optional[str] = None,
    file_level: int = logging.DEBUG,
) -> str:
    """配置 root logger，返回日志文件路径。

    - log_dir 为 None 时使用程序目录下的 logs 文件夹（打包 exe 时为 exe 所在目录/logs）
    - 文件名格式: app-YYYYMMDD-HHMMSS.log（秒级），同秒冲突时追加 -1/-2 计数器
    - FileHandler 使用 utf-8 编码（中文日志硬性需求）
    - swap 语义: 每次调用移除并 close 旧 FileHandler（释放 Windows 文件句柄），
      仅保留本次新建的一个 FileHandler；GuiLogBridge 等非 FileHandler 不受影响
    """
    if log_dir is None:
        log_dir = _default_log_dir()
    os.makedirs(log_dir, exist_ok=True)

    # 固定 base 时间戳（秒级），冲突时只递增 counter，避免循环中秒数漂移
    base_ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    counter = 0
    candidate = os.path.join(log_dir, f"app-{base_ts}.log")
    while os.path.exists(candidate):
        counter += 1
        candidate = os.path.join(log_dir, f"app-{base_ts}-{counter}.log")
    log_file = candidate

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # swap 语义: 移除并 close 所有旧 FileHandler，再挂新的（同秒重跑时换新文件）
    for handler in root.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            root.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(file_handler)

    return log_file


def flush_file_handler() -> None:
    """flush 当前 root 上的 FileHandler（完成/停止时确保日志写盘）。"""
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):
            try:
                handler.flush()
            except Exception:
                pass


def cleanup_old_logs(log_dir: Optional[str] = None, days: int = 30) -> int:
    """删除 log_dir 中超过 days 天的 app-*.log 旧日志文件，返回删除数量。"""
    if log_dir is None:
        log_dir = _default_log_dir()

    cutoff = days * 86400
    removed = 0
    for f in glob.glob(os.path.join(log_dir, "app-*.log")):
        try:
            if time.time() - os.path.getmtime(f) > cutoff:
                os.remove(f)
                removed += 1
        except OSError:
            # 文件可能已被占用或并发删除，静默跳过
            pass

    return removed


class GuiLogBridge(logging.Handler):
    """将 logging 记录桥接到 GUI 日志区（可注入 sink）。

    sink 签名必须匹配 form_filler.FormFiller._log(message): 单 str 参数。
    emit() 吞掉所有异常（post-destroy TclError 防护）。
    """

    def __init__(self, sink: Callable[[str], None], level: int = logging.DEBUG):
        super().__init__(level)
        self.sink = sink
        self.sink_id = id(sink)

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        text = f"[{record.levelname}] {message}"
        try:
            self.sink(text)
        except Exception:
            # GUI 销毁后 root.after 会抛 TclError，必须吞掉
            pass
