"""Word ??? PDF"""
import os
import sys
import platform
import traceback
from typing import Optional
import logging


# ===== ??????(?? python-docx ????) =====
import os as _os
from reportlab.pdfbase import pdfmetrics as _pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as _TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont as _UnicodeCIDFont

_CJK_FONT_NAME = None
# ????????(?? Windows ????,PyInstaller ??)
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
            _CJK_FONT_NAME = _fn
            logger.warning("Word CJK font: " + _fn)
            break
        except Exception:
            pass

# ????:reportlab ?? CID ??(??????,????????)
if not _CJK_FONT_NAME:
    try:
        _pdfmetrics.registerFont(_UnicodeCIDFont("STSong-Light"))
        _CJK_FONT_NAME = "STSong-Light"
        logger.info("????????? STSong-Light")
    except Exception:
        logger.warning("????????,Word ????????????")

def _has_cjk(text):
    """?????????????"""
    return any(ord(ch) > 0x2E80 for ch in text)
# ===== ???????? =====
logger = logging.getLogger(__name__)


def word_to_pdf(
    word_path: str,
    output_pdf: str,
    page_size: tuple = None
) -> tuple[bool, str]:
    """
    ? Word ????? PDF(?? Microsoft Word COM)
    
    Args:
        word_path: Word ????
        output_pdf: ?? PDF ??
    
    Returns:
        (????, ????)
    """
    # ????
    if platform.system() != 'Windows':
        return False, "Word ? PDF ??? Windows ??"
    
    # ??????
    if not os.path.exists(word_path):
        return False, f"Word ?????: {word_path}"
    
    logger.info(f"Word ? PDF: {word_path} -> {output_pdf}")
    
    try:
        import win32com.client
        import pythoncom
        
        # ??? COM
        pythoncom.CoInitialize()
        logger.info("COM ?????")
        
        try:
            # ??????
            word_path_abs = os.path.abspath(word_path)
            output_pdf_abs = os.path.abspath(output_pdf)
            
            logger.info(f"???? - ??: {word_path_abs}")
            logger.info(f"???? - ??: {output_pdf_abs}")
            
            # ????????
            output_dir = os.path.dirname(output_pdf_abs)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                logger.info(f"??????: {output_dir}")
            
            # ?? Word
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            word.DisplayAlerts = False
            # Backup and set AutomationSecurity to bypass Protected View
            # msoAutomationSecurityForceDisable = 3 (disables all macros, no security warnings)
            original_security = None
            try:
                original_security = word.AutomationSecurity
                word.AutomationSecurity = 3
                logger.info("Word AutomationSecurity set to 3 (ForceDisable)")
            except Exception as _sec_err:
                logger.warning(f"Word AutomationSecurity set failed: {_sec_err}")
            logger.info("Word ??????")
            
            try:
                # ????
                try:
                    doc = word.Documents.Open(word_path_abs, ReadOnly=True)
                except Exception as _open_err:
                    # Trust Center file block? Copy to temp and retry
                    _err_str = str(_open_err)
                    if 'File Block' in _err_str or 'Trust' in _err_str or 'file block' in _err_str.lower():
                        import shutil as _sh, tempfile as _tf
                        _tmp_dir = _tf.gettempdir()
                        _tmp_path = os.path.join(_tmp_dir, os.path.basename(word_path_abs))
                        _sh.copy2(word_path_abs, _tmp_path)
                        logger.warning("Trust Center BLOCKED - retry from temp: " + _tmp_path)
                        doc = word.Documents.Open(_tmp_path, ReadOnly=True)
                        word_path_abs = _tmp_path  # Use temp path for subsequent operations
                    else:
                        raise
                logger.info(f"??????: {word_path_abs}")
                
                
                # Apply user-selected page size to all sections
                if page_size:
                    try:
                        # Try to unprotect document if protected (allows PageSetup changes)
                        try:
                            if doc.ProtectionType != -1:  # wdNoProtection = -1
                                doc.Unprotect()
                                logger.info("Word doc was protected, unprotected for page size")
                        except Exception:
                            pass  # Unprotect failed (may need password), continue anyway
                        
                        for section in doc.Sections:
                            section.PageSetup.PageWidth = page_size[0]
                            section.PageSetup.PageHeight = page_size[1]
                        logger.info(f"Word page size applied: {page_size[0]:.0f}x{page_size[1]:.0f} pts")
                    except Exception as ps_e:
                        logger.warning(f"Word page size skipped (protected doc): {ps_e}")
                
                # ??? PDF
                # wdFormatPDF = 17
                doc.SaveAs(output_pdf_abs, FileFormat=17)
                logger.info(f"PDF ????: {output_pdf_abs}")
                
                # Verify PDF was saved BEFORE closing (Close may fail)
                pdf_ok = os.path.exists(output_pdf_abs)
                
                # Try to close gracefully, ignore errors
                try:
                    doc.Close()
                    logger.info("??????")
                except Exception as _ce:
                    logger.warning("Word doc.Close FAILED (PDF was " + ("saved" if pdf_ok else "NOT saved") + "): " + str(_ce))
                
                if pdf_ok:
                    logger.info(f"????: {output_pdf_abs}")
                    logger.info("PATH: Word COM OK - " + os.path.basename(word_path_abs))
                    return True, ""
                else:
                    return False, "PDF ?????"
            
            finally:
                # Restore original AutomationSecurity
                if original_security is not None:
                    try:
                        word.AutomationSecurity = original_security
                        logger.info(f"Word AutomationSecurity restored to {original_security}")
                    except Exception as _restore_err:
                        logger.warning(f"Word AutomationSecurity restore failed: {_restore_err}")
                try:
                    word.Quit()
                except:
                    pass
                logger.info("Word ????")
        
        finally:
            pythoncom.CoUninitialize()
            logger.info("COM ??")
            # ????????? WINWORD.EXE ????
            # docx2pdf ??????? Dispatch Word.Application,
            # ????? COM ?????????? docx2pdf ??
            try:
                import subprocess
                subprocess.run(['taskkill', '/f', '/im', 'WINWORD.EXE'],
                             capture_output=True, timeout=5,
                             creationflags=0x08000000)
            except:
                pass
    
    except ImportError as e:
        logger.warning(f"pywin32 ???: {e},??????")
        # Fall through to fallback chain below
    
    except Exception as e:
        import traceback as _tb
        _err_lines = _tb.format_exc().strip().split('\n')
        _short = ' | '.join([l.strip() for l in _err_lines[-3:] if l.strip()])
        logger.error("Word COM FAILED: " + type(e).__name__ + " - " + str(e)[:200])
        logger.error("Word COM traceback (last 3 lines): " + _short)
        # Fall through to fallback chain below
    
    # -- Fallback ?:COM ??????? docx2pdf ? LibreOffice --
    
    # ??2: docx2pdf(??? .docx)
    if word_path.lower().endswith('.docx'):
        logger.info("?? docx2pdf ????...")
        success, error = word_to_pdf_docx2pdf(word_path, output_pdf, page_size=page_size)
        if success:
            logger.info("PATH: Word via docx2pdf - " + os.path.basename(word_path))
            return True, ""
        logger.warning(f"docx2pdf ??: {error}")
    
    # ??3: LibreOffice
    logger.info("?? LibreOffice ????...")
    output_dir = os.path.dirname(output_pdf)
    success, error = word_to_pdf_libreoffice(word_path, output_dir, page_size=page_size)
    if success:
        base_name = os.path.splitext(os.path.basename(word_path))[0]
        lo_pdf = os.path.join(output_dir, f"{base_name}.pdf")
        if os.path.exists(lo_pdf) and lo_pdf != output_pdf:
            import shutil
            shutil.move(lo_pdf, output_pdf)
        logger.info("LibreOffice ????")
        return True, ""
    logger.warning(f"LibreOffice ??: {error}")
    
    # ??4: python-docx + reportlab(????,?? Office,? .docx)
    if word_path.lower().endswith('.docx'):
        logger.info("?? python-docx + reportlab ????...")
        success, error = word_to_pdf_python_docx(word_path, output_pdf, page_size=page_size)
        if success:
            logger.info("PATH: Word FALLBACK python-docx - " + os.path.basename(word_path))
            return True, ""
        logger.warning(f"python-docx ??: {error}")
    
    # ???????
    return False, "???? Word ?????? Microsoft Office ? LibreOffice"


