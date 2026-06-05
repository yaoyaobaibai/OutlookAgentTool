"""页码生成模块：为 PDF 添加页码"""
import io
import os
from typing import Tuple

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from pypdf import PdfReader, PdfWriter, Transformation


def create_page_number_overlay(
    page_size: Tuple[float, float],
    page_num: int,
    position: str = 'bottom-center',
    font_size: int = 10
) -> bytes:
    """
    创建单页页码 PDF overlay
    
    Args:
        page_size: 页面尺寸 (width, height) in points
        page_num: 当前页码
        position: 页码位置
        font_size: 字体大小
    
    Returns:
        PDF 字节数据
    """
    width, height = page_size
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=page_size)
    
    # 页码文本
    text = f"- {page_num} -"
    
    # 根据位置计算坐标
    if position.startswith('bottom'):
        y = 1 * cm
    else:  # top
        y = height - 1 * cm
    
    if position.endswith('center'):
        x = width / 2
    elif position.endswith('right'):
        x = width - 2 * cm
    else:  # left
        x = 2 * cm
    
    c.setFont("Helvetica", font_size)
    c.drawCentredString(x, y, text)
    c.save()
    
    packet.seek(0)
    return packet.getvalue()


def add_page_numbers(
    input_pdf_path: str,
    output_pdf_path: str,
    position: str = 'bottom-center',
    font_size: int = 10,
    start_page: int = 1
) -> bool:
    """
    为 PDF 添加页码
    
    Args:
        input_pdf_path: 输入 PDF 路径
        output_pdf_path: 输出 PDF 路径
        position: 页码位置
        font_size: 字体大小
        start_page: 起始页码
    
    Returns:
        是否成功
    """
    try:
        if not os.path.exists(input_pdf_path):
            return False
        
        reader = PdfReader(input_pdf_path)
        total_pages = len(reader.pages)
        
        if total_pages == 0:
            return False
        
        writer = PdfWriter()
        
        for i, page in enumerate(reader.pages):
            # 获取当前页面的实际尺寸
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # 复制页面到 writer
            new_page = writer.add_page(page)
            
            # 为每一页创建对应尺寸的页码 overlay
            overlay_bytes = create_page_number_overlay(
                (page_width, page_height),
                i + start_page,
                position,
                font_size
            )
            
            # 读取 overlay
            overlay_reader = PdfReader(io.BytesIO(overlay_bytes))
            
            # 将 overlay 页面合并到当前页
            if len(overlay_reader.pages) > 0:
                overlay_page = overlay_reader.pages[0]
                # 使用 merge_page 方法
                new_page.merge_page(overlay_page)
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_pdf_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 写入输出文件
        with open(output_pdf_path, 'wb') as f:
            writer.write(f)
        
        return True
    
    except Exception as e:
        # 静默失败，返回 False
        return False
