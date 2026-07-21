# -*- coding: utf-8 -*-
"""PR/PO Agent - Main window UI (Chinese localized)."""

import io
import logging
import os
import sys
import subprocess
import tempfile
import threading
import time

import tkinter as tk
from tkinter import ttk, messagebox

from config import (
    APP_TITLE,
    DEFAULT_WINDOW_SIZE,
    DEFAULT_FONT,
    DEFAULT_FONT_BOLD,
    TITLE_FONT,
    STATS,
    STATS_LABELS,
    STATUS_DISPLAY,
    PRIORITY_DISPLAY,
    EXAMPLE_TASKS,
    UI_TEXT,
    MAIN_WINDOW_TABS,
    GR_ACUBUY_UI_TEXT,
)
from ui.gr_tab import GrAcubuyTab

# Module-level logger for UI events (separate from mail_agent.log)
_ui_logger = None
_ui_log_path = None
_ui_action_label_after_id = None


def _setup_ui_logging(log_dir_path=None):
    """Set up UI event logger that writes to a NEW timestamped log per app launch.

    Pattern (matches PDFMergeTool's PDFMergeTool_logs/):
    - File: log_YYYYMMDD_HHMMSS.log
    - Dir: %USERPROFILE%/PRPOAgent_logs/
    - Each app launch creates a brand-new file (mode="w", truncated).
    - No rotation, no append to yesterday's file.

    Returns:
        tuple: (logger, log_path)
    """
    global _ui_logger, _ui_log_path

    from datetime import datetime

    if log_dir_path is None:
        log_dir_path = os.path.join(
            os.path.expandvars(os.path.expanduser("%USERPROFILE%")),
            "PRPOAgent_logs"
        )

    try:
        os.makedirs(log_dir_path, exist_ok=True)
    except Exception:
        log_dir_path = os.path.join(tempfile.gettempdir(), "PRPOAgent_logs")
        os.makedirs(log_dir_path, exist_ok=True)

    # PDFMergeTool pattern: log_YYYYMMDD_HHMMSS.log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir_path, f"log_{timestamp}.log")
    _ui_log_path = log_path

    logger = logging.getLogger("prpo_agent_ui")
    logger.setLevel(logging.INFO)
    # Don't propagate to root (prevents messages from polluting other logs)
    logger.propagate = False

    # mode="w" = overwrite on each launch
    try:
        fh = logging.FileHandler(log_path, encoding="utf-8", mode="w")
        fh.setFormatter(
            logging.Formatter(
                "%(asctime)s %(name)s %(levelname)s: %(message)s"
            )
        )
        logger.addHandler(fh)
    except Exception as e:
        sys.stderr.write("Failed to set up UI log: %s\n" % e)

    _ui_logger = logger
    return logger, log_path


def _log_ui(level, msg, *args):
    """Log via _ui_logger if available. Force flush for immediate on-disk evidence."""
    if _ui_logger is not None:
        try:
            getattr(_ui_logger, level)(msg, *args)
            for h in _ui_logger.handlers:
                try:
                    h.flush()
                except Exception:
                    pass
        except Exception:
            pass