def word_to_pdf_docx2pdf(
    word_path: str,
    output_pdf: str,
    page_size: tuple = None
) -> tuple[bool, str]:
    """
    ?? docx2pdf ???(????)
    
    Args:
        word_path: Word ????
        output_pdf: ?? PDF ??
    
    Returns:
        (????, ????)
    """
    try:
        from docx2pdf import convert
        
        # ????????
        output_dir = os.path.dirname(output_pdf)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        convert(word_path, output_pdf)
        
        if os.path.exists(output_pdf):
            return True, ""
        else:
            return False, "???????? PDF ??"
    
    except ImportError:
        return False, "??? docx2pdf ?"
    
    except AttributeError as e:
        return False, f"docx2pdf ????(??? Word ??????? COM ???)"
    
    except Exception as e:
        return False, f"docx2pdf ????: {e}"


def word_to_pdf_libreoffice(
    word_path: str,
    output_dir: str,
    page_size: tuple = None
) -> tuple[bool, str]:
    """
    ?? LibreOffice ????? Word ? PDF
    
    Args:
        word_path: Word ????
        output_dir: ????
    
    Returns:
        (????, ????)
    """
    import subprocess
    _CREATE_NO_WINDOW = 0x08000000 if sys.platform == 'win32' else 0
    
    try:
        # ?? LibreOffice
        soffice_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            "soffice"  # ? PATH ??
        ]
        
        soffice = None
        for path in soffice_paths:
            if os.path.exists(path):
                soffice = path
                break
        
        if not soffice:
            # ??? PATH ??
            result = subprocess.run(['where', 'soffice'], capture_output=True, text=True,
                                   creationflags=_CREATE_NO_WINDOW)
            if result.returncode == 0:
                soffice = result.stdout.strip().split('\n')[0]
        
        if not soffice:
            return False, "??? LibreOffice"
        
        # ????
        cmd = [
            soffice,
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            word_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60,
                               creationflags=_CREATE_NO_WINDOW)
        
        if result.returncode == 0:
            # ??????
            base_name = os.path.splitext(os.path.basename(word_path))[0]
            output_pdf = os.path.join(output_dir, f"{base_name}.pdf")
            if os.path.exists(output_pdf):
                return True, ""
        
        return False, f"LibreOffice ????: {result.stderr}"
    
    except subprocess.TimeoutExpired:
        return False, "LibreOffice ????"
    except Exception as e:
        return False, f"????: {e}"


