"""PDF 合并模块"""
import os
import traceback
from typing import List, Optional

from pypdf import PdfWriter, PdfReader


def merge_pdfs(
    pdf_paths: List[str],
    output_path: str,
    add_bookmarks: bool = False
) -> tuple[bool, str]:
    """
    合并多个 PDF 文件
    
    Args:
        pdf_paths: PDF 文件路径列表（按顺序合并）
        output_path: 输出 PDF 路径
        add_bookmarks: 是否添加书签（以文件名命名）
    
    Returns:
        (是否成功, 错误消息)
    """
    try:
        if not pdf_paths:
            return False, "没有 PDF 文件需要合并"
        
        # 确保输出路径有效
        if not output_path:
            return False, "输出路径无效"
        
        writer = PdfWriter()
        
        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                return False, f"文件不存在: {pdf_path}"
            
            try:
                # 追加所有页面
                writer.append(pdf_path)
                
            except Exception as e:
                return False, f"读取 PDF 失败 [{pdf_path}]: {e}"
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 写入合并后的 PDF
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        if os.path.exists(output_path):
            return True, ""
        else:
            return False, "写入 PDF 失败"
    
    except Exception as e:
        error_msg = f"合并失败: {e}"
        print(error_msg)
        traceback.print_exc()
        return False, error_msg


def get_pdf_page_count(pdf_path: str) -> int:
    """
    获取 PDF 文件的页数
    
    Args:
        pdf_path: PDF 文件路径
    
    Returns:
        页数，失败返回 0
    """
    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except:
        return 0


def get_pdf_info(pdf_path: str) -> Optional[dict]:
    """
    获取 PDF 文件信息
    
    Args:
        pdf_path: PDF 文件路径
    
    Returns:
        包含信息的字典，失败返回 None
    """
    try:
        reader = PdfReader(pdf_path)
        first_page = reader.pages[0]
        
        return {
            'pages': len(reader.pages),
            'width': float(first_page.mediabox.width),
            'height': float(first_page.mediabox.height),
            'encrypted': reader.is_encrypted,
        }
    except:
        return None
