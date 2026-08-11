"""
CheckboxHandler - Built-in handler for 'checkbox' field type.
Handles checkbox toggling with flexible boolean value parsing.
"""

import logging
from typing import Any

from logging_setup import mask_value
from .base_handler import BaseHandler

logger = logging.getLogger(__name__)


class CheckboxHandler(BaseHandler):
    """Handles 'checkbox' field type."""

    def _parse_bool(self, value) -> bool:
        """Parse various value formats into a boolean.

        Supports:
            - bool: True/False
            - int/float: 0 = False, non-zero = True
            - str: "true", "1", "yes", "on", "y" = True (case-insensitive)
            - other: Python bool() conversion
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on", "y")
        return bool(value)

    def execute(self, field_config: dict, value: str) -> dict:
        """
        Execute field filling logic for checkboxes.

        Supports force_click option in handler_config for stubborn elements.
        Parses boolean values from strings, integers, and booleans.

        Args:
            field_config: Field configuration from workflow.json
            value: Value to fill into the field (truthy/falsy)

        Returns:
            {"success": bool, "message": str, "evidence": dict}
        """
        selector = field_config.get("selector", "")
        if not selector:
            return {"success": False, "message": "No selector provided", "evidence": {}}

        logger.debug("[checkbox] start selector=%s value=%s", selector, mask_value(value))

        try:
            element = self.page.locator(selector)
            if element.count() == 0:
                return {"success": False, "message": f"Element not found: {selector}", "evidence": {}}

            bool_value = self._parse_bool(value)
            logger.debug("[checkbox] parsed value=%s", bool_value)
            hc = field_config.get("handler_config", {})
            force_click = hc.get("force_click", False)

            if force_click:
                if bool_value:
                    action_name = "check"
                    element.check()
                else:
                    action_name = "uncheck"
                    element.uncheck()
            else:
                action_name = "set_checked"
                element.set_checked(bool_value)

            logger.debug("[checkbox] action=%s on %s (force=%s)", action_name, selector, force_click)

            logger.debug("[checkbox] success %s", selector)
            return {
                "success": True,
                "message": f"Checkbox '{selector}' set to {bool_value}",
                "evidence": {"selector": selector, "value": bool_value}
            }
        except Exception as e:
            logger.debug("[checkbox] failed %s: %s", selector, e)
            return {
                "success": False,
                "message": f"Failed to set checkbox '{selector}': {str(e)}",
                "evidence": {"error": str(e)}
            }

    def validate(self, field_config: dict) -> list:
        errors = super().validate(field_config)
        # Checkbox handler expects a boolean-interpretable value
        return errors
