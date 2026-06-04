"""
MSG to PDF è½¬æ¢å™¨
ä»Ž .msg æ–‡ä»¶ä¸­æå–é™„ä»¶å¹¶è½¬æ¢ä¸º PDF
"""
import os
import re
import tempfile
import threading
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)
# ===== ???????(?? _html_body_to_pdf ??????) =====
_CJK_FONT_FAMILY = None
_CJK_FONT_INITIALIZED = False

def _init_cjk_font():
    global _CJK_FONT_FAMILY, _CJK_FONT_INITIALIZED
    if _CJK_FONT_INITIALIZED:
        return
    _CJK_FONT_INITIALIZED = True
    
    import os as _os
    from reportlab.pdfbase import pdfmetrics as _pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont as _TTFont
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont as _UnicodeCIDFont
    
    _SYS_FONT_CANDIDATES = [
        (r"C:\Windows\Fonts\simsun.ttc", "SimSun"),
        (r"C:\Windows\Fonts\msyh.ttc", "Microsoft YaHei"),
        (r"C:\Windows\Fonts\simhei.ttf", "SimHei"),
        (r"C:\Windows\Fonts\simkai.ttf", "SimKai"),
        (r"C:\Windows\Fonts\mingliub.ttc", "MingLiU"),
    ]
    for _fp, _fn in _SYS_FONT_CANDIDATES:
        if _os.path.exists(_fp):
            try:
                _pdfmetrics.registerFont(_TTFont(_fn, _fp, subfontIndex=0))
                _CJK_FONT_FAMILY = _fn
                logger.warning("CJK font registered: " + _fn)
                return
            except Exception as _e:
                logger.warning("CJK font register FAILED for " + _fp + ": " + str(_e))
    
    try:
        _pdfmetrics.registerFont(_UnicodeCIDFont("STSong-Light"))
        _CJK_FONT_FAMILY = "STSong-Light"
        logger.warning("CJK font fallback: STSong-Light registered")
    except Exception as _e2:
        logger.warning("CJK font ALL FAILED: " + str(_e2))
# ===== ????????? =====

