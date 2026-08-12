"""
AutoCompleteHandler - Built-in handler for 'autocomplete' field type.
Handles custom autocomplete/dropdown widgets (iValua SelectorControl components).

Supports two modes via handler_config.mode:
  - "dropdown": Click selector div, type into _search input, select from dropdown items
  - "autocompletion": Type into _search input (triggers server-side search), select from suggestions

Supports a two-step search-then-select interaction for iValua SelectorControl widgets:
when handler_config.search_value is set, the search input receives the search term
(typed character-by-character via press_sequentially) while dropdown items are
matched against the field value (displayed text).
handler_config.result_selector overrides the default dropdown item selector.

Typing is done with press_sequentially (per keystroke) rather than a single fill():
iValua's SelectorControl fires a server-side AJAX search (GetQueryHandle) for each
character typed, so the dropdown results only render after the per-character search
chain completes. A one-shot fill() fires a single input event and never populates
the dropdown.
"""

import logging
import re
from typing import Any

from logging_setup import mask_value
from .base_handler import BaseHandler

logger = logging.getLogger(__name__)

# Common PO/GR prefixes (case-insensitive) that iValua prepends to order/receipt
# numbers in dropdown item labels. Stripped in _normalize() so a digits-only Excel
# value ("600123") still matches "PO-600123" / "PO0147739" dropdown items.
_PREFIX_RE = re.compile(r"^(po|gr)[\s-]*", re.IGNORECASE)


