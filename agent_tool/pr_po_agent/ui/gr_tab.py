# -*- coding: utf-8 -*-
"""PR/PO Agent - GR-Acubuy Tab UI skeleton (v1.3.2+).

Functional stub: form fields, attachments placeholder, Save Draft button.
All backend integration is deferred to Phase 2 (per .omo/plans/gr-acubuy-team-plan.md).
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox

from config import (
    DEFAULT_FONT,
    DEFAULT_FONT_BOLD,
    EXAMPLE_TASKS,
    GR_ACUBUY_UI_TEXT,
    PRIORITY_DISPLAY,
    STATS,
    STATS_LABELS,
    STATUS_DISPLAY,
)

logger = logging.getLogger(__name__)


class GrAcubuyTab:
    """GR-Acubuy main window tab — functional stub (Phase 1 UI skeleton)."""

    def __init__(self, parent):
        """Build the GR-Acubuy tab inside the parent notebook."""
        self.parent = parent
        self.frame = ttk.Frame(parent, padding=(10, 5))
        self._supplier_entry = None
        self._amount_entry = None
        self._invoice_entry = None
        self._attachments_list = None
        self._status_label = None

        self._build_today_overview()
        self._build_form_section()
        self._build_attachments_section()
        self._build_action_section()
        self._build_status_row()

    # ------------------------------------------------------------------
    # 今日概览 section (stats + task list, was in main_window)
    # ------------------------------------------------------------------

    def _build_today_overview(self):
        overview = ttk.LabelFrame(
            self.frame,
            text=GR_ACUBUY_UI_TEXT["today_overview_title"],
            padding=(10, 5),
        )
        overview.pack(fill="x", pady=(0, 8))

        # 3 stat cards (smaller than original main_window)
        cards_frame = ttk.Frame(overview)
        cards_frame.pack(fill="x", pady=(0, 5))
        for idx, (key, value) in enumerate(STATS.items()):
            card = ttk.LabelFrame(
                cards_frame,
                text=STATS_LABELS[key],
                padding=(8, 4),
            )
            card.grid(row=0, column=idx, padx=(0, 6), sticky="nsew")
            num_label = ttk.Label(card, text=str(value), font=("Microsoft YaHei", 14, "bold"))
            num_label.pack(fill="x")
            cards_frame.columnconfigure(idx, weight=1, uniform="stat")

        # Compact task list (reuse EXAMPLE_TASKS as placeholder)
        list_frame = ttk.Frame(overview)
        list_frame.pack(fill="x")
        columns = ("id", "title", "status")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=4)
        tree.heading("id", text="ID")
        tree.heading("title", text="\u6807\u9898")
        tree.heading("status", text="\u72b6\u6001")
        tree.column("id", width=60, anchor="center")
        tree.column("title", width=380)
        tree.column("status", width=80, anchor="center")
        for task in EXAMPLE_TASKS:
            tree.insert("", "end", values=(
                task["id"], task["title"], STATUS_DISPLAY[task["status"]],
            ))
        tree.pack(fill="x")

    # ------------------------------------------------------------------
    # GR 表单 section
    # ------------------------------------------------------------------

    def _build_form_section(self):
        form = ttk.LabelFrame(
            self.frame,
            text=GR_ACUBUY_UI_TEXT["form_section_title"],
            padding=(10, 8),
        )
        form.pack(fill="x", pady=(0, 8))

        # Supplier
        row = ttk.Frame(form)
        row.pack(fill="x", pady=3)
        ttk.Label(row, text=GR_ACUBUY_UI_TEXT["gr_supplier_label"], width=10, anchor="e").pack(side="left", padx=(0, 6))
        self._supplier_entry = ttk.Entry(row)
        self._supplier_entry.pack(side="left", fill="x", expand=True)

        # Amount
        row = ttk.Frame(form)
        row.pack(fill="x", pady=3)
        ttk.Label(row, text=GR_ACUBUY_UI_TEXT["gr_amount_label"], width=10, anchor="e").pack(side="left", padx=(0, 6))
        self._amount_entry = ttk.Entry(row)
        self._amount_entry.pack(side="left", fill="x", expand=True)

        # Invoice #
        row = ttk.Frame(form)
        row.pack(fill="x", pady=3)
        ttk.Label(row, text=GR_ACUBUY_UI_TEXT["gr_invoice_label"], width=10, anchor="e").pack(side="left", padx=(0, 6))
        self._invoice_entry = ttk.Entry(row)
        self._invoice_entry.pack(side="left", fill="x", expand=True)

    # ------------------------------------------------------------------
    # 附件 section
    # ------------------------------------------------------------------

    def _build_attachments_section(self):
        att = ttk.LabelFrame(
            self.frame,
            text=GR_ACUBUY_UI_TEXT["attachments_section_title"],
            padding=(10, 5),
        )
        att.pack(fill="x", pady=(0, 8))

        list_frame = ttk.Frame(att)
        list_frame.pack(fill="x")
        self._attachments_list = tk.Listbox(list_frame, height=3)
        self._attachments_list.pack(side="left", fill="x", expand=True)
        self._attachments_list.insert("end", GR_ACUBUY_UI_TEXT["gr_no_attachments"])

        add_btn = ttk.Button(
            list_frame,
            text=GR_ACUBUY_UI_TEXT["gr_add_attachment_btn"],
            command=self._on_add_attachment,
            width=12,
        )
        add_btn.pack(side="right", padx=(6, 0))

    # ------------------------------------------------------------------
    # 操作 section (Save Draft button)
    # ------------------------------------------------------------------

    def _build_action_section(self):
        action = ttk.LabelFrame(
            self.frame,
            text=GR_ACUBUY_UI_TEXT["action_section_title"],
            padding=(10, 5),
        )
        action.pack(fill="x", pady=(0, 8))

        save_btn = ttk.Button(
            action,
            text=GR_ACUBUY_UI_TEXT["gr_save_draft_btn"],
            command=self._on_save_draft,
            width=20,
        )
        save_btn.pack(anchor="center", pady=4)

    # ------------------------------------------------------------------
    # 状态 row
    # ------------------------------------------------------------------

    def _build_status_row(self):
        status = ttk.Frame(self.frame, padding=(10, 3))
        status.pack(fill="x")
        self._status_label = ttk.Label(
            status,
            text=GR_ACUBUY_UI_TEXT["gr_status_disconnected"],
            foreground="gray",
        )
        self._status_label.pack(side="left")

    # ------------------------------------------------------------------
    # Stub handlers (Phase 2 will replace with real logic)
    # ------------------------------------------------------------------

    def _on_add_attachment(self):
        """Stub: show '功能开发中' message."""
        messagebox.showinfo("Acubuy", GR_ACUBUY_UI_TEXT["stub_action_msg"])

    def _on_save_draft(self):
        """Stub: show '功能开发中' message. Will be replaced by Phase 2 acubuy_agent integration."""
        messagebox.showinfo("Acubuy", GR_ACUBUY_UI_TEXT["stub_action_msg"])
