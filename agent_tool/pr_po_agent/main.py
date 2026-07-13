# -*- coding: utf-8 -*-
"""PR/PO Agent - Main entry point (Chinese localized).

Auto-launches Mail Agent thread on startup. Mail Agent runs in-process
as a daemon thread (clean shutdown on PRPOAgent exit).

This version was simplified after extensive debugging: the original
`subprocess.Popen` approach failed inside the PyInstaller --onefile
EXE because sys.executable points to the EXE itself, not a Python
interpreter. The in-process thread approach is the simplest fix that
works in both source and EXE modes.
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

    # Build the main window with reference to MailAgentController
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

    # Auto-launch Mail Agent as in-process thread
    try:
        mail_controller.start()
    except Exception:
        pass  # Mail Agent failure is non-fatal for PRPOAgent

    # Run tray in daemon thread
    run_tray(icon)

    # Hook window close to clean up
    def _on_main_close():
        # Hide-to-tray semantics
        try:
            if hasattr(window, "_on_close"):
                window._on_close()
                return
        except Exception:
            pass
        # Actual close
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
        # Safety net: always stop Mail Agent on exit
        try:
            mail_controller.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
