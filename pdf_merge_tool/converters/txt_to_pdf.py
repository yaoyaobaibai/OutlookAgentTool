"""TXT 文件转 PDF"""
import os
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# 注册中文字体（reportlab 内置，无需外部文件）
try:
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    _CJK_FONT = "STSong-Light"
except Exception:
    _CJK_FONT = None


def txt_to_pdf(
    txt_path: str,
    output_pdf: str,
    font_name: str = "Helvetica",
    font_size: int = 12,
    encoding: str = 'utf-8',
    page_size: tuple = A4
) -> bool:
    """
    将 TXT 文件转换为 PDF
    
    Args:
        txt_path: TXT 文件路径
        output_pdf: 输出 PDF 路径
        font_name: 字体名称
        font_size: 字体大小
        encoding: 文件编码
        page_size: 页面尺寸
    
    Returns:
        是否成功
    """
    try:
        # 读取文本内容
        with open(txt_path, 'r', encoding=encoding) as f:
            lines = f.readlines()
        
        # 自动检测中文，切换字体
        has_cjk = _CJK_FONT and any(
            ord(ch) > 0x2E80 for line in lines for ch in line
        )
        if has_cjk:
            font_name = _CJK_FONT
        
        # 创建 PDF
        c = canvas.Canvas(output_pdf, pagesize=page_size)
        
        # 页面边距
        left_margin = 2 * cm
        right_margin = 2 * cm
        top_margin = 2 * cm
        bottom_margin = 2 * cm
        
        # 可用宽度
        usable_width = page_size[0] - left_margin - right_margin
        
        # 行高
        line_height = font_size * 1.5
        
        # 当前 Y 坐标
        y = page_size[1] - top_margin
        
        c.setFont(font_name, font_size)
        
        # Estimate chars per line based on font size
        avg_char_width = font_size * 0.55
        max_chars = max(20, int(usable_width / avg_char_width))
        
        for line in lines:
            line = line.rstrip('\n\r')
            
            # Word wrap: split long lines to fit within usable_width
            while len(line) > max_chars:
                if y < bottom_margin + line_height:
                    c.showPage()
                    c.setFont(font_name, font_size)
                    y = page_size[1] - top_margin
                
                # Find a good break point (space, comma, period, etc.)
                break_point = max_chars
                for bp in range(min(max_chars, len(line)) - 1, max(max_chars - 30, 0), -1):
                    if line[bp] in ' ,;.，；。、':
                        break_point = bp + 1
                        break
                
                chunk = line[:break_point]
                line = line[break_point:]
                
                try:
                    c.drawString(left_margin, y, chunk)
                except UnicodeEncodeError:
                    pass
                y -= line_height
            
            # Draw remaining text
            if y < bottom_margin + line_height:
                c.showPage()
                c.setFont(font_name, font_size)
                y = page_size[1] - top_margin
            try:
                c.drawString(left_margin, y, line)
            except UnicodeEncodeError:
                pass
            y -= line_height
        
        c.save()
        return os.path.exists(output_pdf)
    
    except Exception as e:
        print(f"TXT 转 PDF 失败: {e}")
        return False