def word_to_pdf_python_docx(
    word_path: str,
    output_pdf: str,
    page_size: tuple = None
) -> tuple[bool, str]:
    """
    ?? python-docx + reportlab ?? .docx ? PDF(????,?? Office)
    
    ???: COM -> docx2pdf -> LibreOffice -> python-docx+reportlab
    """
    try:
        import docx
        from docx.oxml.ns import qn
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table as RLTable, TableStyle
    except ImportError as e:
        return False, f"????: {e}"
    
    try:
        document = docx.Document(word_path)
        
        if page_size is None:
            page_size = (595.28, 841.89)  # A4 default
        
        pdf_doc = SimpleDocTemplate(
            output_pdf,
            pagesize=page_size,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        for element in document.element.body:
            tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
            
            if tag == 'p':
                para = _build_paragraph(element, styles)
                if para:
                    story.append(para)
            elif tag == 'tbl':
                tbl = _build_table(element)
                if tbl:
                    story.append(Spacer(1, 6))
                    story.append(tbl)
                    story.append(Spacer(1, 6))
        
        if not story:
            return False, "?????"
        
        pdf_doc.build(story)
        
        if os.path.exists(output_pdf) and os.path.getsize(output_pdf) > 0:
            return True, ""
        return False, "PDF ?????"
    
    except Exception as e:
        return False, f"python-docx ????: {e}"


def _build_paragraph(para_element, styles):
    """? docx ?? XML ??? reportlab Paragraph"""
    from docx.oxml.ns import qn
    
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph, Spacer
    
    runs = []
    for r in para_element.findall(qn('w:r')):
        text_parts = []
        rpr = r.find(qn('w:rPr'))
        is_bold = False
        is_italic = False
        font_size = None
        
        if rpr is not None:
            if rpr.find(qn('w:b')) is not None:
                is_bold = True
            if rpr.find(qn('w:i')) is not None:
                is_italic = True
            sz = rpr.find(qn('w:sz'))
            if sz is not None:
                try:
                    font_size = int(sz.get(qn('w:val'), '24')) / 2
                except (ValueError, AttributeError):
                    pass
        
        for t in r.findall(qn('w:t')):
            text = t.text or ''
            if text:
                text_parts.append(text)
        
        if text_parts:
            text = ''.join(text_parts)
            text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            runs.append((text, is_bold, is_italic, font_size))
    
    if not runs:
        return Spacer(1, 4)
    
    para_parts = []
    for text, is_bold, is_italic, _fs in runs:
        if is_bold and is_italic:
            para_parts.append(f'<b><i>{text}</i></b>')
        elif is_bold:
            para_parts.append(f'<b>{text}</b>')
        elif is_italic:
            para_parts.append(f'<i>{text}</i>')
        else:
            para_parts.append(text)
    
    para_text = ''.join(para_parts)
    size = runs[0][3] if runs[0][3] else 10
    
    # ??????,??????
    font_kwargs = {}
    if _CJK_FONT_NAME and _has_cjk(para_text):
        font_kwargs = {"fontName": _CJK_FONT_NAME}
    
    style = ParagraphStyle(
        'temp_para',
        parent=styles['Normal'],
        fontSize=size,
        leading=size * 1.5,
        spaceAfter=4,
        **font_kwargs
    )
    
    return Paragraph(para_text, style)


def _build_table(tbl_element):
    """? docx ?? XML ??? reportlab Table"""
    from docx.oxml.ns import qn
    from reportlab.lib import colors
    from reportlab.platypus import Table as RLTable, TableStyle
    
    rows = []
    for tr in tbl_element.findall(qn('w:tr')):
        row_cells = []
        for tc in tr.findall(qn('w:tc')):
            cell_parts = []
            for p in tc.findall(qn('w:p')):
                for r in p.findall(qn('w:r')):
                    for t in r.findall(qn('w:t')):
                        text = t.text or ''
                        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        cell_parts.append(text)
            row_cells.append(' '.join(cell_parts))
        if row_cells:
            rows.append(row_cells)
    
    if not rows:
        return None
    
    table = RLTable(rows)
    tbl_style = [
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]
    # ??????????,??????
    if _CJK_FONT_NAME and _has_cjk(''.join(''.join(r) for r in rows)):
        tbl_style.append(('FONTNAME', (0, 0), (-1, -1), _CJK_FONT_NAME))
    table.setStyle(TableStyle(tbl_style))
    return table