# -*- coding: utf-8 -*-
"""PR/PO Agent - Tools Tab (v1.3.4+).

Launch external EXEs (OutlookAgent / PDFMergeTool / FormFiller) via sibling-directory detection.

Sister-tab to GrAcubuyTab. UI is intentionally simple: 3 buttons + status indicators.
"""

import logging
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox

from config import DEFAULT_FONT_BOLD, GR_ACUBUY_UI_TEXT

logger = logging.getLogger(__name__)


class ToolsTab:
    """Tools tab — launch external EXEs by sibling-directory detection.

    Looks for each EXE in the same directory as PRPOAgent.exe (or the source
    directory in dev mode). If found, button is enabled and shows green status.
    If missing, button is disabled and shows red status.
    """

    TOOLS = [
        ("OutlookAgent", "OutlookAgent.exe"),
        ("PDFMergeTool", "PDFMergeTool.exe"),
        ("FormFiller",   "FormFiller.exe"),
    ]

    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding=(20, 10))
        self._tool_widgets = {}  # exe_name -> (button, status_label)
        self._build_ui()
        self._refresh_status()

    def _build_ui(self):
        title = ttk.Label(
            self.frame,
            text=GR_ACUBUY_UI_TEXT["tools_tab_title"],
            font=DEFAULT_FONT_BOLD,
        )
        title.pack(anchor="w", pady=(0, 8))

        desc = ttk.Label(
            self.frame,
            text="Click button to launch the matching EXE. The EXE must be in the same directory as PRPOAgent.exe.",
            foreground="gray",
        )
        desc.pack(anchor="w", pady=(0, 16))

        for display_name, exe_name in self.TOOLS:
            row = ttk.Frame(self.frame)
            row.pack(fill="x", pady=6)

            btn = ttk.Button(
                row,
                text=f"Start {display_name}",
                width=22,
                command=lambda n=exe_name: self._launch(n),
            )
            btn.pack(side="left")

            status_label = ttk.Label(row, text="Checking...", foreground="gray")
            status_label.pack(side="left", padx=(12, 0))

            self._tool_widgets[exe_name] = (btn, status_label)

    def _get_sibling_dir(self) -> str:
        """Return the directory where PRPOAgent.exe lives (or source dir in dev)."""
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        # Source mode: this file is at agent_tool/pr_po_agent/ui/tools_tab.py,
        # PRPOAgent.exe would be at agent_tool/pr_po_agent/dist/PRPOAgent.exe.
        # For dev, look in the same dir as this file's parent (pr_po_agent/).
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _refresh_status(self):
        sibling_dir = self._get_sibling_dir()
        for exe_name, (btn, status_label) in self._tool_widgets.items():
            exe_path = os.path.join(sibling_dir, exe_name)
            if os.path.isfile(exe_path):
                btn.config(state="normal")
                status_label.config(
                    text=f"{GR_ACUBUY_UI_TEXT['tools_status_found']}: {exe_path}",
                    foreground="green",
                )
            else:
                btn.config(state="disabled")
                status_label.config(
                    text=f"{GR_ACUBUY_UI_TEXT['tools_status_missing']}: {exe_path}",
                    foreground="red",
                )

    def _launch(self, exe_name: str):
        sibling_dir = self._get_sibling_dir()
        exe_path = os.path.join(sibling_dir, exe_name)
        if not os.path.isfile(exe_path):
            messagebox.showerror(
                "Tools",
                GR_ACUBUY_UI_TEXT["tools_launch_failed"].format(
                    name=exe_name, path=exe_path,
                ),
            )
            return
        try:
            subprocess.Popen(
                [exe_path],
                creationflags=0x08000000,  # Windows: hide console window
            )
            logger.info("Launched %s from %s", exe_name, sibling_dir)
        except Exception as e:
            messagebox.showerror(
                "Tools",
                f"Failed to launch {exe_name}:\n{e}",
            )
            logger.error("Launch %s failed: %s", exe_name, e)
