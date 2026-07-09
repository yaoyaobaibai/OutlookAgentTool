# -*- coding: utf-8 -*-
"""PR/PO Agent - Confirmation dialog (Chinese localized)."""

import tkinter as tk
from tkinter import ttk, messagebox

from config import (
    DEFAULT_FONT,
    DEFAULT_FONT_BOLD,
    CONFIRM_DIALOG,
    UI_TEXT,
)


class ConfirmDialog:
    """Confirmation dialog showing order details (Chinese UI)."""

    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(CONFIRM_DIALOG["title"])
        self.dialog.geometry("420x260")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._build_header()
        self._build_details()
        self._build_buttons()

        # Center on parent (size matches the geometry above)
        self.dialog.update_idletasks()
        if parent.winfo_viewable():
            px = parent.winfo_rootx() + (parent.winfo_width() - 420) // 2
            py = parent.winfo_rooty() + (parent.winfo_height() - 260) // 2
            self.dialog.geometry(f"+{px}+{py}")

    # ------------------------------------------------------------------
    # UI sections
    # ------------------------------------------------------------------

    def _build_header(self):
        header = ttk.Label(
            self.dialog,
            text=CONFIRM_DIALOG["header"],
            font=DEFAULT_FONT_BOLD,
            padding=(15, 15, 15, 5),
        )
        header.pack(fill="x")

    def _build_details(self):
        details_frame = ttk.Frame(self.dialog, padding=(15, 5))
        details_frame.pack(fill="x")

        rows = [
            (CONFIRM_DIALOG["vendor"], CONFIRM_DIALOG["vendor_name"]),
            (CONFIRM_DIALOG["amount"], CONFIRM_DIALOG["amount_value"]),
            (CONFIRM_DIALOG["terms"], CONFIRM_DIALOG["terms_value"]),
        ]

        for row, (label_text, value_text) in enumerate(rows):
            label = ttk.Label(
                details_frame, text=label_text, font=DEFAULT_FONT_BOLD
            )
            label.grid(row=row, column=0, sticky="e", padx=(0, 10), pady=4)

            value = ttk.Label(details_frame, text=value_text, font=DEFAULT_FONT)
            value.grid(row=row, column=1, sticky="w", pady=4)

    def _build_buttons(self):
        btn_frame = ttk.Frame(self.dialog, padding=(15, 10, 15, 15))
        btn_frame.pack(fill="x")

        cancel_btn = ttk.Button(
            btn_frame,
            text=CONFIRM_DIALOG["cancel_btn"],
            command=self._on_cancel,
        )
        cancel_btn.pack(side="right", padx=(5, 0))

        confirm_btn = ttk.Button(
            btn_frame,
            text=CONFIRM_DIALOG["confirm_btn"],
            command=self._on_confirm,
        )
        confirm_btn.pack(side="right", padx=5)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_confirm(self):
        messagebox.showinfo(
            UI_TEXT["hint_dialog_title"], UI_TEXT["under_dev"]
        )

    def _on_cancel(self):
        self.dialog.destroy()
