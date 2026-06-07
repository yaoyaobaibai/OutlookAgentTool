"""
附件处理模块 - 下载和管理邮件附件
"""
import os
import base64
import logging
import shutil
import re
import threading
import pythoncom
from typing import List, Optional, Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# ===== CJK font lazy-init (same as msg_to_pdf.py) =====
_CJK_FONT_FAMILY_OA = None
_CJK_FONT_INIT_OA = False


def _init_cjk_font_oa():
    global _CJK_FONT_FAMILY_OA, _CJK_FONT_INIT_OA
    if _CJK_FONT_INIT_OA:
        return
    _CJK_FONT_INIT_OA = True
    import os as _os
    from reportlab.pdfbase import pdfmetrics as _pm
    from reportlab.pdfbase.ttfonts import TTFont as _TTF
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont as _CID

    candidates = [
        (r"C:\Windows\Fonts\simsun.ttc", "SimSun"),
        (r"C:\Windows\Fonts\msyh.ttc", "Microsoft YaHei"),
        (r"C:\Windows\Fonts\simhei.ttf", "SimHei"),
        (r"C:\Windows\Fonts\simkai.ttf", "SimKai"),
        (r"C:\Windows\Fonts\mingliub.ttc", "MingLiU"),
    ]
    for fp, fn in candidates:
        if _os.path.exists(fp):
            try:
                _pm.registerFont(_TTF(fn, fp, subfontIndex=0))
                _CJK_FONT_FAMILY_OA = fn
                logger.warning("OA CJK font registered: " + fn)
                return
            except Exception as e:
                logger.warning("OA CJK font FAILED for " + fp + ": " + str(e))
    try:
        _pm.registerFont(_CID("STSong-Light"))
        _CJK_FONT_FAMILY_OA = "STSong-Light"
    except:
        logger.warning("OA CJK font ALL FAILED")


# ===== end font init =====


# ========== MSG 文件处理函数（内联避免导入问题） ==========

def is_msg_file(file_path: str) -> bool:
    """检查是否是 .msg 文件"""
    return os.path.splitext(file_path)[1].lower() == '.msg'


