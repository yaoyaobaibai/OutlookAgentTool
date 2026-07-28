"""
DatePickerHandler - Built-in handler for 'datepicker' field type.

Supports two modes:
1. "direct_input" (default) - Fill date input field directly via Playwright fill()
2. "popup" - Interact with calendar popup (e.g. CSMS Cal.aspx style)
"""

import datetime
from typing import Any, Tuple

from .base_handler import BaseHandler


class DatePickerHandler(BaseHandler):
    """Handles 'datepicker' field type with two modes: direct_input and popup."""

    def execute(self, field_config: dict, value: str) -> dict:
        """
        Execute date picker field filling.

        Args:
            field_config: Field configuration from workflow.json
            value: Date value to fill (supports datetime, YYYY-MM-DD, MM/DD/YYYY, etc.)

        Returns:
            {"success": bool, "message": str, "evidence": dict}
        """
        selector = field_config.get("selector", "")
        if not selector:
            return {"success": False, "message": "No selector provided", "evidence": {}}

        try:
            hc = field_config.get("handler_config", {})
            mode = hc.get("mode", "direct_input")

            if mode == "popup":
                return self._execute_popup(field_config, selector, value, hc)
            else:
                return self._execute_direct_input(field_config, selector, value, hc)

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to fill datepicker '{selector}': {str(e)}",
                "evidence": {"error": str(e)}
            }

    def _execute_direct_input(self, field_config: dict, selector: str, value: str, hc: dict) -> dict:
        """Fill date input field directly using Playwright fill()."""
        element = self.page.locator(selector)
        if element.count() == 0:
            return {"success": False, "message": f"Element not found: {selector}", "evidence": {}}

        element.wait_for(state="visible", timeout=5000)

        # Parse and format the date
        date_format = hc.get("date_format", "MM/DD/YYYY")
        year, month, day = self._parse_date(value)
        formatted_date = self._format_date(year, month, day, date_format)

        # Clear and fill
        element.fill("")
        element.fill(formatted_date)

        # Trigger change and blur events for reactive forms
        self.page.evaluate("""(selector) => {
            const el = document.querySelector(selector);
            if (el) {
                el.dispatchEvent(new Event('change', { bubbles: true, cancelable: true }));
                el.dispatchEvent(new Event('blur', { bubbles: true, cancelable: true }));
            }
        }""", selector)

        return {
            "success": True,
            "message": f"Filled date '{formatted_date}' into '{selector}'",
            "evidence": {
                "selector": selector,
                "value": formatted_date,
                "mode": "direct_input"
            }
        }

    def _execute_popup(self, field_config: dict, selector: str, value: str, hc: dict) -> dict:
        """Open calendar popup, select year/month/day, and wait for popup to close."""
        trigger_selector = hc.get("trigger_selector")
        if not trigger_selector:
            return {
                "success": False,
                "message": "Missing 'trigger_selector' in handler_config for popup mode",
                "evidence": {}
            }

        # Parse date components
        year, month, day = self._parse_date(value)

        # Find and click the trigger button to open the popup
        trigger = self.page.locator(trigger_selector)
        if trigger.count() == 0:
            return {"success": False, "message": f"Trigger element not found: {trigger_selector}", "evidence": {}}

        trigger.wait_for(state="visible", timeout=5000)

        # Use expect_popup to capture the popup window
        with self.page.expect_popup() as popup_info:
            trigger.click()

        popup_page = popup_info.value
        popup_wait_ms = hc.get("popup_wait_timeout_ms", 5000)
        popup_page.wait_for_load_state(state="load", timeout=popup_wait_ms)

        # Select year
        year_selector = hc.get("year_selector", "select[id*='ddlYear']")
        year_elem = popup_page.locator(year_selector)
        if year_elem.count() > 0:
            year_elem.wait_for(state="visible", timeout=3000)
            year_elem.select_option(value=year)

        # Select month
        month_selector = hc.get("month_selector", "select[id*='ddlMonth']")
        month_elem = popup_page.locator(month_selector)
        if month_elem.count() > 0:
            month_elem.wait_for(state="visible", timeout=3000)
            month_elem.select_option(value=month)

        # Click the day link
        day_pattern = hc.get("day_pattern", "a:text('{day}')")
        day_selector = day_pattern.replace("{day}", day)
        day_elem = popup_page.locator(day_selector)
        if day_elem.count() == 0:
            popup_page.close()
            return {
                "success": False,
                "message": f"Day link not found for day {day} using selector: {day_selector}",
                "evidence": {"year": year, "month": month, "day": day}
            }

        day_elem.first.click()

        # Popup should auto-close after day selection; wait briefly
        popup_page.wait_for_timeout(500)

        return {
            "success": True,
            "message": f"Selected date {year}-{month}-{day} via popup",
            "evidence": {
                "year": year,
                "month": month,
                "day": day,
                "mode": "popup"
            }
        }

    def _parse_date(self, value) -> Tuple[str, str, str]:
        """
        Parse date from various input formats.

        Supported formats:
        - datetime.datetime object
        - YYYY-MM-DD or YYYY-MM-DD HH:MM:SS (Excel datetime string)
        - MM/DD/YYYY
        - YYYY/MM/DD

        Returns:
            (year, month, day) as zero-padded strings
        """
        if isinstance(value, datetime.datetime):
            return str(value.year), str(value.month).zfill(2), str(value.day).zfill(2)

        value = str(value).strip()

        # YYYY-MM-DD or YYYY-MM-DD HH:MM:SS (Excel datetime)
        if '-' in value:
            date_part = value.split(' ')[0]
            parts = date_part.split('-')
            if len(parts) == 3:
                return parts[0], parts[1], parts[2]

        # MM/DD/YYYY or YYYY/MM/DD
        if '/' in value:
            parts = value.split('/')
            if len(parts) == 3:
                # If first part is 4 digits, it's YYYY/MM/DD
                if len(parts[0]) == 4:
                    return parts[0], parts[1], parts[2]
                # Otherwise MM/DD/YYYY
                return parts[2], parts[0], parts[1]

        raise ValueError(f"Unrecognized date format: {value}")

    def _format_date(self, year: str, month: str, day: str, fmt: str = "MM/DD/YYYY") -> str:
        """Format date components to target output format."""
        if fmt == "MM/DD/YYYY":
            return f"{month}/{day}/{year}"
        elif fmt == "DD/MM/YYYY":
            return f"{day}/{month}/{year}"
        elif fmt == "YYYY-MM-DD":
            return f"{year}-{month}-{day}"
        # Default fallback
        return f"{month}/{day}/{year}"

    def validate(self, field_config: dict) -> list:
        errors = super().validate(field_config)
        hc = field_config.get("handler_config", {})
        mode = hc.get("mode", "direct_input")

        if mode == "popup" and not hc.get("trigger_selector"):
            errors.append("Popup mode requires 'trigger_selector' in handler_config")

        return errors
