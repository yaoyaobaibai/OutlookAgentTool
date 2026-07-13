# -*- coding: utf-8 -*-
"""PR/PO Agent - Main entry point (Chinese localized).

Auto-launches Mail Agent subprocess on startup. Mail Agent runs in
background and is terminated when PRPOAgent exits.
"""

import io
import os
import sys
import tempfile
import tkinter as tk

# === Force UTF-8 stdout to avoid cp1252 crash on Windows ===
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
_lock_path = os.path.join(tempfile.gettempdir(), "PRPOAgent.single.lock")
try:
    _lock_fd = os.open(_lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
except Exception:
    os._exit(0)

from config import APP_TITLE

from ui.main_window import MainWindow
from tray import create_tray_icon, run_tray
from mail_controller import MailAgentController


def main():
    """Start PR/PO Assistant: hide window, show tray icon, run main loop."""
    root = tk.Tk()

    # Build the main window (gets reference to MailAgentController for UI)
    mail_controller = MailAgentController()
    window = MainWindow(root, mail_controller=mail_controller)

    # Start hidden - only tray icon visible
    root.withdraw()

    # Create tray icon
    icon = create_tray_icon(
        root=root,
        title=APP_TITLE,
        show_callback=window.show,
    )

    # Auto-launch Mail Agent as a child process
    mail_controller.start()

    # Run tray in daemon thread
    run_tray(icon)

    # Hook window close to clean up child process
    _orig_close = root.protocol("WM_DELETE_WINDOW")
    def _on_main_close():
        # If the main window's own _on_close exists, call it (hides window)
        try:
            if hasattr(window, "_on_close"):
                window._on_close()
                return  # hide-to-tray semantics: do not exit
        except Exception:
            pass
        # No _on_close or it failed: actually stop everything
        try:
            mail_controller.stop()
        except Exception:
            pass
        try:
            icon.stop()
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass
    root.protocol("WM_DELETE_WINDOW", _on_main_close)

    # tkinter main loop in main thread
    try:
        root.mainloop()
    finally:
        # Safety net: always stop Mail Agent on exit regardless of how
        # the loop ended (exception, kill, etc.)
        try:
            mail_controller.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
