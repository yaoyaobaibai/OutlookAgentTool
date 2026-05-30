@echo off
echo Building PDF Merge Tool...
echo.

cd /d "%~dp0"

pyinstaller --onefile --windowed --name "PDFMergeTool" --hidden-import=converters --hidden-import=converters.txt_to_pdf --hidden-import=converters.image_to_pdf --hidden-import=converters.word_to_pdf --hidden-import=converters.excel_to_pdf --hidden-import=converters.pdf_merger --hidden-import=converters.msg_to_pdf --hidden-import=utils --hidden-import=utils.file_utils --hidden-import=utils.page_numbers --collect-all reportlab --hidden-import=pypdf --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=converters.zip_handler --hidden-import=utils.crash_dump main.py

echo.
echo Build complete!
echo Executable is in: dist\PDFMergeTool.exe
pause
