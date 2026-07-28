# -*- coding: utf-8 -*-
"""PR/PO Agent - System tray icon and menu (Chinese localized)."""

import threading

from PIL import Image, ImageDraw


def _create_icon_image():
    """Generate a 16x16 green circle icon using PIL."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((1, 1, 14, 14), fill=(76, 175, 80, 255))
    return img


def create_tray_icon(root, title, show_callback):
    """Create and return a pystray.Icon with right-click menu.

    Args:
        root: tk.Tk root window.
        title: Tooltip text for the tray icon (Chinese app title).
        show_callback: Callable to show the main window.

    Returns:
        pystray.Icon instance (not yet running).
    """
    import pystray

    # Lazy import so config edits don't break tray.py at runtime.
    from config import UI_TEXT

    def _show_window(icon, item):
        show_callback()

    def _exit_app(icon, item):
        icon.stop()
        root.destroy()

    def _view_log(icon, item):
        """Open UI log file (called from tray menu)."""
        import os
        import subprocess
        import sys
        log_path = os.path.join(
            os.path.expandvars(os.path.expanduser("%USERPROFILE%")),
            "PRPOAgent", "prpo_agent_ui.log"
        )
        try:
            if sys.platform == "win32":
                os.startfile(log_path)
            elif sys.platform == "darwin":
                subprocess.call(["open", log_path])
            else:
                subprocess.call(["xdg-open", log_path])
        except Exception:
            pass

    def _open_log_folder(icon, item):
        """Open log folder in file explorer (called from tray menu)."""
        import os
        import subprocess
        import sys
        log_dir = os.path.join(
            os.path.expandvars(os.path.expanduser("%USERPROFILE%")),
            "PRPOAgent"
        )
        try:
            if sys.platform == "win32":
                subprocess.run(["explorer", log_dir], check=False)
            elif sys.platform == "darwin":
                subprocess.call(["open", log_dir])
            else:
                subprocess.call(["xdg-open", log_dir])
        except Exception:
            pass

    menu = pystray.Menu(
        pystray.MenuItem(UI_TEXT["tray_show"], _show_window, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(UI_TEXT["tray_view_log"], _view_log),
        pystray.MenuItem(UI_TEXT["tray_open_log_folder"], _open_log_folder),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(UI_TEXT["tray_exit"], _exit_app),
    )

    icon = pystray.Icon(
        name=title,
        title=title,
        icon=_create_icon_image(),
        menu=menu,
    )

    return icon


def run_tray(icon):
    """Run the tray icon in a daemon thread.

    Args:
        icon: pystray.Icon instance.

    Returns:
        threading.Thread (daemon, already started).
    """
    tray_thread = threading.Thread(target=icon.run, daemon=True)
    tray_thread.start()
    return tray_thread