class AutoCompleteHandler(BaseHandler):
    """Handles 'autocomplete' field type - custom SelectorControl widgets (iValua).

    Two-step interaction (handler_config.search_value): type the search term into
    the _search input character-by-character via press_sequentially (each keystroke
    triggers iValua's server-side AJAX search, so the dropdown results only appear
    after the per-character search chain), wait for results, then click the dropdown
    item whose text matches the field value. handler_config.result_selector overrides
    the default dropdown item selector (default "{selector} {dropdown_selector}").
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
        # Two-step search-then-select: when set, the search input receives
        # search_value (the search term, typed per keystroke) while dropdown items
        # are matched against the field value (the displayed text of the desired result).
        search_value = hc.get("search_value")
        logger.debug(
            "[autocomplete] start selector=%s value=%s mode=%s",
            selector, mask_value(value), mode,
        )
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
        # Per-character AJAX search + server round-trip takes longer than a single
        # fill, so the default wait after typing is higher (still configurable).
        wait_ms = hc.get("wait_after_input_ms", 3000)
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
            logger.debug("[autocomplete] main element visible %s", selector)

            # 2. Click the selector div to activate/focus it (opens dropdown in "dropdown" mode,
            #    focuses the control in "autocompletion" mode)
            main_element.click()
            logger.debug("[autocomplete] clicked selector div %s", selector)

            # 3. Find the search input and type the value character-by-character
            search_input = self._find_search_input(search_sel, main_element)
            if search_input is None:
                return {
                    "success": False,
                    "message": f"Search input not found: {search_sel}",
                    "evidence": {"selector": selector}
                }

            if clear_before:
                search_input.fill("")

            search_term = str(search_value) if search_value is not None else str(value)
            # Type character-by-character so the widget's per-keystroke
            # server-side search (iValua GetQueryHandle AJAX) fires.
            # This is what makes the dropdown results appear at all.
            press_delay = hc.get("delay_between_chars", 50)
            search_input.press_sequentially(search_term, delay=press_delay)
            logger.debug(
                "[autocomplete] typed '%s' into search %s (clear=%s, delay=%s)",
                mask_value(search_term), search_sel, clear_before, press_delay,
            )

            # 4. Wait for suggestions to appear (server roundtrip in autocompletion mode,
            #    dropdown render in dropdown mode)
            self.page.wait_for_timeout(wait_ms)

            # 5. Locate dropdown items (custom result_selector, or the default
            #    scoped under the field's selector) and select the matching item.
            #    Items are always matched against the field value.
            item_selector = result_sel or f"{selector} {dropdown_sel}"
            items = self.page.locator(item_selector)
            item_count = items.count()
            first5 = []
            for i in range(min(item_count, 5)):
                try:
                    t = items.nth(i).text_content()
                    first5.append(mask_value((t or "").strip()))
                except Exception:
                    first5.append("?")
            logger.debug("[autocomplete] dropdown items=%d first5=%s", item_count, first5)

            if item_count > 0:
                match_status = self._select_matching_item(items, str(value))
            else:
                logger.warning(
                    "[autocomplete] NO dropdown items appeared for value=%s (selector=%s)",
                    mask_value(value), selector,
                )
                # If no dropdown items appeared, attempt JS fallback
                if hidden_sel:
                    logger.debug("[autocomplete] setting hidden input %s=%s", hidden_sel, mask_value(value))
                    self._set_hidden_input(hidden_sel, value)

                evidence = {
                    "selector": selector,
                    "value": value,
                    "mode": mode,
                }
                if search_value is not None:
                    evidence["search_value"] = search_value
                evidence["warning"] = "未找到下拉选项，可能搜索无结果，请人工确认"

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
                logger.debug("[autocomplete] setting hidden input %s=%s", hidden_sel, mask_value(value))
                self._set_hidden_input(hidden_sel, value)

            evidence = {
                "selector": selector,
                "value": value,
                "mode": mode,
            }
            if search_value is not None:
                evidence["search_value"] = search_value

            if match_status == "fallback":
                evidence["warning"] = "未找到匹配项，已选中第一项，可能不是目标订单，请人工确认"

            logger.debug("[autocomplete] success selected value=%s", mask_value(value))
            return {
                "success": True,
                "message": f"Selected '{value}' from autocomplete '{selector}'",
                "evidence": evidence
            }

        except Exception as e:
            logger.debug("[autocomplete] failed for %s: %s", selector, e)
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

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize a display/text value into a comparison key.

        - Keeps only the first ' - ' separated token, so vendor/description
          suffixes (e.g. " - Vendor A") never affect matching.
        - Strips common PO/GR prefixes (PO-, PO, GR-, GR) case-insensitively.
        - Lowercases and strips surrounding whitespace.

        Conservative by design: values that match no prefix pattern (e.g. email
        addresses like "jo@gmail.com") pass through untouched apart from the
        lowercase/trim, so approver-field matching is unchanged.
        """
        token = (text or "").split(" - ")[0]
        token = _PREFIX_RE.sub("", token)
        return token.strip().lower()

    def _select_matching_item(self, items, value: str) -> str:
        """
        Select a dropdown item matching the given value.

        Priority: exact (normalized keys equal) > partial (normalized value is a
        case-insensitive substring of the normalized item) > first item.

        Returns a match status string: "exact", "partial", or "fallback".
        Matching is done on normalized comparison keys only - the clicked item
        always uses its original displayed text (item_text is never rewritten).
        """
        value_key = self._normalize(value)

        # 1. Try exact match (normalized comparison keys)
        for i in range(items.count()):
            item_raw = items.nth(i).text_content()
            item_text = item_raw.strip() if item_raw is not None else ""
            logger.debug("[autocomplete] exact match: searching item=%s", mask_value(item_text))
            if self._normalize(item_text) == value_key:
                items.nth(i).click()
                logger.debug("[autocomplete] exact match item='%s' clicked", mask_value(item_text))
                return "exact"

        # 2. Try case-insensitive partial match (only when the normalized key is
        #    non-empty, otherwise an empty key would match every item)
        if value_key:
            for i in range(items.count()):
                item_raw = items.nth(i).text_content()
                item_text = item_raw.strip() if item_raw is not None else ""
                logger.debug(
                    "[autocomplete] partial match: value='%s' vs item='%s'",
                    mask_value(value), mask_value(item_text),
                )
                if value_key in self._normalize(item_text):
                    items.nth(i).click()
                    logger.debug("[autocomplete] partial match item='%s' clicked", mask_value(item_text))
                    return "partial"

        # 3. Fall back to first item
        first_text = items.first.text_content()
        logger.debug(
            "[autocomplete] NO exact/partial match - fallback to first item='%s'",
            mask_value(first_text or ""),
        )
        items.first.click()
        return "fallback"

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
