"""
AutoCompleteHandler - Built-in handler for 'autocomplete' field type.
Handles custom autocomplete/dropdown widgets (iValua SelectorControl components).

Supports two modes via handler_config.mode:
  - "dropdown": Click selector div, type into _search input, select from dropdown items
  - "autocompletion": Type into _search input (triggers server-side search), select from suggestions

Supports a two-step search-then-select interaction for iValua SelectorControl widgets:
when handler_config.search_value is set, the search input is filled with the search
term while dropdown items are matched against the field value (displayed text).
handler_config.result_selector overrides the default dropdown item selector.
"""

from typing import Any
from .base_handler import BaseHandler


class AutoCompleteHandler(BaseHandler):
    """Handles 'autocomplete' field type - custom SelectorControl widgets (iValua).

    Two-step interaction (handler_config.search_value): type the search term into
    the _search input (server-side AJAX search), wait for results, then click the
    dropdown item whose text matches the field value. handler_config.result_selector
    overrides the default dropdown item selector (default "{selector} {dropdown_selector}").
    """

    def execute(self, field_config: dict, value: str) -> dict:
        """
        Execute field filling logic for iValua SelectorControl widgets.

        Args:
            field_config: Field configuration from workflow.json
            value: Value to fill into the field

        Returns:
            {"success": bool, "message": str, "evidence": dict}
        """
        selector = field_config.get("selector", "")
        if not selector:
            return {"success": False, "message": "No selector provided", "evidence": {}}

        hc = field_config.get("handler_config", {})
        mode = hc.get("mode", "dropdown")
        # Two-step search-then-select: when set, the search input is filled with
        # search_value (the search term) while dropdown items are matched against
        # the field value (the displayed text of the desired result).
        search_value = hc.get("search_value")
        # Accept both the legacy search_input_selector key and the schema-level
        # search_selector key used by existing workflows, falling back to the
        # conventional "{selector}_search" suffix.
        search_sel = (
            hc.get("search_input_selector")
            or hc.get("search_selector")
            or f"{selector}_search"
        )
        # result_selector overrides the default dropdown item selector so custom
        # widgets (e.g. iValua "{selector}_MenuItem span.text") can be targeted.
        result_sel = hc.get("result_selector")
        dropdown_sel = hc.get("dropdown_selector", ".menu > .item")
        wait_ms = hc.get("wait_after_input_ms", 1000)
        clear_before = hc.get("clear_before", True)
        hidden_sel = hc.get("hidden_input_selector")

        try:
            # 1. Verify main selector element exists and is visible
            main_element = self.page.locator(selector)
            if main_element.count() == 0:
                return {
                    "success": False,
                    "message": f"Element not found: {selector}",
                    "evidence": {}
                }
            main_element.wait_for(state="visible", timeout=5000)

            # 2. Click the selector div to activate/focus it (opens dropdown in "dropdown" mode,
            #    focuses the control in "autocompletion" mode)
            main_element.click()

            # 3. Find the search input and fill the value
            search_input = self._find_search_input(search_sel, main_element)
            if search_input is None:
                return {
                    "success": False,
                    "message": f"Search input not found: {search_sel}",
                    "evidence": {"selector": selector}
                }

            if clear_before:
                search_input.fill("")

            if search_value is not None:
                # Two-step: fill the search term (triggers server-side search),
                # then select the result whose displayed text matches the value.
                search_input.fill(str(search_value))
            else:
                # Backward compatible: fill the field value itself.
                search_input.fill(str(value))

            # 4. Wait for suggestions to appear (server roundtrip in autocompletion mode,
            #    dropdown render in dropdown mode)
            self.page.wait_for_timeout(wait_ms)

            # 5. Locate dropdown items (custom result_selector, or the default
            #    scoped under the field's selector) and select the matching item.
            #    Items are always matched against the field value.
            item_selector = result_sel or f"{selector} {dropdown_sel}"
            items = self.page.locator(item_selector)
            item_count = items.count()

            if item_count > 0:
                self._select_matching_item(items, str(value))
            else:
                # If no dropdown items appeared, attempt JS fallback
                if hidden_sel:
                    self._set_hidden_input(hidden_sel, value)

                evidence = {
                    "selector": selector,
                    "value": value,
                    "mode": mode,
                }
                if search_value is not None:
                    evidence["search_value"] = search_value
                evidence["warning"] = "No dropdown items appeared"

                return {
                    "success": True,
                    "message": (
                        f"Filled '{value}' on '{selector}', "
                        "no dropdown items appeared to select"
                    ),
                    "evidence": evidence
                }

            # 6. Optionally set hidden input as extra fallback
            if hidden_sel:
                self._set_hidden_input(hidden_sel, value)

            evidence = {
                "selector": selector,
                "value": value,
                "mode": mode,
            }
            if search_value is not None:
                evidence["search_value"] = search_value

            return {
                "success": True,
                "message": f"Selected '{value}' from autocomplete '{selector}'",
                "evidence": evidence
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Autocomplete failed for '{selector}': {str(e)}",
                "evidence": {"error": str(e)}
            }

    def _find_search_input(self, search_sel: str, main_element) -> Any:
        """
        Find the search input element. Retries with a second click if not found initially,
        since the input may only appear after the selector is activated.
        """
        search_input = self.page.locator(search_sel)
        if search_input.count() == 0:
            # The search input may not be rendered until the selector is clicked;
            # click again and wait briefly
            main_element.click()
            self.page.wait_for_timeout(500)
            search_input = self.page.locator(search_sel)
            if search_input.count() == 0:
                return None

        search_input.wait_for(state="visible", timeout=5000)
        # Click the search input before filling (mirrors the real interaction:
        # focus the _search field, then type) so the control is guaranteed active.
        search_input.click()
        return search_input

    def _select_matching_item(self, items, value: str) -> None:
        """
        Select a dropdown item matching the given value.
        Priority: exact match > partial (case-insensitive) match > first item.
        """
        clicked = False

        # 1. Try exact match
        for i in range(items.count()):
            item_text = items.nth(i).text_content().strip()
            if item_text == value:
                items.nth(i).click()
                clicked = True
                break

        # 2. Try case-insensitive partial match
        if not clicked:
            value_lower = value.lower()
            for i in range(items.count()):
                item_text = items.nth(i).text_content().strip()
                if value_lower in item_text.lower():
                    items.nth(i).click()
                    clicked = True
                    break

        # 3. Fall back to first item
        if not clicked:
            items.first.click()

    def _set_hidden_input(self, hidden_sel: str, value: str) -> None:
        """Set a hidden input's value via JavaScript as safety fallback."""
        try:
            self.page.evaluate(
                """([sel, val]) => {
                    const el = document.querySelector(sel);
                    if (el) el.value = val;
                }""",
                [hidden_sel, str(value)]
            )
        except Exception:
            pass  # Silent fail - this is a best-effort fallback

    def validate(self, field_config: dict) -> list:
        errors = super().validate(field_config)
        hc = field_config.get("handler_config", {})
        mode = hc.get("mode", "dropdown")
        if mode not in ("dropdown", "autocompletion"):
            errors.append(
                f"Invalid handler_config.mode '{mode}'. "
                "Must be 'dropdown' or 'autocompletion'."
            )
        return errors
