# -*- coding: utf-8 -*-
"""PR/PO Agent - Settings dialog (Chinese localized)."""

import tkinter as tk
from tkinter import ttk, messagebox

from config import DEFAULT_FONT, SETTINGS_TABS, SETTINGS_FIELDS, UI_TEXT


class SettingsDialog:
    """Settings dialog with tabbed configuration panels (Chinese UI)."""

    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(UI_TEXT["settings_btn"])
        self.dialog.geometry("500x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._entries = {}

        self._build_notebook()
        self._build_bottom_buttons()

        # Center on parent
        self.dialog.update_idletasks()
        if parent.winfo_viewable():
            px = parent.winfo_rootx() + (parent.winfo_width() - 500) // 2
            py = parent.winfo_rooty() + (parent.winfo_height() - 450) // 2
            self.dialog.geometry(f"+{px}+{py}")

    # ------------------------------------------------------------------
    # Notebook tabs
    # ------------------------------------------------------------------

    def _build_notebook(self):
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        for tab_key, tab_label in SETTINGS_TABS.items():
            tab_frame = ttk.Frame(notebook, padding=(15, 10))
            notebook.add(tab_frame, text=tab_label)
            self._make_fields(tab_frame, SETTINGS_FIELDS[tab_key])

    def _make_fields(self, parent_frame, fields):
        """Build label + entry pairs vertically stacked."""
        for label_text, key in fields:
            row_frame = ttk.Frame(parent_frame)
            row_frame.pack(fill="x", pady=4)

            lbl = ttk.Label(row_frame, text=label_text, width=14, anchor="e")
            lbl.pack(side="left", padx=(0, 8))

            entry = ttk.Entry(row_frame)
            entry.pack(side="left", fill="x", expand=True)

            # Show password-style mask for password fields
            if "password" in key.lower() or "passwd" in key.lower():
                entry.config(show="*")

            self._entries[key] = entry

    # ------------------------------------------------------------------
    # Bottom buttons
    # ------------------------------------------------------------------

    def _build_bottom_buttons(self):
        btn_frame = ttk.Frame(self.dialog, padding=(10, 8))
        btn_frame.pack(fill="x")

        cancel_btn = ttk.Button(
            btn_frame, text=UI_TEXT["cancel"], command=self._on_cancel
        )
        cancel_btn.pack(side="right", padx=(5, 0))

        save_btn = ttk.Button(
            btn_frame, text=UI_TEXT["save_settings"], command=self._on_save
        )
        save_btn.pack(side="right", padx=5)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_save(self):
        messagebox.showinfo(
            UI_TEXT["hint_dialog_title"], UI_TEXT["under_dev"]
        )

    def _on_cancel(self):
        self.dialog.destroy()
