"""
InputHandler - Built-in handler for 'input' field type.
Handles text inputs and textareas using Playwright fill().
"""

from typing import Any
from .base_handler import BaseHandler


class InputHandler(BaseHandler):
    """Handles 'input' field type - text inputs and textareas."""

    def execute(self, field_config: dict, value: str) -> dict:
        """
        Execute field filling logic using Playwright fill().

        Args:
            field_config: Field configuration from workflow.json
            value: Value to fill into the field

        Returns:
            {"success": bool, "message": str, "evidence": dict}
        """
        selector = field_config.get("selector", "")
        if not selector:
            return {"success": False, "message": "No selector provided", "evidence": {}}

        try:
            iframe_selector = field_config.get("handler_config", {}).get("iframe_selector", "")
            if iframe_selector:
                # Field lives inside an iframe (e.g. modal.aspx delivery_item_manage)
                element = self.page.frame_locator(iframe_selector).locator(selector)
            else:
                element = self.page.locator(selector)

            if element.count() == 0:
                return {"success": False, "message": f"Element not found: {selector}", "evidence": {}}

            element.wait_for(state="visible", timeout=5000)

            clear_first = field_config.get("handler_config", {}).get("clear_first", True)
            if clear_first:
                element.fill("")
            element.fill(str(value))

            evidence = {"selector": selector, "value": value}
            if iframe_selector:
                evidence["iframe"] = iframe_selector
            return {
                "success": True,
                "message": f"Filled '{value}' into '{selector}'",
                "evidence": evidence
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to fill '{selector}': {str(e)}",
                "evidence": {"error": str(e)}
            }

    def validate(self, field_config: dict) -> list:
        errors = super().validate(field_config)
        # Input handler supports both <input> and <textarea> elements
        return errors