class MainWindow:
    """Main application window for PR/PO Agent (Chinese UI)."""

    def __init__(self, root, mail_controller=None):
        # === Setup UI event logger ===
        _setup_ui_logging()
        _log_ui("info", "PRPOAgent started; PID=%d", os.getpid())

        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.minsize(700, 500)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Mail Agent controller (may be None in tests)
        self.mail_controller = mail_controller

        self._build_notebook()
        self._build_bottom_buttons()
        self._build_status_bar()
        self._build_mail_status_bar()

        # Start polling mail agent status
        if self.mail_controller is not None:
            self._refresh_mail_status()
        else:
            # No controller: just show disabled state
            self._set_mail_status(False)

    # ------------------------------------------------------------------
    # Main notebook (6 tabs: 1 enabled + 5 disabled)
    # ------------------------------------------------------------------

    def _build_notebook(self):
        """Build the 6-tab notebook. Only GR-Acubuy is enabled in v1.3.2."""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        for idx, (key, label, enabled, future_version) in enumerate(MAIN_WINDOW_TABS):
            if enabled:
                # GR-Acubuy tab: real functional stub
                gr_tab = GrAcubuyTab(notebook)
                notebook.add(gr_tab.frame, text=label)
            else:
                # Disabled tab: centered placeholder label
                tab_frame = ttk.Frame(notebook, padding=(20, 30))
                notebook.add(tab_frame, text=label)
                msg = GR_ACUBUY_UI_TEXT["disabled_tab_msg"].format(version=future_version)
                ttk.Label(
                    tab_frame,
                    text=msg,
                    font=DEFAULT_FONT,
                    foreground="gray",
                ).pack(expand=True)
                notebook.tab(idx, state="disabled")

    # ------------------------------------------------------------------
    # Bottom buttons
    # ------------------------------------------------------------------

    def _build_bottom_buttons(self):
        btn_frame = ttk.Frame(self.root, padding=(10, 5))
        btn_frame.pack(fill="x", padx=10, pady=(0, 5))

        # Only "Settings" button remains here.
        # Mail Agent Start/Stop controls are in the mail status bar below.
        # Window minimize-to-tray is handled by the X button (_on_close).
        # 2026-07-14: removed dead "开始监听" and "最小化到托盘" demo buttons
        # (they showed "功能开发中" messageboxes).
        settings_btn = ttk.Button(
            btn_frame,
            text=UI_TEXT["settings_btn"],
            command=self._on_settings,
        )
        settings_btn.pack(side="right", padx=5)

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------

    def _build_status_bar(self):
        """Build status bar: left status label + 3 service indicators (right)."""
        bar = ttk.Frame(self.root, relief="sunken")
        bar.pack(fill="x", side="bottom")

        # Left: general status label (kept from previous version)
        status_label = ttk.Label(
            bar,
            text=UI_TEXT["status_bar_default"],
            padding=(10, 3),
        )
        status_label.pack(side="left", fill="x", expand=True)

        # Right: 3 service indicators (Mail + Acubuy + SharePoint)
        # Mail status is updated by _set_mail_status() via _svc_mail_label
        self._svc_mail_label = ttk.Label(bar, text="Mail: --", padding=(5, 3))
        self._svc_mail_label.pack(side="right")
        self._svc_acubuy_label = ttk.Label(
            bar, text="Acubuy: \u672a\u8fde\u63a5", foreground="gray", padding=(5, 3)
        )
        self._svc_acubuy_label.pack(side="right")
        self._svc_sharepoint_label = ttk.Label(
            bar, text="SharePoint: \u672a\u8fde\u63a5", foreground="gray", padding=(5, 3)
        )
        self._svc_sharepoint_label.pack(side="right")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_close(self):
        """Minimize to tray on close (X button)."""
        self.root.withdraw()

    def _on_settings(self):
        messagebox.showinfo(
            UI_TEXT["hint_dialog_title"], UI_TEXT["under_dev"]
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Mail agent status bar (bottom row)
    # ------------------------------------------------------------------

    def _build_mail_status_bar(self):
        """Build Mail Agent controls (status text + buttons)."""
        self._mail_status_frame = ttk.Frame(self.root, padding=(10, 5))
        self._mail_status_frame.pack(fill="x", side="bottom")

        # Mail Agent status label
        self._mail_status_label = ttk.Label(
            self._mail_status_frame,
            text="Mail Agent: ...",
            font=DEFAULT_FONT,
        )
        self._mail_status_label.pack(side="left")

        # Action status label (short-lived feedback after button click)
        self._action_status_label = ttk.Label(
            self._mail_status_frame,
            text="",
            font=DEFAULT_FONT,
            foreground="gray",
        )
        self._action_status_label.pack(side="left", padx=(10, 0))

        # Open log folder button (rightmost)
        open_log_folder_btn = ttk.Button(
            self._mail_status_frame,
            text=UI_TEXT["open_log_folder_btn"],
            command=self._on_open_log_folder,
            width=14,
        )
        open_log_folder_btn.pack(side="right", padx=(5, 0))

        # View log button
        view_log_btn = ttk.Button(
            self._mail_status_frame,
            text=UI_TEXT["view_log_btn"],
            command=self._on_view_log,
            width=10,
        )
        view_log_btn.pack(side="right", padx=5)

        # Stop button
        self._mail_stop_btn = ttk.Button(
            self._mail_status_frame,
            text=UI_TEXT["mail_stop_btn"],
            command=self._on_mail_stop,
            width=10,
        )
        self._mail_stop_btn.pack(side="right", padx=5)

        # Start button
        self._mail_start_btn = ttk.Button(
            self._mail_status_frame,
            text=UI_TEXT["mail_start_btn"],
            command=self._on_mail_start,
            width=10,
        )
        self._mail_start_btn.pack(side="right", padx=(5, 0))

    def _on_mail_start(self):
        """Handle Start button click (async + 30s watchdog).

        Behavior:
        1. Log click on UI thread
        2. Spawn daemon thread that calls mail_controller.start()
        3. UI immediately returns
        4. Background thread logs result
        5. Watchdog reports timeout if start() doesn't return in 30s
        """
        _log_ui("info", UI_TEXT["log_entry_click_start"])

        if self.mail_controller is None:
            _log_ui("error", "mail_controller is None - cannot start")
            self._set_action_status("Mail Agent not configured", color="red")
            return

        self._set_action_status("Starting Mail Agent...", color="gray")

        op_done = threading.Event()
        op_result = {"value": None, "exception": None}

        def _do_start():
            try:
                was_running = self.mail_controller.is_running()
                _log_ui("info", "[bg] is_running() BEFORE = %s", was_running)

                if was_running:
                    op_result["value"] = "already_running"
                    op_done.set()
                    return

                t0 = time.time()
                _log_ui("info", "[bg] calling mail_controller.start()...")
                result = self.mail_controller.start()
                _log_ui("info", "[bg] mail_controller.start() returned %s in %.2fs",
                        result, time.time() - t0)
                op_result["value"] = result
                op_done.set()
            except Exception as e:
                _log_ui("error", "[bg] start() raised Exception: %s", e, exc_info=True)
                op_result["exception"] = e
                op_done.set()
            except BaseException as e:
                _log_ui("error", "[bg] start() raised BaseException: %s: %s",
                        type(e).__name__, e, exc_info=True)
                op_result["exception"] = e
                op_done.set()

        threading.Thread(target=_do_start, daemon=True, name="MailStartThread").start()
        self.root.after(100, lambda: self._watch_start(op_done, op_result, 0))

    def _watch_start(self, op_done, op_result, elapsed_ms):
        """Watchdog for start operation - check every 500ms, timeout at 30s."""
        if op_done.is_set():
            exc = op_result.get("exception")
            val = op_result.get("value")
            if exc is not None:
                err_str = str(exc) if isinstance(exc, Exception) else f"{type(exc).__name__}: {exc}"
                self._set_action_status(
                    UI_TEXT["action_start_failed"].format(error=err_str), color="red")
            elif val == "already_running":
                self._set_action_status(UI_TEXT["action_already_running"], color="orange")
            elif val:
                self._set_action_status(UI_TEXT["action_start_success"], color="green")
            else:
                self._set_action_status(
                    UI_TEXT["action_start_failed"].format(error="returned False"), color="red")
            self._refresh_mail_status()
            return

        if elapsed_ms >= 30000:
            _log_ui("error", "[bg] start() watchdog timeout after 30s - start() hung")
            self._set_action_status("Mail Agent start timeout (30s) - check logs", color="red")
            self._refresh_mail_status()
            return

        self.root.after(500, lambda: self._watch_start(op_done, op_result, elapsed_ms + 500))

    def _on_mail_stop(self):
        """Handle Stop button click (async + 30s watchdog)."""
        _log_ui("info", UI_TEXT["log_entry_click_stop"])

        if self.mail_controller is None:
            _log_ui("error", "mail_controller is None - cannot stop")
            self._set_action_status("Mail Agent not configured", color="red")
            return

        self._set_action_status("Stopping Mail Agent...", color="gray")

        op_done = threading.Event()
        op_result = {"value": None, "exception": None}

        def _do_stop():
            try:
                was_running = self.mail_controller.is_running()
                _log_ui("info", "[bg] is_running() BEFORE = %s", was_running)

                if not was_running:
                    op_result["value"] = "not_running"
                    op_done.set()
                    return

                t0 = time.time()
                _log_ui("info", "[bg] calling mail_controller.stop()...")
                self.mail_controller.stop()
                _log_ui("info", "[bg] mail_controller.stop() returned in %.2fs", time.time() - t0)
                op_result["value"] = True
                op_done.set()
            except Exception as e:
                _log_ui("error", "[bg] stop() raised Exception: %s", e, exc_info=True)
                op_result["exception"] = e
                op_done.set()
            except BaseException as e:
                _log_ui("error", "[bg] stop() raised BaseException: %s: %s",
                        type(e).__name__, e, exc_info=True)
                op_result["exception"] = e
                op_done.set()

        threading.Thread(target=_do_stop, daemon=True, name="MailStopThread").start()
        self.root.after(100, lambda: self._watch_stop(op_done, op_result, 0))

    def _watch_stop(self, op_done, op_result, elapsed_ms):
        """Watchdog for stop operation."""
        if op_done.is_set():
            exc = op_result.get("exception")
            val = op_result.get("value")
            if exc is not None:
                err_str = str(exc) if isinstance(exc, Exception) else f"{type(exc).__name__}: {exc}"
                self._set_action_status(f"Stop failed: {err_str}", color="red")
            elif val == "not_running":
                self._set_action_status("Mail Agent not running", color="orange")
            elif val:
                self._set_action_status(UI_TEXT["action_stop_success"], color="green")
            else:
                self._set_action_status("Stop failed: returned False", color="red")
            self._refresh_mail_status()
            return

        if elapsed_ms >= 30000:
            _log_ui("error", "[bg] stop() watchdog timeout after 30s")
            self._set_action_status("Mail Agent stop timeout (30s) - check logs", color="red")
            self._refresh_mail_status()
            return

        self.root.after(500, lambda: self._watch_stop(op_done, op_result, elapsed_ms + 500))

    def _set_action_status(self, text, color="gray"):
        """Show a short-lived status message next to the Mail Agent status."""
        try:
            self._action_status_label.config(text=text, foreground=color)
        except Exception:
            return

        global _ui_action_label_after_id
        try:
            if _ui_action_label_after_id is not None:
                self.root.after_cancel(_ui_action_label_after_id)
        except Exception:
            pass
        try:
            _ui_action_label_after_id = self.root.after(5000, self._clear_action_status)
        except Exception:
            pass

    def _clear_action_status(self):
        """Clear the action status label (called after 5s timeout)."""
        try:
            self._action_status_label.config(text="", foreground="gray")
        except Exception:
            pass

    def _on_view_log(self):
        """Open the UI log file in default application."""
        _log_ui("info", "User clicked [View Log]")
        if _ui_log_path is None:
            return
        try:
            if sys.platform == "win32":
                os.startfile(_ui_log_path)
            elif sys.platform == "darwin":
                subprocess.call(["open", _ui_log_path])
            else:
                subprocess.call(["xdg-open", _ui_log_path])
            _log_ui("info", "Opened log file: %s", _ui_log_path)
        except Exception as e:
            _log_ui("error", "Failed to open log file: %s", e)
            messagebox.showerror("Error", "Cannot open log file: %s" % e)

    def _on_open_log_folder(self):
        """Open the log directory in file explorer."""
        _log_ui("info", "User clicked [Open Log Folder]")
        if _ui_log_path is None:
            return
        log_dir = os.path.dirname(_ui_log_path)
        try:
            if sys.platform == "win32":
                subprocess.run(["explorer", log_dir], check=False)
            elif sys.platform == "darwin":
                subprocess.call(["open", log_dir])
            else:
                subprocess.call(["xdg-open", log_dir])
            _log_ui("info", "Opened log folder: %s", log_dir)
        except Exception as e:
            _log_ui("error", "Failed to open log folder: %s", e)
            messagebox.showerror("Error", "Cannot open log folder: %s" % e)

    def _set_mail_status(self, is_running):
        if is_running:
            self._mail_status_label.config(text="Mail Agent: running")
            self._svc_mail_label.config(text="Mail: running", foreground="green")
            self._mail_start_btn.state(["disabled"])
            self._mail_stop_btn.state(["!disabled"])
        else:
            self._mail_status_label.config(text="Mail Agent: stopped")
            self._svc_mail_label.config(text="Mail: stopped", foreground="orange")
            self._mail_start_btn.state(["!disabled"])
            self._mail_stop_btn.state(["disabled"])

    def _set_acubuy_status(self, status_text, color="gray"):
        """Update Acubuy service indicator (Phase 2 will call this)."""
        self._svc_acubuy_label.config(text="Acubuy: " + status_text, foreground=color)

    def _set_sharepoint_status(self, status_text, color="gray"):
        """Update SharePoint service indicator (Phase 2 will call this)."""
        self._svc_sharepoint_label.config(text="SharePoint: " + status_text, foreground=color)

    def _refresh_mail_status(self):
        """Poll the controller every 2 seconds and update the status row."""
        if self.mail_controller is not None:
            self._set_mail_status(self.mail_controller.is_running())
        try:
            self.root.after(2000, self._refresh_mail_status)
        except Exception:
            pass

    def show(self):
        """Restore the window from tray (called by tray icon)."""
        self.root.deiconify()
        self.root.lift()
