@echo off
echo Building PDF Merge Tool...
echo.

cd /d "%~dp0"

pyinstaller --onefile --windowed --name "PDFMergeTool" --hidden-import=converters --hidden-import=converters.txt_to_pdf --hidden-import=converters.image_to_pdf --hidden-import=converters.word_to_pdf --hidden-import=converters.excel_to_pdf --hidden-import=converters.pdf_merger --hidden-import=converters.msg_to_pdf --hidden-import=utils --hidden-import=utils.file_utils --hidden-import=utils.page_numbers --collect-all reportlab --hidden-import=pypdf --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=converters.zip_handler --hidden-import=utils.crash_dump --hidden-import=reportlab.graphics.barcode.code128 --hidden-import=reportlab.graphics.barcode.code93 --hidden-import=reportlab.graphics.barcode.code39 --hidden-import=reportlab.graphics.barcode.eanbc --hidden-import=reportlab.graphics.barcode.usps --hidden-import=reportlab.graphics.barcode.usps4s --hidden-import=reportlab.graphics.barcode.ecc200datamatrix --hidden-import=weasyprint --hidden-import=weasyprint.css --hidden-import=weasyprint.html --collect-all weasyprint main.py

echo.
echo Build complete!
echo Executable is in: dist\PDFMergeTool.exe
pause

