# -*- coding: utf-8 -*-
"""PR/PO Agent - Main window UI (Chinese localized)."""

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
)


class MainWindow:
    """Main application window for PR/PO Agent (Chinese UI)."""

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.minsize(700, 500)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_stats_panel()
        self._build_task_list()
        self._build_bottom_buttons()
        self._build_status_bar()

    # ------------------------------------------------------------------
    # Stats panel
    # ------------------------------------------------------------------

    def _build_stats_panel(self):
        panel = ttk.Frame(self.root, padding=(10, 10, 10, 5))
        panel.pack(fill="x")

        cards_data = [
            ("pending", STATS["pending"]),
            ("processing", STATS["processing"]),
            ("completed", STATS["completed"]),
        ]

        for idx, (key, value) in enumerate(cards_data):
            card = ttk.LabelFrame(panel, text=STATS_LABELS[key], padding=(15, 10))
            card.grid(row=0, column=idx, padx=(0, 10), sticky="nsew")

            num_label = ttk.Label(
                card,
                text=str(value),
                font=TITLE_FONT,
                anchor="center",
            )
            num_label.pack(fill="x")

        # Equal column weights so cards align neatly
        for col in range(3):
            panel.columnconfigure(col, weight=1, uniform="stat")

    # ------------------------------------------------------------------
    # Task list
    # ------------------------------------------------------------------

    def _build_task_list(self):
        list_frame = ttk.LabelFrame(
            self.root, text=UI_TEXT["task_list_title"], padding=(10, 5)
        )
        list_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        columns = ("id", "title", "status", "priority")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        # Column headings in Chinese
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="标题")
        self.tree.heading("status", text="状态")
        self.tree.heading("priority", text="优先级")

        self.tree.column("id", width=70, anchor="center")
        self.tree.column("title", width=380)
        self.tree.column("status", width=110, anchor="center")
        self.tree.column("priority", width=80, anchor="center")

        # Populate with example tasks (status/priority shown in Chinese)
        for task in EXAMPLE_TASKS:
            self.tree.insert(
                "",
                "end",
                values=(
                    task["id"],
                    task["title"],
                    STATUS_DISPLAY[task["status"]],
                    PRIORITY_DISPLAY[task["priority"]],
                ),
            )

        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

    # ------------------------------------------------------------------
    # Bottom buttons
    # ------------------------------------------------------------------

    def _build_bottom_buttons(self):
        btn_frame = ttk.Frame(self.root, padding=(10, 5))
        btn_frame.pack(fill="x", padx=10, pady=(0, 5))

        # Three buttons: Settings, Start Monitoring, Minimize to Tray
        # Aligned right; min-size button on the very right
        minimize_btn = ttk.Button(
            btn_frame,
            text=UI_TEXT["minimize_btn"],
            command=self._on_minimize_to_tray,
        )
        minimize_btn.pack(side="right", padx=(5, 0))

        start_btn = ttk.Button(
            btn_frame,
            text=UI_TEXT["start_monitor_btn"],
            command=self._on_start_monitoring,
        )
        start_btn.pack(side="right", padx=5)

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
        bar = ttk.Frame(self.root, relief="sunken")
        bar.pack(fill="x", side="bottom")
        status_label = ttk.Label(
            bar,
            text=UI_TEXT["status_bar_default"],
            padding=(10, 3),
        )
        status_label.pack(side="left", fill="x", expand=True)

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

    def _on_start_monitoring(self):
        messagebox.showinfo(
            UI_TEXT["hint_dialog_title"], UI_TEXT["under_dev"]
        )

    def _on_minimize_to_tray(self):
        """Manual minimize to tray (also closes the window)."""
        messagebox.showinfo(
            UI_TEXT["hint_dialog_title"], UI_TEXT["under_dev"]
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show(self):
        """Restore the window from tray (called by tray icon)."""
        self.root.deiconify()
        self.root.lift()