def parse_msg_file(msg_path: str) -> Tuple[bool, Dict, List[Dict], str]:
    """
    解析 .msg 文件，提取邮件信息和附件列表
    """
    try:
        import extract_msg

        msg = extract_msg.Message(msg_path)

        email_info = {
            'sender': msg.sender or "Unknown",
            'subject': msg.subject or "(No Subject)",
            'date': str(msg.date) if msg.date else "",
            'to': msg.to or "",
            'cc': msg.cc or "",
            'body': msg.body or "",
        }

        attachments = []
        for attachment in msg.attachments:
            try:
                # 跳过内嵌图片（hidden=True 的附件是正文中的 Logo/图标）
                try:
                    if getattr(attachment, 'hidden', False):
                        continue
                except:
                    pass
                # 跳过有 contentId 的图片附件（签名/Logo）
                try:
                    cid = getattr(attachment, 'contentId', None)
                    if cid:
                        fn_lower = (attachment.longFilename or attachment.shortFilename or "").lower()
                        if any(fn_lower.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                            continue
                except:
                    pass

                filename = attachment.longFilename or attachment.shortFilename or f"attachment_{len(attachments)}"

                # 检查附件类型
                # type=1 是嵌入的 .msg 邮件附件
                is_embedded_msg = False
                try:
                    if hasattr(attachment, 'type') and attachment.type == 1:
                        is_embedded_msg = True
                except:
                    pass

                if is_embedded_msg:
                    # 嵌入的 .msg 邮件附件，标记为特殊类型
                    attachments.append({
                        'name': filename + '.msg',
                        'size': 0,
                        'data': None,
                        'is_embedded_msg': True,
                        'attachment_obj': attachment,
                    })
                else:
                    # 普通附件
                    data = attachment.data
                    size = len(data) if data else 0
                    attachments.append({
                        'name': filename,
                        'size': size,
                        'data': data,
                        'is_embedded_msg': False,
                    })
            except Exception as e:
                logger.error(f"获取附件信息失败: {e}")

        msg.close()
        return True, email_info, attachments, ""

    except Exception as e:
        logger.error(f"解析 .msg 文件失败: {e}")
        return False, {}, [], str(e)


def extract_attachments_from_msg(
        msg_path: str,
        output_dir: str,
        selected_indices: Optional[List[int]] = None,
        attachments_info: Optional[List[Dict]] = None,
        _depth: int = 0
) -> Tuple[bool, List[str], str]:
    """
    从 .msg 文件中提取附件到指定目录
    
    Args:
        msg_path: .msg 文件路径
        output_dir: 输出目录
        selected_indices: 选中的附件索引列表
        attachments_info: 附件信息列表（如果已解析过）
    """
    try:
        import extract_msg

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        msg = extract_msg.Message(msg_path)
        extracted_files = []

        if _depth > 3:
            logger.warning(f"附件嵌套深度超过3层，跳过: {msg_path}")
            msg.close()
            return True, [], ""

        # 确定要处理的附件索引及顺序
        if selected_indices:
            # 按用户指定的顺序遍历
            indices_to_process = selected_indices
        else:
            # 未指定则处理全部，按原始顺序
            indices_to_process = list(range(len(msg.attachments)))

        for idx in indices_to_process:
            if idx >= len(msg.attachments):
                logger.warning(f"跳过无效附件索引: {idx}")
                continue

            attachment = msg.attachments[idx]

            # 跳过内嵌图片（hidden=True）
            try:
                if getattr(attachment, 'hidden', False):
                    continue
            except:
                pass
            # 跳过有 contentId 的图片附件（签名/Logo）
            try:
                cid = getattr(attachment, 'contentId', None)
                if cid:
                    fn_lower = (attachment.longFilename or attachment.shortFilename or "").lower()
                    if any(fn_lower.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                        continue
            except:
                pass

            try:
                filename = attachment.longFilename or attachment.shortFilename or f"attachment_{idx}"

                # 检查是否是嵌入的 .msg 邮件附件（type=1）
                is_embedded_msg = False
                try:
                    if hasattr(attachment, 'type') and attachment.type == 1:
                        is_embedded_msg = True
                        filename = filename + '.msg'
                except:
                    pass

                if is_embedded_msg:
                    # 嵌入的 .msg 邮件附件
                    # 只提取正文和邮件信息，不处理里面的附件
                    safe_filename = "".join(
                        c if c.isalnum() or c in (' ', '.', '_', '-', '(', ')') else '_'
                        for c in filename
                    )

                    import tempfile

                    # 保存嵌入 .msg 为临时文件后重新打开（解决 .msg 属性读取不可靠的 bug）
                    tmp_path = os.path.join(output_dir, f"_emb_{idx}.msg")

                    # 用 extractEmbedded=True 保存嵌入邮件
                    try:
                        attachment.save(customPath=output_dir, customFilename=f"_emb_{idx}", extractEmbedded=True)
                        # save() 创建的文件可能不带扩展名，rename 加上 .msg
                        for fn in os.listdir(output_dir):
                            if fn.startswith(f"_emb_{idx}"):
                                old = os.path.join(output_dir, fn)
                                if old != tmp_path:
                                    if os.path.exists(tmp_path):
                                        os.remove(tmp_path)
                                    os.rename(old, tmp_path)
                                break
                    except Exception:
                        logger.warning(f"无法保存嵌入邮件附件 {idx}，回退到 .msg 属性")
                        if hasattr(attachment, 'msg') and attachment.msg:
                            embedded_msg = attachment.msg
                        else:
                            continue

                    # 重新打开保存的 .msg 文件
                    if os.path.exists(tmp_path):
                        try:
                            embedded_msg = extract_msg.Message(tmp_path)
                        except Exception as e:
                            logger.warning(f"无法打开嵌入邮件 {tmp_path}: {e}")
                            if hasattr(attachment, 'msg') and attachment.msg:
                                embedded_msg = attachment.msg
                            else:
                                continue
                    elif not hasattr(attachment, 'msg') or not attachment.msg:
                        continue

                    # Try HTML body rendering for embedded .msg (preserve tables, images, formatting)
                    body_pdf = os.path.join(output_dir, f"{os.path.splitext(safe_filename)[0]}_email_body.pdf")
                    body_ok = False
                    try:
                        emb_html = getattr(embedded_msg, 'htmlBody', None)
                        logger.warning(f"DEBUG embedded htmlBody: type={type(emb_html).__name__}, len={len(emb_html) if emb_html else 0}")
                        if emb_html:
                            body_ok = _html_body_to_pdf(embedded_msg, body_pdf, output_dir)
                            logger.warning(f"DEBUG _html_body_to_pdf result: {body_ok}")
                        else:
                            logger.warning("DEBUG embedded msg has no htmlBody, fallback to text")
                    except Exception:
                        pass

                    if body_ok:
                        extracted_files.append(body_pdf)
                        logger.info(f"Extracted embedded msg body (HTML): {os.path.basename(body_pdf)}")
                    else:
                        try:
                            # 获取邮件信息
                            emb_from = embedded_msg.sender or "Unknown"
                            emb_subject = embedded_msg.subject or "(No Subject)"
                            emb_body = embedded_msg.body or ""

                            # 格式化日期
                            emb_date = ""
                            if embedded_msg.date:
                                # 转换为类似 Outlook 的格式
                                try:
                                    from datetime import datetime
                                    if hasattr(embedded_msg.date, 'strftime'):
                                        emb_date = embedded_msg.date.strftime("%A, %B %d, %Y %I:%M %p")
                                    else:
                                        emb_date = str(embedded_msg.date)
                                except:
                                    emb_date = str(embedded_msg.date)

                                # 获取收件人 To
                                emb_to = ""
                                try:
                                    if hasattr(embedded_msg, 'to') and embedded_msg.to:
                                        if isinstance(embedded_msg.to, list):
                                            emb_to = "; ".join(str(t) for t in embedded_msg.to)
                                        else:
                                            emb_to = str(embedded_msg.to)
                                except:
                                    pass

                                # 获取抄送 CC
                                emb_cc = ""
                                try:
                                    if hasattr(embedded_msg, 'cc') and embedded_msg.cc:
                                        if isinstance(embedded_msg.cc, list):
                                            emb_cc = "; ".join(str(c) for c in embedded_msg.cc)
                                        else:
                                            emb_cc = str(embedded_msg.cc)
                                except:
                                    pass

                                # 获取附件名字列表
                                emb_attachments = ""
                                try:
                                    if hasattr(embedded_msg, 'attachments') and embedded_msg.attachments:
                                        att_names = []
                                        for att in embedded_msg.attachments:
                                            att_name = att.longFilename or att.shortFilename or ""
                                            if att_name:
                                                att_names.append(att_name)
                                        if att_names:
                                            emb_attachments = "; ".join(att_names)
                                except:
                                    pass

                                # 生成邮件正文文件（Outlook 转发格式）
                                content_lines = []
                                content_lines.append(f"From: {emb_from}")
                                content_lines.append(f"Sent: {emb_date}")
                                if emb_to:
                                    content_lines.append(f"To: {emb_to}")
                                if emb_cc:
                                    content_lines.append(f"Cc: {emb_cc}")
                                content_lines.append(f"Subject: {emb_subject}")
                                if emb_attachments:
                                    content_lines.append(f"Attachments: {emb_attachments}")
                                content_lines.append("")
                                content_lines.append(emb_body)

                                content_text = "\n".join(content_lines)

                                # 保存到输出目录
                                dest_name = f"{os.path.splitext(safe_filename)[0]}_email_body.txt"
                                dest_path = os.path.join(output_dir, dest_name)

                                base, ext = os.path.splitext(dest_name)
                                counter = 1
                                while os.path.exists(dest_path):
                                    dest_path = os.path.join(output_dir, f"{base}_{counter}{ext}")
                                counter += 1

                                with open(dest_path, 'w', encoding='utf-8') as f:
                                    f.write(content_text)

                                extracted_files.append(dest_path)
                                logger.info(f"提取嵌入.msg正文: {dest_name}")

                                # 递归提取嵌入邮件的附件（直接处理，不保存+重解析）
                                if _depth < 3:
                                    try:
                                        emb_sub_dir = os.path.join(output_dir, f"_emb_{idx}")
                                        os.makedirs(emb_sub_dir, exist_ok=True)

                                        # 直接遍历 embedded_msg 的附件列表
                                        for emb_att in embedded_msg.attachments:
                                            # 跳过内嵌图片（hidden=True 的附件是正文中的 Logo/图标）
                                            try:
                                                if getattr(emb_att, 'hidden', False):
                                                    continue
                                            except:
                                                pass
                                            # 跳过有 contentId 的图片附件（签名/Logo）
                                            try:
                                                cid = getattr(emb_att, 'contentId', None)
                                                if cid:
                                                    fn_lower = (emb_att.longFilename or emb_att.shortFilename or "").lower()
                                                    if any(fn_lower.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                                                        continue
                                            except:
                                                pass
                                            try:
                                                emb_fn = emb_att.longFilename or emb_att.shortFilename or f"embedded_{len(extracted_files)}"
                                                safe_emb_fn = "".join(
                                                    c if c.isalnum() or c in (' ', '.', '_', '-', '(', ')') else '_'
                                                    for c in emb_fn
                                                )

                                                # 处理嵌套的嵌套 .msg（递归提取）
                                                is_nested_msg = False
                                                try:
                                                    if hasattr(emb_att, 'type') and emb_att.type == 1:
                                                        is_nested_msg = True
                                                except:
                                                    pass

                                                if is_nested_msg:
                                                    if _depth < 2 and hasattr(emb_att, 'msg') and emb_att.msg:
                                                        # 直接处理嵌套.msg内容，不走 save+重解析
                                                        try:
                                                            nested_msg = emb_att.msg
                                                            nested_sub = os.path.join(emb_sub_dir,
                                                                                      f"_nested_{len(extracted_files)}")
                                                            os.makedirs(nested_sub, exist_ok=True)
                                                            for n_att in nested_msg.attachments:
                                                                # 跳过内嵌图片（hidden=True）
                                                                try:
                                                                    if getattr(n_att, 'hidden', False):
                                                                        continue
                                                                except:
                                                                    pass
                                                                # 跳过有 contentId 的图片附件（签名/Logo）
                                                                try:
                                                                    cid = getattr(n_att, 'contentId', None)
                                                                    if cid:
                                                                        fn_lower = (n_att.longFilename or n_att.shortFilename or "").lower()
                                                                        if any(fn_lower.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                                                                            continue
                                                                except:
                                                                    pass
                                                                try:
                                                                    n_fn = n_att.longFilename or n_att.shortFilename or f"n_{len(extracted_files)}"
                                                                    safe_n = "".join(
                                                                        c if c.isalnum() or c in (' ', '.', '_', '-',
                                                                                                  '(', ')') else '_' for
                                                                        c in n_fn)
                                                                    n_data = n_att.data
                                                                    if n_data is None or not isinstance(n_data, bytes):
                                                                        continue
                                                                    n_save = os.path.join(nested_sub, safe_n)
                                                                    with open(n_save, 'wb') as f:
                                                                        f.write(n_data)
                                                                    extracted_files.append(n_save)
                                                                    logger.info(f"从深层嵌套邮件提取: {safe_n}")
                                                                except Exception as inner_e:
                                                                    logger.error(f"深层嵌套子附件提取失败: {inner_e}")
                                                        except Exception as e:
                                                            logger.error(f"深层嵌套邮件提取失败: {e}")
                                                    else:
                                                        logger.info(f"跳过深层嵌套邮件（深度限制）: {safe_emb_fn}")
                                                    continue

                                                data = emb_att.data
                                                if data is None:
                                                    continue
                                                if not isinstance(data, bytes):
                                                    # 非bytes附件，跳过
                                                    logger.debug(f"跳过非bytes附件: {safe_emb_fn}")
                                                    continue

                                                save_path = os.path.join(emb_sub_dir, safe_emb_fn)
                                                base, ext = os.path.splitext(safe_emb_fn)
                                                counter = 1
                                                while os.path.exists(save_path):
                                                    save_path = os.path.join(emb_sub_dir, f"{base}_{counter}{ext}")
                                                    counter += 1

                                                with open(save_path, 'wb') as f:
                                                    f.write(data)
                                                extracted_files.append(save_path)
                                                logger.info(f"从嵌入邮件提取: {safe_emb_fn}")
                                            except Exception as inner_e:
                                                logger.error(f"提取嵌入邮件子附件失败: {inner_e}")
                                    except Exception as e:
                                        logger.error(f"提取嵌入邮件附件失败: {e}")

                                embedded_msg.close()
                                try:
                                    os.remove(tmp_path)
                                except Exception:
                                    pass
                        except Exception as e:
                            logger.error(f"提取嵌入的.msg失败: {e}")
                            try:
                                os.remove(tmp_path)
                            except Exception:
                                pass
                            continue

                else:
                    # 普通附件
                    data = attachment.data
                    if data is None:
                        logger.warning(f"附件 {idx} 无数据，跳过")
                        continue

                    safe_filename = "".join(
                        c if c.isalnum() or c in (' ', '.', '_', '-', '(', ')') else '_'
                        for c in filename
                    )

                    save_path = os.path.join(output_dir, safe_filename)

                    # 处理重名
                    base, ext = os.path.splitext(safe_filename)
                    counter = 1
                    while os.path.exists(save_path):
                        save_path = os.path.join(output_dir, f"{base}_{counter}{ext}")
                        counter += 1

                    with open(save_path, 'wb') as f:
                        f.write(data)

                    extracted_files.append(save_path)
                    logger.info(f"提取附件: {filename}")

            except Exception as e:
                logger.error(f"提取附件 {idx} 失败: {e}")

        msg.close()
        return True, extracted_files, ""

    except Exception as e:
        logger.error(f"提取附件失败: {e}")
        return False, [], str(e)


def _compress_image_if_needed(data, max_size=200*1024):
    """Compress image if it exceeds max_size, preserving content."""
    if len(data) <= max_size:
        return data
    
    try:
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(data))
        
        # Calculate scale ratio
        ratio = (max_size / len(data)) ** 0.5
        new_size = (int(img.width * ratio), int(img.height * ratio))
        
        # Resize and compress
        img = img.resize(new_size, Image.LANCZOS)
        output = io.BytesIO()
        
        # Convert RGBA to RGB if needed (for PNG with transparency)
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        
        img.save(output, format='JPEG', quality=85, optimize=True)
        compressed = output.getvalue()
        logger.info(f"Compressed image from {len(data)//1024}KB to {len(compressed)//1024}KB")
        return compressed
    except Exception as e:
        logger.warning(f"Image compression failed: {e}, using original")
        return data


def _html_body_to_pdf(msg, output_pdf, temp_dir, page_size=None):
    """Use weasyprint to convert email HTML body to PDF (preserves tables and images)"""

    _init_cjk_font_oa()
    html_body = msg.htmlBody
    logger.info(f"OA PATH: _html_body_to_pdf START, htmlBody len={len(html_body) if html_body else 0}")

    if not html_body:
        return False

    # Decode HTML body
    if isinstance(html_body, bytes):
        try:
            html_body = html_body.decode('utf-8', errors='replace')
        except:
            return False

    if not html_body.strip():
        return False

    # Replace inline images (hidden=True) with base64 data URIs
    # Skip images larger than 200KB to prevent HTML size explosion
    MAX_INLINE_IMG_SIZE = 200 * 1024  # 200KB
    for att in msg.attachments:
        try:
            # Support both dict format (from COM) and object format (from extract_msg)
            if isinstance(att, dict):
                hidden = att.get('hidden', False)
                cid = att.get('contentId')
                data = att.get('data')
                mime = att.get('mimetype', 'image/png')
            else:
                hidden = getattr(att, 'hidden', False)
                cid = getattr(att, 'contentId', None)
                data = att.data
                mime = att.mimetype or 'image/png'

            if hidden and cid and isinstance(data, bytes):
                if len(data) > MAX_INLINE_IMG_SIZE:
                    data = _compress_image_if_needed(data, MAX_INLINE_IMG_SIZE)
                b64 = base64.b64encode(data).decode('ascii')
                data_uri = f'data:{mime};base64,{b64}'
                html_body = html_body.replace(f'cid:{cid}', data_uri)
                logger.info(f"OA Embedded image: cid={cid}, size={len(data)//1024}KB, mime={mime}")
        except:
            pass

    # Build @page CSS for weasyprint (plain CSS string, not HTML <style> tag)
    page_css_parts = []
    if page_size and isinstance(page_size, (list, tuple)) and len(page_size) == 2:
        width_mm = page_size[0] * 0.3528
        height_mm = page_size[1] * 0.3528
        page_css_parts.append(f'@page {{ size: {width_mm:.1f}mm {height_mm:.1f}mm; margin: 15mm; }}')
        logger.info(f"OA PAGE CSS: @page size {width_mm:.1f}mm {height_mm:.1f}mm")
    
    # Table and image formatting CSS
    page_css_parts.append('table { width: 100%; table-layout: fixed; border-collapse: collapse; }')
    page_css_parts.append('td, th { word-wrap: break-word; overflow-wrap: break-word; }')
    page_css_parts.append('tr { page-break-inside: avoid; }')
    page_css_parts.append('img { max-width: 100%; max-height: 90%; height: auto; page-break-inside: avoid; }')
    
    # Line spacing control
    page_css_parts.append('body { line-height: 1.2; }')
    page_css_parts.append('p { margin: 0 0 8px 0; }')
    page_css_parts.append('div { margin: 0; }')
    
    # CJK font fallback
    if _CJK_FONT_FAMILY_OA:
        page_css_parts.append(f'body {{ font-family: "{_CJK_FONT_FAMILY_OA}", Arial, Helvetica, sans-serif; }}')
    
    page_css = '\n'.join(page_css_parts)
    
    # Strip all <style> blocks from original email HTML (weasyprint handles CSS via stylesheets)
    html_body = re.sub(r'<style[^>]*>.*?</style>', '', html_body, flags=re.DOTALL | re.IGNORECASE)
    logger.info(f"OA PATH: _html_body_to_pdf after CSS strip, html len={len(html_body)}")

    # Convert HTML to PDF using weasyprint
    body_rendered = False
    try:
        from weasyprint import HTML, CSS
        
        logger.info("OA PATH: _html_body_to_pdf attempting weasyprint render...")
        
        # Create HTML object
        html_obj = HTML(string=html_body)
        
        # Create CSS object with page size and table styles
        css_obj = CSS(string=page_css)
        
        # Render PDF with stylesheets
        html_obj.write_pdf(output_pdf, stylesheets=[css_obj])
        
        body_rendered = True
        logger.info("OA PATH: _html_body_to_pdf weasyprint render SUCCESS")
    except Exception as e:
        import traceback
        logger.warning(f"OA PATH: weasyprint render FAILED: {type(e).__name__}: {e}")
        logger.warning(f"OA TRACEBACK: {traceback.format_exc()}")
        
        # Fallback: try without custom page size
        try:
            logger.info("OA PATH: attempting weasyprint render WITHOUT custom page size...")
            html_obj = HTML(string=html_body)
            # Use only table/image CSS, no @page
            fallback_css = '\n'.join(page_css_parts[1:]) if len(page_css_parts) > 1 else ''
            css_obj = CSS(string=fallback_css)
            html_obj.write_pdf(output_pdf, stylesheets=[css_obj])
            body_rendered = True
            logger.info("OA PATH: weasyprint fallback render SUCCESS")
        except Exception as e2:
            logger.warning(f"OA PATH: weasyprint fallback FAILED: {type(e2).__name__}: {e2}")
    
    if body_rendered and os.path.exists(output_pdf) and os.path.getsize(output_pdf) > 0:
        return True
    return False


# ========== ????? ==========


class AttachmentHandler:
    """Attachment handler class"""

    def __init__(self, temp_dir: str, allowed_extensions: List[str]):
        self.temp_dir = temp_dir
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            logger.info(f"Temp dir created: {temp_dir}")

    def is_msg_file(self, file_path: str) -> bool:
        return os.path.splitext(file_path)[1].lower() == '.msg'

    def parse_msg_file(self, msg_path: str) -> Tuple[bool, Dict, List[Dict], str]:
        return parse_msg_file(msg_path)

    def extract_attachments_from_msg(self, msg_path, output_dir, selected_indices=None):
        return extract_attachments_from_msg(msg_path, output_dir, selected_indices)

    def is_allowed(self, filename: str) -> bool:
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.allowed_extensions

    def download_attachments(self, mail_item, selected_indices=None):
        try:
            downloaded_files = []
            attachments = mail_item.Attachments
            if attachments.Count == 0:
                return True, [], ""
            for i in range(1, attachments.Count + 1):
                if selected_indices and (i - 1) not in selected_indices:
                    continue
                try:
                    attachment = attachments.Item(i)
                    filename = attachment.FileName or f"attachment_{i}"
                    if not self.is_allowed(filename):
                        continue
                    save_path = self._get_unique_path(self.temp_dir, filename)
                    attachment.SaveAsFile(save_path)
                    downloaded_files.append(save_path)
                    logger.info(f"Downloaded: {filename}")
                except Exception as e:
                    logger.warning(f"Download attachment {i} failed: {e}")
            return True, downloaded_files, ""
        except Exception as e:
            return False, [], str(e)

    def _get_unique_path(self, directory: str, filename: str) -> str:
        base, ext = os.path.splitext(filename)
        path = os.path.join(directory, filename)
        counter = 1
        while os.path.exists(path):
            path = os.path.join(directory, f"{base}_{counter}{ext}")
            counter += 1
        return path

    def cleanup_temp_files(self):
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned temp dir: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Clean temp dir failed: {e}")
