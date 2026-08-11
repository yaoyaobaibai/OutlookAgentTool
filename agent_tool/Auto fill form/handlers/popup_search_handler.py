"""
PopupSearchHandler - Built-in handler for 'popup_search' field type.

Handles fields that require: clicking a trigger -> popup/iframe opens ->
configurable search steps -> select result -> popup closes.

This is designed for fields like CSMS's Priming Project Manager, where
a trigger button opens a search popup for selecting values.
"""

import logging
from typing import Any

from logging_setup import mask_value
from .base_handler import BaseHandler

logger = logging.getLogger(__name__)


class PopupSearchHandler(BaseHandler):
    """Handles 'popup_search' field type - popup search-and-select fields."""

    def execute(self, field_config: dict, value: str) -> dict:
        """
        Execute popup search-and-select logic.

        Flow:
        1. Click trigger button (trigger_selector)
        2. Detect popup (try popup event -> iframe -> main page fallback)
        3. Execute configured steps sequentially inside the popup
        4. Return result

        Args:
            field_config: Field configuration from workflow.json
            value: Value to fill into the field (passed to step actions)

        Returns:
            {"success": bool, "message": str, "evidence": dict}
        """
        selector = field_config.get("selector", "")
        if not selector:
            return {"success": False, "message": "No selector provided", "evidence": {}}

        hc = field_config.get("handler_config", {})
        trigger_sel = hc.get("trigger_selector", selector)
        popup_timeout_ms = hc.get("popup_timeout_ms", 10000)
        steps = hc.get("steps", [])

        logger.debug("[popup_search] start trigger=%s value=%s", trigger_sel, mask_value(value))

        try:
            # --- Step 1: Click trigger button ---
            print(f"  Clicking trigger: '{trigger_sel}'")
            trigger = self.page.locator(trigger_sel).first
            trigger.wait_for(state="visible", timeout=5000)
            trigger.click()
            print(f"  ✓ Trigger clicked")

            # --- Step 2: Detect popup/iframe ---
            popup = self._detect_popup(popup_timeout_ms)
            detected = popup is not None
            if popup is None:
                print(f"  ℹ No popup detected, falling back to main page")
                popup = self.page
            is_iframe = detected and not hasattr(popup, "wait_for_load_state")
            logger.debug("[popup_search] popup detected=%s (iframe=%s)", detected, is_iframe)

            # Wait for popup to settle
            try:
                popup.wait_for_load_state("networkidle")
            except Exception:
                pass

            # --- Step 3: Execute configured steps ---
            steps_executed = 0
            for i, step in enumerate(steps):
                try:
                    self._execute_step(popup, step, value, i)
                    steps_executed += 1
                except Exception as e:
                    print(f"  Step {i + 1} failed: {e}")
                    logger.warning("[popup_search] step %s failed: %s", step.get("action", ""), e)
                    # Continue with next step (non-fatal)

            logger.debug("[popup_search] success %s (%s/%s steps)", selector, steps_executed, len(steps))
            return {
                "success": True,
                "message": f"Popup search completed for '{selector}' ({steps_executed}/{len(steps)} steps executed)",
                "evidence": {
                    "steps_configured": len(steps),
                    "steps_executed": steps_executed,
                    "trigger_selector": trigger_sel,
                },
            }

        except Exception as e:
            logger.debug("[popup_search] failed: %s", e)
            return {
                "success": False,
                "message": f"Popup search failed: {str(e)}",
                "evidence": {"error": str(e)},
            }

    def _detect_popup(self, timeout_ms: int):
        """
        Detect popup window or iframe after clicking trigger.

        Detection order:
        1. Wait for 'popup' event (new browser window)
        2. Try iframe detection (name/id containing 'popup')
        3. Fall back to None (caller uses main page)

        Returns:
            Popup page, frame_locator, or None
        """
        popup = None

        # Method 1: Popup event (new browser window)
        try:
            popup = self.page.wait_for_event("popup", timeout=timeout_ms)
            print(f"  ✓ Popup detected (new window)")
            return popup
        except Exception:
            print(f"  ℹ No popup event detected")

        # Method 2: Iframe fallback
        try:
            iframe = self.page.frame_locator(
                'iframe[name*="popup"], iframe[id*="popup"], '
                'iframe[name*="search"], iframe[id*="search"], '
                'iframe[name*="dialog"], iframe[id*="dialog"]'
            ).first
            # Probe iframe to verify it's accessible
            if iframe.locator("body").count() > 0:
                print(f"  ✓ Popup detected (iframe)")
                return iframe
        except Exception:
            print(f"  ℹ No iframe detected")

        return None

    def _execute_step(self, context, step: dict, value: str, index: int):
        """
        Execute a single step inside the popup context.

        Supported actions:
            - fill: Fill text into an input
            - click: Click an element
            - wait: Pause execution
            - select_option: Select an option from a dropdown
            - evaluate: Run JavaScript in the page

        Args:
            context: Page or FrameLocator to operate on
            step: Step configuration dict
            value: The original field value (used as default step value)
            index: Step index (for logging)
        """
        action = step.get("action", "")
        sel = step.get("selector", "")
        step_value = step.get("value", value)
        step_num = index + 1

        logger.debug("[popup_search] step %s selector=%s value=%s", action, sel, mask_value(step_value))

        if action == "fill":
            print(f"    Step {step_num}: fill '{step_value}' into '{sel}'")
            locator = context.locator(sel)
            locator.wait_for(state="visible", timeout=5000)
            locator.fill("")
            locator.fill(step_value)

        elif action == "click":
            print(f"    Step {step_num}: click '{sel}'")
            locator = context.locator(sel).first
            locator.wait_for(state="visible", timeout=5000)
            locator.click()

        elif action == "wait":
            wait_ms = step.get("timeout_ms", 1000)
            print(f"    Step {step_num}: wait {wait_ms}ms")
            context.wait_for_timeout(wait_ms)

        elif action == "select_option":
            print(f"    Step {step_num}: select_option '{step_value}' in '{sel}'")
            locator = context.locator(sel)
            locator.wait_for(state="visible", timeout=5000)
            locator.select_option(step_value)

        elif action == "evaluate":
            script = step.get("script", "")
            print(f"    Step {step_num}: evaluate script")
            context.evaluate(script)

        else:
            print(f"    Step {step_num}: unknown action '{action}', skipping")

    def validate(self, field_config: dict) -> list:
        """
        Validate field_config for popup_search type.

        Checks:
        - Base handler validation (selector required)
        - trigger_selector presence (recommended)

        Returns:
            List of error messages (empty = valid)
        """
        errors = super().validate(field_config)
        hc = field_config.get("handler_config", {})
        if not hc.get("trigger_selector"):
            errors.append("Missing recommended 'trigger_selector' in handler_config")
        return errors
