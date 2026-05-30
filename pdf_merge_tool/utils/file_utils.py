"""文件工具模块：文件类型检测、临时文件管理"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional

# 支持的文件格式
SUPPORTED_FORMATS = {
    '.txt': 'text',
    '.pdf': 'pdf',
    '.png': 'image',
    '.jpg': 'image',
    '.jpeg': 'image',
    '.gif': 'image',
    '.bmp': 'image',
    '.tiff': 'image',
    '.webp': 'image',
    '.docx': 'word',
    '.doc': 'word',   # 旧版 Word 格式
    '.xlsx': 'excel',
    '.xls': 'excel',
    '.msg': 'msg',  # Outlook 邮件文件
    '.zip': 'zip',
}

# 临时文件目录
_temp_dir: Optional[str] = None


def get_file_type(file_path: str) -> Optional[str]:
    """
    根据文件扩展名判断文件类型
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件类型 ('text', 'pdf', 'image', 'word', 'excel') 或 None
    """
    ext = Path(file_path).suffix.lower()
    ext = ext.rstrip('_').rstrip('\u200b\u200c\u200d\u2060\u00a0')  # strip invisible Unicode chars
    # Handle double extensions like .docx.doc → try .docx first
    if ext not in SUPPORTED_FORMATS:
        suffixes = Path(file_path).suffixes
        if len(suffixes) >= 2:
            prev_ext = suffixes[-2].lower().rstrip('_').rstrip('\u200b\u200c\u200d\u2060\u00a0')
            if prev_ext in SUPPORTED_FORMATS:
                ext = prev_ext
    return SUPPORTED_FORMATS.get(ext)


def get_temp_dir() -> str:
    """
    获取临时文件目录，如果不存在则创建
    
    Returns:
        临时目录路径
    """
    global _temp_dir
    if _temp_dir is None:
        # 打包后使用用户临时目录
        base_temp = tempfile.gettempdir()
        _temp_dir = os.path.join(base_temp, 'pdf_merge_tool_temp')
        
        # 确保目录存在
        if not os.path.exists(_temp_dir):
            os.makedirs(_temp_dir)
    
    return _temp_dir


def cleanup_temp_files():
    """清理临时文件目录"""
    global _temp_dir
    if _temp_dir and os.path.exists(_temp_dir):
        try:
            shutil.rmtree(_temp_dir)
        except:
            pass
        _temp_dir = None


def is_word_installed() -> bool:
    """检查是否安装了 Microsoft Word（用于 docx2pdf）"""
    try:
        import win32com.client
        win32com.client.Dispatch("Word.Application")
        return True
    except:
        return False


def is_libreoffice_installed() -> bool:
    """检查是否安装了 LibreOffice"""
    # Windows 常见安装路径
    common_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return True
    
    # 检查 PATH 环境变量
    import shutil
    return shutil.which('soffice') is not None
