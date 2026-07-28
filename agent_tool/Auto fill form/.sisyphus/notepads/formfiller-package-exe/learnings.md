# FormFiller EXE Packaging - Learnings

## Initial State

## Build Process
- PyInstaller 6.x changed `--onedir` layout: all contents go into `_internal/` by default
- Fixed with `--contents-directory .` to flatten structure (CWD-relative code compatibility)
- The original `执行打包.bat` uses `^` line continuations which don't work via PowerShell/cmd
- Direct PyInstaller CLI invocation via PowerShell script `pack.ps1` was used instead
- Build time: ~4-5 minutes
- Output size: 392 MB total (numpy, scipy, pandas, playwright, cryptography, etc.)
- EXE size: 26.94 MB (thin launcher)

## Key Decisions
- `--contents-directory .` to keep data files at top level (matching code's CWD-relative paths)
- `--console` mode (user preference)
- No bundled Chromium (uses user's installed Chrome via `channel="chrome"`)

- Python 3.14.4 at `C:\Users\p1325970\AppData\Local\Python\pythoncore-3.14-64\python.exe`
- PyInstaller 6.21.0 installed
- Playwright 1.61.0 installed (browsers NOT installed)
- Existing packaging scripts: `执行打包.bat`, `重新打包.bat`
- Default mode uses user's Chrome via `channel="chrome"`
- All file paths are CWD-relative (no `__file__` or `sys._MEIPASS` usage)
