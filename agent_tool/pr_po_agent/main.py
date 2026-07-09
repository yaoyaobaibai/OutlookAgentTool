# -*- coding: utf-8 -*-
"""PR/PO Agent - Main entry point (Chinese localized)."""

import io
import os
import sys
import tempfile
import tkinter as tk

# === Force UTF-8 stdout to avoid cp1252 crash on Windows ===
# Mirrors the pattern in agent_tool/pdf_merge_tool/main.py.
if sys.stdout and hasattr(sys.stdout, "buffer"):
    try:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
    except Exception:
        pass

# === PyInstaller onefile: locate bundled modules via _MEIPASS ===
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    sys.path.insert(0, sys._MEIPASS)
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# === Single-instance guard ===
# Use exclusive file creation (O_CREAT | O_EXCL). If another instance
# already holds the lock file, we use os._exit(0) (NOT sys.exit) to
# forcibly terminate. PyInstaller --windowed mode can swallow sys.exit
# because there's no stdout to flush; os._exit bypasses that.
_lock_path = os.path.join(tempfile.gettempdir(), "PRPOAgent.single.lock")
try:
    _lock_fd = os.open(_lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
except Exception:
    os._exit(0)

from config import APP_TITLE

from ui.main_window import MainWindow
from tray import create_tray_icon, run_tray


def main():
    """Start PR/PO Assistant: hide window, show tray icon, run main loop."""
    root = tk.Tk()

    # Build the main window
    window = MainWindow(root)

    # Start hidden - only tray icon visible
    root.withdraw()

    # Create tray icon (Chinese menu strings from config)
    icon = create_tray_icon(
        root=root,
        title=APP_TITLE,
        show_callback=window.show,
    )

    # Run tray in daemon thread
    run_tray(icon)

    # tkinter main loop in main thread
    root.mainloop()


if __name__ == "__main__":
    main()
