"""图片文件转 PDF"""
import os
import tempfile
from typing import List, Optional

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def image_to_pdf(
    image_paths: List[str],
    output_pdf: str,
    fit_page: bool = True,
    page_size: tuple = A4
) -> bool:
    """
    将图片转换为 PDF（可多张图片合并到一个 PDF）
    图片居中显示，页面大小可配置（默认 A4）
    
    Args:
        image_paths: 图片路径列表
        output_pdf: 输出 PDF 路径
        fit_page: 是否适应页面大小
        page_size: 页面尺寸（A3/A4/Letter）
    
    Returns:
        是否成功
    """
    temp_files = []
    try:
        if not image_paths:
            return False
        
        # 页面大小
        page_width, page_height = page_size
        margin = 1 * cm
        
        # 可用区域
        usable_width = page_width - 2 * margin
        usable_height = page_height - 2 * margin
        
        # 创建 PDF
        c = canvas.Canvas(output_pdf, pagesize=page_size)
        
        for img_path in image_paths:
            img = Image.open(img_path)
            
            # 转换为 RGB 模式
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            img_width, img_height = img.size
            
            # 计算缩放比例，保持宽高比
            scale_w = usable_width / img_width
            scale_h = usable_height / img_height
            scale = min(scale_w, scale_h, 1.0)  # 不放大，最多原始大小
            
            new_width = img_width * scale
            new_height = img_height * scale
            
            # 计算居中位置
            x = (page_width - new_width) / 2
            y = (page_height - new_height) / 2
            
            # 保存到临时文件（reportlab drawImage 需要文件路径）
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_files.append(temp_file.name)
            img.save(temp_file.name, format='JPEG', quality=95)
            temp_file.close()
            
            # 绘制图片
            c.drawImage(
                temp_file.name,
                x, y,
                width=new_width,
                height=new_height
            )
            
            c.showPage()
        
        c.save()
        return os.path.exists(output_pdf)
    
    except Exception as e:
        print(f"图片转 PDF 失败: {e}")
        return False
    
    finally:
        # 清理临时文件
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass


def single_image_to_pdf(
    image_path: str,
    output_pdf: str
) -> bool:
    """
    单张图片转 PDF
    
    Args:
        image_path: 图片路径
        output_pdf: 输出 PDF 路径
    
    Returns:
        是否成功
    """
    return image_to_pdf([image_path], output_pdf)