def extract_attachments_from_msg(msg_path: str, output_dir: str, _depth: int = 0, page_size=None) -> Tuple[bool, List[str], str]:
    """
    ä»Ž .msg æ–‡ä»¶ä¸­æå–æ‰€æœ‰é™„ä»¶
    
    Args:
        msg_path: .msg æ–‡ä»¶è·¯å¾„
        output_dir: è¾“å‡ºç›®å½•
        _depth: åµŒå¥—æ·±åº¦ï¼ˆå†…éƒ¨ä½¿ç”¨ï¼‰
        
    Returns:
        (æ˜¯å¦æˆåŠŸ, é™„ä»¶è·¯å¾„åˆ—è¡¨, é”™è¯¯ä¿¡æ¯)
    """
    try:
        import extract_msg
        
        # ç¡®ä¿è¾“å‡ºç›®å½•å­˜åœ¨
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # æ‰“å¼€ .msg æ–‡ä»¶
        msg = extract_msg.Message(msg_path)
        
        attachments = []
        
        # éåŽ†æ‰€æœ‰é™„ä»¶
        for attachment in msg.attachments:
            # Skip inline images (hidden=True OR image with contentId)
            try:
                if getattr(attachment, "hidden", False):
                    continue
            except:
                pass
            # Also skip image attachments with contentId (logos/signatures)
            try:
                cid = getattr(attachment, "contentId", None)
                if cid:
                    fn_lower = (attachment.longFilename or attachment.shortFilename or "").lower()
                    if any(fn_lower.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                        continue
            except:
                pass
                pass
            try:
                # æ£€æŸ¥æ˜¯å¦æ˜¯åµŒå…¥çš„ .msg é‚®ä»¶é™„ä»¶ï¼ˆtype=1ï¼‰
                is_embedded_msg = False
                try:
                    if hasattr(attachment, 'type') and attachment.type == 1:
                        is_embedded_msg = True
                except:
                    pass
                
                # ç¡®å®šæ–‡ä»¶å
                filename = attachment.longFilename or attachment.shortFilename or f"attachment_{len(attachments)}"
                safe_filename = "".join(
                    c if c.isalnum() or c in (' ', '.', '_', '-', '(', ')') else '_' for c in filename
                )
                
                if is_embedded_msg:
                    # ========== åµŒå…¥ .msg é‚®ä»¶é™„ä»¶å¤„ç† ==========
                    if _depth >= 3:
                        logger.warning(f"åµŒå¥—æ·±åº¦è¾¾åˆ°ä¸Šé™({_depth})ï¼Œè·³è¿‡åµŒå…¥é‚®ä»¶: {safe_filename}")
                        continue
                    
                    # èŽ·å–åµŒå…¥é‚®ä»¶å¯¹è±¡
                    if not hasattr(attachment, 'msg') or not attachment.msg:
                        logger.warning(f"åµŒå…¥ .msg {safe_filename} æ—  msg å±žæ€§ï¼Œè·³è¿‡")
                        continue
                    
                    embedded_msg = attachment.msg
                    
                    # æå–é‚®ä»¶æ­£æ–‡ä¿¡æ¯
                    emb_from = getattr(embedded_msg, 'sender', None) or "Unknown"
                    emb_subject = getattr(embedded_msg, 'subject', None) or "(No Subject)"
                    emb_body = getattr(embedded_msg, 'body', None) or ""
                    emb_date = ""
                    try:
                        if getattr(embedded_msg, 'date', None):
                            emb_date = str(embedded_msg.date)
                    except:
                        pass
                    emb_to = getattr(embedded_msg, 'to', None) or ""
                    
                    # ä¿å­˜åµŒå…¥é‚®ä»¶æ­£æ–‡ä¸º .txt
                    body_lines = []
                    # Try HTML body rendering for embedded email
                    body_ok = False
                    body_path = None
                    try:
                        emb_html = getattr(embedded_msg, "htmlBody", None)
                        if not emb_html:
                            try:
                                _ = getattr(embedded_msg, "rtfBody", None)
                            except:
                                pass
                            emb_html = getattr(embedded_msg, "htmlBody", None)
                        if emb_html:
                            body_filename = f"{safe_filename}_email_body.pdf"
                            body_path = os.path.join(output_dir, body_filename)
                            base, ext = os.path.splitext(body_filename)
                            counter = 1
                            while os.path.exists(body_path):
                                body_path = os.path.join(output_dir, f"{base}_{counter}{ext}")
                                counter += 1
                            body_ok = _html_body_to_pdf(embedded_msg, body_path, output_dir, page_size=page_size)
                            if body_ok:
                                logger.info(f"Embedded HTML body: {os.path.basename(body_path)}")
                    except Exception as _ebe:
                        logger.debug(f"Embedded HTML skip: {_ebe}")
                    
                    # Fallback: plain text
                    if not body_ok:
                        body_lines = []
                        body_lines.append(f"From: {emb_from}")
                        if emb_date:
                            body_lines.append(f"Sent: {emb_date}")
                        if emb_to:
                            body_lines.append(f"To: {emb_to}")
                        body_lines.append(f"Subject: {emb_subject}")
                        body_lines.append("")
                        body_lines.append(emb_body)
                        body_content = "\n".join(body_lines)
                        body_filename = f"{safe_filename}_email_body.txt"
                        body_path = os.path.join(output_dir, body_filename)
                        base, ext = os.path.splitext(body_filename)
                        counter = 1
                        while os.path.exists(body_path):
                            body_path = os.path.join(output_dir, f"{base}_{counter}{ext}")
                            counter += 1
                        with open(body_path, "w", encoding="utf-8") as f:
                            f.write(body_content)
                        logger.info(f"Embedded plain text: {os.path.basename(body_path)}")
                    
                    attachments.append(body_path)
                    logger.info(f"Embedded body extracted: {os.path.basename(body_path)}")
                    # é€’å½’æå–åµŒå…¥é‚®ä»¶çš„é™„ä»¶
                    if hasattr(embedded_msg, 'attachments') and embedded_msg.attachments:
                        emb_sub_dir = os.path.join(output_dir, f"_emb_{len(attachments)}")
                        os.makedirs(emb_sub_dir, exist_ok=True)
                        
                        for emb_att in embedded_msg.attachments:
                            # Skip inline images (hidden=True)
                            try:
                                if getattr(emb_att, "hidden", False):
                                    continue
                            except:
                                pass
                            # Also skip image attachments with contentId (logos/signatures)
                            try:
                                cid = getattr(emb_att, "contentId", None)
                                if cid:
                                    fn_lower = (getattr(emb_att, 'longFilename', '') or getattr(emb_att, 'shortFilename', '') or '').lower()
                                    if any(fn_lower.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                                        continue
                            except:
                                pass
                            try:
                                emb_fn = getattr(emb_att, 'longFilename', None) or getattr(emb_att, 'shortFilename', None) or f"embedded_{len(attachments)}"
                                safe_emb_fn = "".join(
                                    c if c.isalnum() or c in (' ', '.', '_', '-', '(', ')') else '_'
                                    for c in emb_fn
                                )
                                
                                # æ£€æŸ¥åµŒå¥—çš„åµŒå¥— .msg
                                is_nested_msg = False
                                try:
                                    if hasattr(emb_att, 'type') and emb_att.type == 1:
                                        is_nested_msg = True
                                except:
                                    pass
                                
                                if is_nested_msg:
                                    if _depth < 2 and hasattr(emb_att, 'msg') and emb_att.msg:
                                        # æ·±å±‚åµŒå¥—é‚®ä»¶ï¼šé€å±‚æå–é™„ä»¶
                                        nested_msg = emb_att.msg
                                        for n_att in getattr(nested_msg, 'attachments', []):
                                            # Skip inline images (hidden=True)
                                            try:
                                                if getattr(n_att, "hidden", False):
                                                    continue
                                            except:
                                                pass
                                            # Also skip image attachments with contentId (logos/signatures)
                                            try:
                                                cid = getattr(n_att, "contentId", None)
                                                if cid:
                                                    fn_lower = (getattr(n_att, 'longFilename', '') or getattr(n_att, 'shortFilename', '') or '').lower()
                                                    if any(fn_lower.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                                                        continue
                                            except:
                                                pass
                                            try:
                                                n_fn = getattr(n_att, 'longFilename', None) or getattr(n_att, 'shortFilename', None) or f"n_{len(attachments)}"
                                                safe_n = "".join(
                                                    c if c.isalnum() or c in (' ', '.', '_', '-', '(', ')') else '_'
                                                    for c in n_fn
                                                )
                                                n_data = getattr(n_att, 'data', None)
                                                if n_data is None or not isinstance(n_data, bytes):
                                                    continue
                                                n_save = os.path.join(emb_sub_dir, safe_n)
                                                bn, ex = os.path.splitext(safe_n)
                                                n_counter = 1
                                                while os.path.exists(n_save):
                                                    n_save = os.path.join(emb_sub_dir, f"{bn}_{n_counter}{ex}")
                                                    n_counter += 1
                                                with open(n_save, 'wb') as f:
                                                    f.write(n_data)
                                                attachments.append(n_save)
                                                logger.info(f"ä»Žæ·±å±‚åµŒå¥—é‚®ä»¶æå–: {safe_n}")
                                            except Exception as inner_e:
                                                logger.error(f"æ·±å±‚åµŒå¥—å­é™„ä»¶æå–å¤±è´¥: {inner_e}")
                                    continue
                                
                                # æ™®é€šé™„ä»¶ï¼ˆåœ¨åµŒå…¥é‚®ä»¶ä¸­ï¼‰
                                data = getattr(emb_att, 'data', None)
                                if data is None:
                                    continue
                                if not isinstance(data, bytes):
                                    logger.debug(f"è·³è¿‡éžbytesé™„ä»¶: {safe_emb_fn}")
                                    continue
                                
                                save_path = os.path.join(emb_sub_dir, safe_emb_fn)
                                bn, ex = os.path.splitext(safe_emb_fn)
                                n_counter = 1
                                while os.path.exists(save_path):
                                    save_path = os.path.join(emb_sub_dir, f"{bn}_{n_counter}{ex}")
                                    n_counter += 1
                                
                                with open(save_path, 'wb') as f:
                                    f.write(data)
                                attachments.append(save_path)
                                logger.info(f"ä»ŽåµŒå…¥é‚®ä»¶æå–: {safe_emb_fn}")
                            except Exception as inner_e:
                                logger.error(f"æå–åµŒå…¥é‚®ä»¶å­é™„ä»¶å¤±è´¥: {inner_e}")
                    
                    try:
                        if hasattr(embedded_msg, 'close'):
                            embedded_msg.close()
                    except:
                        pass
                    
                else:
                    # ========== æ™®é€šé™„ä»¶å¤„ç† ==========
                    data = attachment.data
                    
                    if data is None:
                        logger.debug(f"Attachment {attachment.longFilename or attachment.shortFilename} has no data, skipping")
                        continue
                
                    # ä¿å­˜é™„ä»¶
                    save_path = os.path.join(output_dir, safe_filename)
                    
                    # å¤„ç†é‡åæ–‡ä»¶
                    base, ext = os.path.splitext(safe_filename)
                    counter = 1
                    while os.path.exists(save_path):
                        save_path = os.path.join(output_dir, f"{base}_{counter}{ext}")
                        counter += 1
                    
                    with open(save_path, 'wb') as f:
                        f.write(data)
                    
                    attachments.append(save_path)
                    logger.info(f"Extracted attachment: {filename}")
                    
            except Exception as e:
                logger.error(f"Failed to extract attachment: {e}")
                continue
        
        msg.close()
        
        if not attachments:
            return False, [], "No attachments found in .msg file"
        
        return True, attachments, ""
        
    except ImportError:
        return False, [], "extract-msg library not installed"
    except Exception as e:
        logger.error(f"Failed to extract attachments from .msg: {e}")
        return False, [], str(e)


def get_msg_email_info(msg_path: str) -> Optional[dict]:
    """
    èŽ·å– .msg æ–‡ä»¶çš„é‚®ä»¶ä¿¡æ¯ï¼ˆç”¨äºŽé‚®ä»¶é™„ä»¶åœºæ™¯ï¼‰
    
    Args:
        msg_path: .msg æ–‡ä»¶è·¯å¾„
        
    Returns:
        é‚®ä»¶ä¿¡æ¯å­—å…¸ï¼ŒåŒ…å«å‘ä»¶äººã€ä¸»é¢˜ã€æ—¶é—´ç­‰
    """
    try:
        import extract_msg
        
        msg = extract_msg.Message(msg_path)
        
        info = {
            'sender': getattr(msg, 'sender', None) or "Unknown",
            'sender_email': getattr(msg, 'senderEmail', None) or "",
            'subject': getattr(msg, 'subject', None) or "(No Subject)",
            'date': str(msg.date) if getattr(msg, 'date', None) else "",
            'to': getattr(msg, 'to', None) or "",
            'cc': getattr(msg, 'cc', None) or "",
            'body': getattr(msg, 'body', None) or "",
        }
        
        msg.close()
        return info
        
    except Exception as e:
        logger.error(f"Failed to get email info from .msg: {e}")
        return None


def _read_msg_html_via_outlook(msg_path):
    """Read HTML body from .msg file using Outlook COM.
    Outlook handles RTF encoding internally, avoiding extract_msg byte 0x90 errors.
    Returns HTML string on success, None on failure."""
    import urllib.parse
    msg_path = urllib.parse.unquote(msg_path).replace('/', '\\')
    import pythoncom
    pythoncom.CoInitialize()
    try:
        import win32com.client
        logger.info("COM: Dispatching Outlook.Application")
        outlook = win32com.client.Dispatch("Outlook.Application")
        logger.info("COM: Dispatch OK, opening shared item")
        mail = outlook.Session.OpenSharedItem(msg_path)
        logger.info("COM: OpenSharedItem OK, reading HTMLBody")
        html = mail.HTMLBody
        logger.info(f"COM: HTMLBody len={len(html) if html else 0}")

        # Read inline image attachments before closing mail
        attachments = []
        try:
            att_count = mail.Attachments.Count
            logger.info(f"COM: Found {att_count} attachments")
            for i in range(1, att_count + 1):
                try:
                    att = mail.Attachments.Item(i)
                    # Get contentId (MAPI property tag for PR_ATTACH_CONTENT_ID)
                    content_id = None
                    try:
                        prop_accessor = att.PropertyAccessor
                        content_id = prop_accessor.GetProperty(
                            "http://schemas.microsoft.com/mapi/proptag/0x3712001E")
                    except:
                        pass

                    if content_id:
                        # Read attachment binary data via temp file
                        data = None
                        try:
                            temp_path = os.path.join(tempfile.gettempdir(), att.FileName)
                            att.SaveAsFile(temp_path)
                            with open(temp_path, 'rb') as f:
                                data = f.read()
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                        except Exception as e:
                            logger.warning(f"COM: Failed to read attachment {i}: {e}")

                        if data:
                            # Get MIME type (MAPI property tag for PR_ATTACH_MIME_TAG)
                            mime_type = 'image/png'
                            try:
                                prop_accessor = att.PropertyAccessor
                                mime_type = prop_accessor.GetProperty(
                                    "http://schemas.microsoft.com/mapi/proptag/0x370E001E") or 'image/png'
                            except:
                                pass

                            attachments.append({
                                'contentId': content_id,
                                'data': data,
                                'mimetype': mime_type,
                                'hidden': True
                            })
                            logger.info(f"COM: Inline image: {att.FileName}, size={len(data)//1024}KB, cid={content_id}")
                except Exception as e:
                    logger.warning(f"COM: Failed to process attachment {i}: {e}")
        except Exception as e:
            logger.warning(f"COM: Failed to enumerate attachments: {e}")

        mail.Close(0)  # olDiscard = 0, don't save changes
        if html and html.strip():
            logger.info(f"COM: SUCCESS, html len={len(html)}, attachments={len(attachments)}")
            return html, attachments
        logger.warning("COM: HTMLBody is empty or None")
        return None, []
    except Exception as e:
        logger.warning(f"COM reader FAILED: {type(e).__name__}: {e}")
        return None, []
    finally:
        pythoncom.CoUninitialize()


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
    """ä½¿ç”¨ xhtml2pdf å°†é‚®ä»¶ HTML æ­£æ–‡è½¬æ¢ä¸º PDFï¼ˆä¿ç•™è¡¨æ ¼å’Œå›¾ç‰‡ï¼‰"""
    import base64
    _init_cjk_font()  # Lazy-init CJK font (logging configured by now)
    
    html_body = msg.htmlBody
    logger.info(f"PATH: _html_body_to_pdf START, htmlBody len={len(html_body) if html_body else 0}")
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
            # Support both dict (from COM) and object (from extract_msg) formats
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
                # Replace cid: references
                html_body = html_body.replace(f'cid:{cid}', data_uri)
                logger.info(f"Embedded image: cid={cid}, size={len(data)//1024}KB, mime={mime}")
        except:
            pass
    
    # Log original size for diagnostics
    logger.info(f"PATH: _html_body_to_pdf before CSS strip, html len={len(html_body)}")
    
    # Inject @page CSS for paper size (A3/A4/Letter) â€” use mm units
    # xhtml2pdf has known issues with pt units in @page, causing A3 infinite loops
    if page_size and isinstance(page_size, (list, tuple)) and len(page_size) == 2:
        width_mm = page_size[0] * 0.3528
        height_mm = page_size[1] * 0.3528
        page_css = f'<style>@page {{ size: {width_mm:.1f}mm {height_mm:.1f}mm; margin: 15mm; }} table {{ width: 100%; table-layout: fixed; border-collapse: collapse; }} td, th {{ word-wrap: break-word; overflow-wrap: break-word; }} tr {{ page-break-inside: avoid; }} img {{ max-width: 100%; max-height: 90%; height: auto; page-break-inside: avoid; }}</style>'
        if '<head>' in html_body.lower():
            html_body = html_body.replace('<head>', f'<head>{page_css}', 1).replace('<HEAD>', f'<HEAD>{page_css}', 1)
        else:
            html_body = page_css + html_body
    
    logger.info(f"PATH: _html_body_to_pdf after CSS inject, html len={len(html_body)}")
    # Patch both DEFAULT_CSS AND DEFAULT_FONT so xhtml2pdf resolves to CJK font
    if _CJK_FONT_FAMILY:
        try:
            import xhtml2pdf.default as _xd
            _xd.DEFAULT_CSS = _xd.DEFAULT_CSS.replace(
                'font-family: Helvetica;',
                'font-family: ' + _CJK_FONT_FAMILY + ';'
            )
            _xd.DEFAULT_FONT['helvetica'] = _CJK_FONT_FAMILY
            _xd.DEFAULT_FONT['helvetica-bold'] = _CJK_FONT_FAMILY
            _xd.DEFAULT_FONT['sansserif'] = _CJK_FONT_FAMILY
            _xd.DEFAULT_FONT['sans'] = _CJK_FONT_FAMILY
            _xd.DEFAULT_FONT['arial'] = _CJK_FONT_FAMILY
            _xd.DEFAULT_FONT['verdana'] = _CJK_FONT_FAMILY
            _xd.DEFAULT_FONT[_CJK_FONT_FAMILY.lower()] = _CJK_FONT_FAMILY
            logger.info("CJK font patched xhtml2pdf CSS+fontmap: " + _CJK_FONT_FAMILY)
        except Exception as _pe:
            logger.warning("Failed to patch xhtml2pdf: " + str(_pe))
    
    # Convert HTML to PDF - try with styles first, strip and retry if fails
    body_rendered = False
    try:
        import logging as _logging
        
        # First attempt: render with original styles (preserves formatting)
        logger.info("PATH: _html_body_to_pdf attempting render WITH styles...")
        _logging.disable(_logging.CRITICAL)
        try:
            from xhtml2pdf import pisa
            result = [None]
            def render_pdf():
                try:
                    with open(output_pdf, 'wb') as f:
                        pisa.CreatePDF(html_body, f, encoding='utf-8')
                    result[0] = True
                except Exception:
                    pass

            render_thread = threading.Thread(target=render_pdf)
            render_thread.start()
            render_thread.join(timeout=45.0)
            body_rendered = (result[0] is True)
        except Exception:
            pass
        finally:
            _logging.disable(_logging.NOTSET)
        
        # Second attempt: strip styles and retry if first attempt failed
        if not body_rendered:
            logger.warning("PATH: render WITH styles failed, stripping styles and retrying...")
            html_body = re.sub(
                r'<style[^>]*>.*?</style>',
                '',
                html_body,
                flags=re.DOTALL | re.IGNORECASE
            )
            # Re-inject @page CSS after stripping
            if page_size and isinstance(page_size, (list, tuple)) and len(page_size) == 2:
                width_mm = page_size[0] * 0.3528
                height_mm = page_size[1] * 0.3528
                page_css = f'<style>@page {{ size: {width_mm:.1f}mm {height_mm:.1f}mm; margin: 15mm; }} table {{ width: 100%; table-layout: fixed; border-collapse: collapse; }} td, th {{ word-wrap: break-word; overflow-wrap: break-word; }} tr {{ page-break-inside: avoid; }} img {{ max-width: 100%; max-height: 90%; height: auto; page-break-inside: avoid; }}</style>'
                if '<head>' in html_body.lower():
                    html_body = html_body.replace('<head>', f'<head>{page_css}', 1).replace('<HEAD>', f'<HEAD>{page_css}', 1)
                else:
                    html_body = page_css + html_body
            
            logger.info(f"PATH: _html_body_to_pdf after CSS strip, html len={len(html_body)}")
            _logging.disable(_logging.CRITICAL)
            try:
                result = [None]
                def render_pdf2():
                    try:
                        with open(output_pdf, 'wb') as f:
                            pisa.CreatePDF(html_body, f, encoding='utf-8')
                        result[0] = True
                    except Exception:
                        pass

                render_thread2 = threading.Thread(target=render_pdf2)
                render_thread2.start()
                render_thread2.join(timeout=45.0)
                body_rendered = (result[0] is True)
            except Exception:
                pass
            finally:
                _logging.disable(_logging.NOTSET)
        
        logger.info(f"PATH: _html_body_to_pdf render result: body_rendered={body_rendered}")
    except Exception:
        pass
    
    if body_rendered and os.path.exists(output_pdf) and os.path.getsize(output_pdf) > 0:
        return True
    
    return False


def msg_to_pdf(
    msg_path: str, 
    output_pdf: str, 
    include_info_page: bool = False,
    page_size=None,
    include_attachments: bool = True,
    _depth: int = 0
) -> Tuple[bool, str]:
    """
    å°† .msg æ–‡ä»¶ä¸­çš„é™„ä»¶è½¬æ¢ä¸º PDF
    
    Args:
        msg_path: .msg æ–‡ä»¶è·¯å¾„
        output_pdf: è¾“å‡º PDF è·¯å¾„
        include_info_page: æ˜¯å¦åŒ…å«é‚®ä»¶ä¿¡æ¯é¡µ
        page_size: çº¸å¼ å¤§å° (width, height) in pointsï¼Œå¦‚ A4=(595.28, 841.89)
        
    Returns:
        (æ˜¯å¦æˆåŠŸ, é”™è¯¯ä¿¡æ¯)
    """
    try:
        if _depth > 4:
            logger.warning(f"MSG nesting depth >4, skipped: {os.path.basename(msg_path)}")
            return False, "é™„ä»¶åµŒå¥—æ·±åº¦è¶…è¿‡é™åˆ¶"
        
        import shutil
        
        # åˆ›å»ºä¸´æ—¶ç›®å½•å­˜æ”¾æå–çš„é™„ä»¶
        temp_dir = tempfile.mkdtemp(prefix="msg_extract_")
        
        # 1. èŽ·å–é‚®ä»¶ä¿¡æ¯ï¼ˆåŒ…æ‹¬æ­£æ–‡ï¼‰
        info = get_msg_email_info(msg_path)
        if not info:
            return False, "Failed to read email info"
        
        # å¯¼å…¥å…¶ä»–è½¬æ¢å™¨
        from . import txt_to_pdf, image_to_pdf, word_to_pdf, excel_to_pdf, merge_pdfs
        from utils.file_utils import get_file_type
        
        pdf_files = []
        
        # 2. å§‹ç»ˆç”Ÿæˆæ­£æ–‡ PDFï¼ˆä¼˜å…ˆ HTML æ¸²æŸ“ï¼Œä¿ç•™è¡¨æ ¼å’Œå›¾ç‰‡ï¼‰
        body_pdf_path = os.path.join(temp_dir, "_email_body.pdf")
        
        # 2. Try Outlook COM first (handles RTF encoding internally)
        body_ok = False
        html_body, com_attachments = _read_msg_html_via_outlook(msg_path)
        if html_body:
            logger.info("PATH: Outlook COM HTML reader: success")
            class _COMResult:
                pass
            com_result = _COMResult()
            com_result.htmlBody = html_body
            com_result.attachments = com_attachments
            body_ok = _html_body_to_pdf(com_result, body_pdf_path, temp_dir,
                                         page_size=page_size or (595.28, 841.89))
        # Fallback: extract_msg path
        if not body_ok:
            logger.info("PATH: Outlook COM HTML reader: fallback to extract_msg")
            try:
                import extract_msg
                msg_obj = extract_msg.Message(msg_path)
                body_ok = _html_body_to_pdf(msg_obj, body_pdf_path, temp_dir,
                                             page_size=page_size or (595.28, 841.89))
                msg_obj.close()
            except Exception as e:
                logger.debug(f"HTML body render not available: {e}")
        
        # Fallback: çº¯æ–‡æœ¬æ­£æ–‡
        if not body_ok:
            body_text_lines = [
                f"From: {info['sender']} ({info['sender_email']})",
                f"To: {info['to']}",
                f"Subject: {info['subject']}",
                f"Date: {info['date']}",
                "",
                re.sub(r'<[^>]+>', '', info['body']) if info['body'] else "(No body content)",
            ]
            body_text = "\n".join(body_text_lines)
            logger.info(f"PATH: Plain text fallback, body len={len(body_text)}")
            
            body_txt_path = os.path.join(temp_dir, "_email_body.txt")
            with open(body_txt_path, 'w', encoding='utf-8') as f:
                f.write(body_text)
            
            body_ok = txt_to_pdf(body_txt_path, body_pdf_path, page_size=page_size or (595.28, 841.89))
        
        if body_ok:
            pdf_files.append(body_pdf_path)
        
        # 3. Extract attachments (if enabled)
        if include_attachments:
            extract_ok, attachments, extract_err = extract_attachments_from_msg(msg_path, temp_dir, _depth + 1, page_size=page_size)
            
            if not attachments:
                logger.info(f".msg has no attachments, body only: {os.path.basename(msg_path)}")
            # å³ä½¿æ— é™„ä»¶ä¹Ÿç»§ç»­ â€”â€” æ­£æ–‡ PDF å·²åœ¨ pdf_files ä¸­
            
            # 4. è½¬æ¢æ¯ä¸ªé™„ä»¶ä¸º PDF
            if extract_ok and attachments:
                for attachment in attachments:
                    file_type = get_file_type(attachment)
                    temp_pdf = os.path.join(temp_dir, f"{os.path.basename(attachment)}.pdf")
                    
                    conv_ok = False
                    
                    if file_type == 'pdf':
                        pdf_files.append(attachment)
                        conv_ok = True
                    elif file_type == 'text':
                        conv_ok = txt_to_pdf(attachment, temp_pdf, page_size=page_size)
                    elif file_type == 'image':
                        conv_ok = image_to_pdf([attachment], temp_pdf, page_size=page_size)
                    elif file_type == 'word':
                        conv_ok, _ = word_to_pdf(attachment, temp_pdf, page_size=page_size)
                    elif file_type == 'excel':
                        conv_ok, _ = excel_to_pdf(attachment, temp_dir, page_size=page_size)
                        # Excel å¯èƒ½ç”Ÿæˆä¸åŒåç§°
                        base = os.path.splitext(os.path.basename(attachment))[0]
                        excel_pdf = os.path.join(temp_dir, f"{base}.pdf")
                        if os.path.exists(excel_pdf):
                            temp_pdf = excel_pdf
                        else:
                            conv_ok = False
                    elif file_type == 'zip':
                        # è§£åŽ‹ ZIP å¹¶è½¬æ¢å†…éƒ¨æ–‡ä»¶
                        from converters.zip_handler import extract_from_zip
                        zip_temp = os.path.join(temp_dir, "_zip_" + os.path.basename(attachment))
                        os.makedirs(zip_temp, exist_ok=True)
                        z_ok, z_files, z_err = extract_from_zip(attachment, zip_temp)
                        if z_ok and z_files:
                            for zf in z_files:
                                z_type = get_file_type(zf)
                                z_pdf = os.path.join(temp_dir, os.path.basename(zf) + ".pdf")
                                z_success = False
                                if z_type == 'pdf':
                                    pdf_files.append(zf)
                                    z_success = True
                                elif z_type == 'text':
                                    z_success = txt_to_pdf(zf, z_pdf, page_size=page_size)
                                elif z_type == 'image':
                                    z_success = image_to_pdf([zf], z_pdf, page_size=page_size)
                                elif z_type == 'word':
                                    z_success, _ = word_to_pdf(zf, z_pdf, page_size=page_size)
                                elif z_type == 'excel':
                                    z_success, _ = excel_to_pdf(zf, temp_dir, page_size=page_size)
                                    if z_success:
                                        base = os.path.splitext(os.path.basename(zf))[0]
                                        alt_pdf = os.path.join(temp_dir, f"{base}.pdf")
                                        if os.path.exists(alt_pdf):
                                            z_pdf = alt_pdf
                                elif z_type == 'zip':
                                    # åµŒå¥— ZIPï¼šä¸å†é€’å½’å¤„ç†ï¼Œè·³è¿‡
                                    logger.info(f"è·³è¿‡åµŒå¥—åŽ‹ç¼©åŒ…: {os.path.basename(zf)}")
                                    z_success = True
                                elif z_type == 'msg':
                                    nested_pdf = os.path.join(temp_dir, os.path.basename(zf) + ".pdf")
                                    z_success, _ = msg_to_pdf(zf, nested_pdf, False, _depth + 1)
                                
                                if z_success and os.path.exists(z_pdf):
                                    pdf_files.append(z_pdf)
                                elif z_success and z_type == 'pdf':
                                    pass  # already added
                                else:
                                    logger.warning(f"ZIP å†…æ–‡ä»¶è½¬æ¢å¤±è´¥: {os.path.basename(zf)}")
                        else:
                            logger.warning(f"ZIP è§£åŽ‹å¤±è´¥ï¼Œè·³è¿‡: {os.path.basename(attachment)}")
                        conv_ok = True  # ZIP å¤„ç†ä¸ä¸­æ–­æ•´ä½“
    
                    elif file_type == 'msg':
                        # åµŒå¥—é‚®ä»¶ï¼šé€’å½’æå–é™„ä»¶
                        if _depth >= 3:
                            logger.warning(f"åµŒå¥—é‚®ä»¶æ·±åº¦å·²è¾¾ä¸Šé™ï¼Œè·³è¿‡: {os.path.basename(attachment)}")
                        else:
                            nested_pdf = os.path.join(temp_dir, os.path.basename(attachment) + ".pdf")
                            nested_ok, nested_err = msg_to_pdf(attachment, nested_pdf, False, _depth + 1)
                            if nested_ok and os.path.exists(nested_pdf):
                                pdf_files.append(nested_pdf)
                                conv_ok = True
                            elif nested_err and nested_err.strip():
                                logger.warning(f"åµŒå¥—é‚®ä»¶è½¬æ¢å¤±è´¥: {os.path.basename(attachment)} - {nested_err}")
                    
                    if conv_ok and file_type == 'zip':
                        pass  # ZIP contents already added to pdf_files
                    elif conv_ok and os.path.exists(temp_pdf):
                        pdf_files.append(temp_pdf)
                    elif conv_ok and file_type == 'pdf':
                        pass  # PDF æ–‡ä»¶å·²ç»æ·»åŠ 
                    else:
                        logger.warning(f"Failed to convert attachment: {os.path.basename(attachment)}")
        else:
            logger.info(f"Skipping attachments (include_attachments=False): {os.path.basename(msg_path)}")
        
        # 5. å¦‚æžœæ²¡æœ‰ä»»ä½• PDF å†…å®¹ï¼Œè¿”å›žé”™è¯¯
        if not pdf_files:
            return False, "No content could be converted to PDF"
        
        # 6. åˆå¹¶æ‰€æœ‰ PDF
        if len(pdf_files) == 1:
            shutil.copy(pdf_files[0], output_pdf)
        else:
            merge_ok, merge_err = merge_pdfs(pdf_files, output_pdf)
            if not merge_ok:
                return False, merge_err
        
        # 7. æ¸…ç†ä¸´æ—¶ç›®å½•
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        return True, ""
        
    except Exception as e:
        logger.error(f"msg_to_pdf failed: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

