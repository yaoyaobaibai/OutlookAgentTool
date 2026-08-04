"""
FileUploadHandler - Built-in handler for 'file_upload' field type.
Supports two modes:
  - "native" (CSMS style): direct <input type="file"> interaction
  - "html5_uploader" (iValua style): click button, find hidden input, wait for upload
"""

import os
from typing import Any
from .base_handler import BaseHandler


class FileUploadHandler(BaseHandler):
    """Handles 'file_upload' field type - file upload fields."""

    def execute(self, field_config: dict, value: str) -> dict:
        """
        Execute field filling logic.

        Args:
            field_config: Field configuration from workflow.json
            value: File path to upload

        Returns:
            {"success": bool, "message": str, "evidence": dict}
        """
        selector = field_config.get("selector", "")
        if not selector:
            return {"success": False, "message": "No selector provided", "evidence": {}}

        hc = field_config.get("handler_config", {})
        mode = hc.get("mode", "native")

        # Validate file exists
        if not os.path.exists(value):
            return {
                "success": False,
                "message": f"File not found: {value}",
                "evidence": {"file_path": value}
            }

        try:
            if mode == "native":
                return self._handle_native(field_config, value)
            elif mode == "html5_uploader":
                return self._handle_html5(field_config, value)
            else:
                # Unknown mode - fall back to native
                return self._handle_native(field_config, value)
        except Exception as e:
            return {
                "success": False,
                "message": f"File upload failed: {str(e)}",
                "evidence": {"error": str(e)}
            }

    def _handle_native(self, field_config: dict, value: str) -> dict:
        """Handle native <input type="file"> upload."""
        selector = field_config.get("selector", "")
        element = self.page.locator(selector)
        element.wait_for(state="visible", timeout=5000)
        element.set_input_files(value)
        return {
            "success": True,
            "message": f"File uploaded to '{selector}': {value}",
            "evidence": {"file": value}
        }

    def _handle_html5(self, field_config: dict, value: str) -> dict:
        """Handle HTML5 uploader (iValua style with progress bar).

        NOTE: html5_uploader mode does NOT click the upload button (that opens
        a native file dialog); it sets files directly on the hidden input,
        which triggers iValua's change-based upload.
        """
        selector = field_config.get("selector", "")
        hc = field_config.get("handler_config", {})
        file_input_selector = hc.get("file_input_selector", selector)
        wait_sel = hc.get("wait_for_upload_selector")
        wait_timeout = hc.get("wait_upload_timeout_ms", 30000)
        wait_after = hc.get("wait_after_upload_ms")

        # Find the hidden file input element
        file_input = self.page.locator(file_input_selector)
        if file_input.count() == 0:
            file_input = self.page.locator('input[type="file"]').first
        file_input.set_input_files(value)

        # Wait for upload to complete (progress indicator to disappear)
        # wait_after_upload_ms is the highest priority wait (fixed elapsed time,
        # used when the upload+refresh cycle is measured, e.g. iValua ~4.3s).
        if wait_after is not None:
            self.page.wait_for_timeout(int(wait_after))
        elif wait_sel:
            try:
                self.page.wait_for_selector(wait_sel, state="hidden", timeout=wait_timeout)
            except Exception:
                self.page.wait_for_timeout(3000)
        else:
            self.page.wait_for_timeout(2000)

        return {
            "success": True,
            "message": f"HTML5 upload completed: {value}",
            "evidence": {"file": value}
        }

    def validate(self, field_config: dict) -> list:
        errors = super().validate(field_config)
        hc = field_config.get("handler_config", {})
        mode = hc.get("mode", "native")
        if mode == "html5_uploader":
            # The upload button is OPTIONAL now — html5_uploader mode sets files
            # directly on the hidden file input (clicking the button would open
            # a native file dialog). Base validate() already requires `selector`;
            # file_input_selector falls back to `selector` at runtime, so no
            # extra hard requirement is needed.
            if not hc.get("file_input_selector") and not field_config.get("selector"):
                errors.append(
                    "html5_uploader mode requires 'file_input_selector' in "
                    "handler_config or a 'selector' fallback"
                )
        return errors
