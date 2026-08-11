"""
SelectHandler - Built-in handler for 'select' field type.
Handles native HTML <select> dropdowns with ASP.NET __doPostBack support.
"""

import logging
from typing import Any

from logging_setup import mask_value
from .base_handler import BaseHandler

logger = logging.getLogger(__name__)


class SelectHandler(BaseHandler):
    """Handles 'select' field type - native HTML <select> dropdowns."""

    def execute(self, field_config: dict, value: str) -> dict:
        """
        Execute field filling logic using Playwright select_option().

        Supports value_type: "value" (default) or "label" selection.
        Supports triggering change events and __doPostBack for ASP.NET forms.

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
            element = self.page.locator(selector)
            if element.count() == 0:
                return {"success": False, "message": f"Element not found: {selector}", "evidence": {}}

            element.wait_for(state="visible", timeout=5000)

            hc = field_config.get("handler_config", {})
            value_type = hc.get("value_type", "value")  # "value" or "label"
            logger.debug("[select] start selector=%s value=%s value_type=%s", selector, mask_value(value), value_type)
            trigger_change = hc.get("trigger_change_event", True)
            trigger_postback = hc.get("trigger_postback", False)
            wait_after = hc.get("wait_after_ms", 1000)

            # Select by value or label
            mode_label = "label" if value_type == "label" else "value"
            logger.debug("[select] select_option %s=%s on %s", mode_label, mask_value(value), selector)
            if value_type == "label":
                element.select_option(label=value)
            else:
                element.select_option(value=value)

            # Trigger change event for ASP.NET or dynamic forms
            if trigger_change or trigger_postback:
                element_id = selector.replace("#", "").replace(" ", "")
                postback_str = str(trigger_postback).lower()
                self.page.evaluate(f"""(id) => {{
                    var elem = document.getElementById(id);
                    if (elem) {{
                        elem.dispatchEvent(new Event('change', {{ bubbles: true, cancelable: true }}));
                        if (typeof __doPostBack === 'function' && {postback_str}) {{
                            setTimeout(() => __doPostBack(elem.id, ''), 100);
                        }}
                    }}
                }}""", element_id)
                logger.debug("[select] dispatched change/postback on %s", selector)

            self.page.wait_for_timeout(wait_after)

            logger.debug("[select] success %s", selector)
            return {
                "success": True,
                "message": f"Selected '{value}' in '{selector}'",
                "evidence": {"selector": selector, "value": value}
            }
        except Exception as e:
            logger.debug("[select] failed %s: %s", selector, e)
            return {
                "success": False,
                "message": f"Failed to select in '{selector}': {str(e)}",
                "evidence": {"error": str(e)}
            }

    def validate(self, field_config: dict) -> list:
        errors = super().validate(field_config)
        # Select handler requires a valid <select> element selector
        return errors
