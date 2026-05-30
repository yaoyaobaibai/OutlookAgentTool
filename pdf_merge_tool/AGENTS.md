# PDFMergeTool 子项目指南

## 入口
- main.py → PDFMergeTool 类，TKinter GUI + --auto 静默模式
- build.bat → PyInstaller --onefile --windowed

## 关键文件
- converters/msg_to_pdf.py → ⚠️ _html_body_to_pdf 双副本之一，修完同步 attachment_handler.py
- converters/word_to_pdf.py → Word COM → docx2pdf → LibreOffice → python-docx fallback 链
- converters/excel_to_pdf.py → Excel COM → LibreOffice → openpyxl+Pillow fallback
- converters/txt_to_pdf.py → 文本转 PDF，CJK 字体检测
- utils/file_utils.py → get_file_type() 扩展名映射
- utils/page_numbers.py → reportlab 页码

## 特殊规则
- 使用 PATH: 前缀标识关键路径（如 "PATH: Word COM OK"）
- 中文字体候选：SimSun, YaHei, SimHei, SimKai, MingLiU → STSong-Light 兜底
- xhtml2pdf 渲染需在 Thread 中 + join(timeout=45) 防卡死
- @page CSS 用 mm 单位（pt 会导致 A3 无限循环）
- table CSS 已注入到 page_css：width:100% table-layout:fixed word-wrap:break-word

## 构建
cd agent_tool\pdf_merge_tool
Remove-Item -Force -Recurse dist,build,__pycache__
pyinstaller --onefile --windowed --name "PDFMergeTool" --hidden-import=converters --hidden-import=converters.txt_to_pdf --hidden-import=converters.image_to_pdf --hidden-import=converters.word_to_pdf --hidden-import=converters.excel_to_pdf --hidden-import=converters.pdf_merger --hidden-import=converters.msg_to_pdf --hidden-import=utils --hidden-import=utils.file_utils --hidden-import=utils.page_numbers --collect-all reportlab --hidden-import=pypdf --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=converters.zip_handler --hidden-import=utils.crash_dump main.py
