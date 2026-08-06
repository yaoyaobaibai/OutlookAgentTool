#!/usr/bin/env python3
"""
tests/test_autocomplete_handler.py — Tests for AutoCompleteHandler's two-step
search-then-select interaction (iValua SelectorControl widgets).

Covers:
  1. Two-step: handler_config.search_value fills the search input with the search
     term, while the clicked dropdown item is matched against the field value.
  2. handler_config.result_selector overrides the default dropdown item selector.
  3. handler_config.search_selector (schema key) is honoured alongside the legacy
     search_input_selector key.
   4. Backward compatibility: without search_value, the field value itself is typed
      into the search input (identical to previous behaviour).
   5. No results after search -> success with a warning (not a hard failure).
   6. hidden_input_selector JS fallback still runs when no items appear.
   7. press_sequentially (per-keystroke typing) is used for the search input — not a
      single fill() — so iValua's per-character AJAX search fires.

All tests are OFFLINE-SAFE — a MockPage records interactions; no Playwright browser
is launched. Runnable directly (`python tests/test_autocomplete_handler.py`) or via
pytest (`python -m pytest tests/test_autocomplete_handler.py -v`).
"""

import os
import sys

# Project root — add to sys.path so `handlers` imports from anywhere
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from handlers import get_handler


class MockLocator:
    """Playwright-like locator that records interactions on a MockPage.

    `selector` is the CSS selector; `index` is set when returned from nth()/first().
    """

    def __init__(self, page, selector, index=None):
        self.page = page
        self.selector = selector
        self.index = index

    # --- existence / visibility ---
    def count(self):
        return self.page.locator_counts.get(self.selector, 1)

    def wait_for(self, **kwargs):
        self.page.wait_for_calls.append((self.selector, kwargs))
        return None

    # --- actions ---
    def click(self):
        self.page.clicks.append((self.selector, self.index))
        return None

    def fill(self, value):
        self.page.fills.append((self.selector, str(value)))
        return None

    def press_sequentially(self, text, delay=None):
        self.page.press_seq.append((self.selector, str(text), delay))
        return None

    # --- item traversal ---
    def nth(self, index):
        return MockLocator(self.page, self.selector, index)

    @property
    def first(self):
        return MockLocator(self.page, self.selector, 0)

    def text_content(self):
        texts = self.page.item_texts.get(self.selector, [])
        if self.index is not None:
            if 0 <= self.index < len(texts):
                return texts[self.index]
            return ""
        return texts[0] if texts else ""


class MockPage:
    """Records locator interactions so tests can assert what was filled/clicked."""

    def __init__(self):
        self.clicks = []          # [(selector, index_or_None)]
        self.fills = []           # [(selector, value)]  (used for clear_before)
        self.press_seq = []       # [(selector, text, delay)]  (per-keystroke typing)
        self.timeouts = []        # wait_for_timeout(ms) calls
        self.wait_for_calls = []  # [(selector, kwargs)]
        self.locator_counts = {}  # selector -> count()
        self.item_texts = {}      # selector -> [item texts]
        self.hidden_inputs = []   # [sel, val] pairs passed to evaluate()

    def locator(self, selector):
        return MockLocator(self, selector)

    def wait_for_timeout(self, ms):
        self.timeouts.append(ms)

    def evaluate(self, script, *args):
        # _set_hidden_input passes [hidden_sel, value] as the single argument
        self.hidden_inputs.append(args[0] if args else None)
        return None


def _make_handler(page):
    return get_handler("autocomplete")(page, {})


# ---------------------------------------------------------------------------
# Two-step search-then-select
# ---------------------------------------------------------------------------

def test_two_step_search_then_select():
    """search_value is typed, then the item whose text matches the value is clicked."""
    page = MockPage()
    page.item_texts["#sel_results .text"] = [
        "PO0147739 - 广州2026年7月京东购买（不含税）-上海圆迈贸易有限公司",
        "PO9999999 - Another order",
    ]
    handler = _make_handler(page)

    field_config = {
        "selector": "#sel",
        "handler_config": {
            "search_value": "6000017449",
            "result_selector": "#sel_results .text",
            "wait_after_input_ms": 100,
        },
    }
    result = handler.execute(field_config, "PO0147739")

    # Success, and evidence records the two-step mode
    assert result["success"] is True, result
    assert result["evidence"]["search_value"] == "6000017449"

    # The search input received the SEARCH TERM via press_sequentially (not fill),
    # and the clear_before fill("") happened first on the same input
    fills = [v for (sel, v) in page.fills if sel == "#sel_search"]
    assert fills == [""], f"expected only the clear_before fill, got {fills}"
    press_calls = [t for (sel, t, _d) in page.press_seq if sel == "#sel_search"]
    assert press_calls == ["6000017449"], press_calls
    assert ("#sel_search", "PO0147739") not in page.press_seq

    # The clicked item is the one whose displayed text contains the field value
    assert ("#sel_results .text", 0) in page.clicks, page.clicks
    assert page.item_texts["#sel_results .text"][0].find("PO0147739") != -1

    # Wait used the configured wait_after_input_ms
    assert 100 in page.timeouts, page.timeouts


def test_two_step_no_result_selector_uses_default():
    """Two-step works with the default dropdown item selector when result_selector absent."""
    page = MockPage()
    page.item_texts["#sel .menu > .item"] = [
        "PO0147739 - 广州2026年7月京东购买",
        "PO9999999 - Another order",
    ]
    handler = _make_handler(page)

    field_config = {
        "selector": "#sel",
        "handler_config": {"search_value": "6000017449"},
    }
    result = handler.execute(field_config, "PO0147739")

    assert result["success"] is True, result
    fills = [v for (sel, v) in page.fills if sel == "#sel_search"]
    assert fills == [""], fills
    press_calls = [t for (sel, t, _d) in page.press_seq if sel == "#sel_search"]
    assert press_calls == ["6000017449"], press_calls
    assert ("#sel .menu > .item", 0) in page.clicks, page.clicks


def test_two_step_no_results_returns_success_warning():
    """No dropdown items after search -> success with a warning (not a hard failure)."""
    page = MockPage()
    page.locator_counts["#sel_results .text"] = 0
    handler = _make_handler(page)

    field_config = {
        "selector": "#sel",
        "handler_config": {
            "search_value": "6000017449",
            "result_selector": "#sel_results .text",
        },
    }
    result = handler.execute(field_config, "PO0147739")

    assert result["success"] is True, result
    assert result["evidence"]["warning"] == "No dropdown items appeared"
    assert "no dropdown items appeared" in result["message"]
    # The search term was still typed (per keystroke) before giving up
    fills = [v for (sel, v) in page.fills if sel == "#sel_search"]
    assert fills == [""], fills
    press_calls = [t for (sel, t, _d) in page.press_seq if sel == "#sel_search"]
    assert "6000017449" in press_calls, press_calls


# ---------------------------------------------------------------------------
# Selector key compatibility + backward compatibility
# ---------------------------------------------------------------------------

def test_search_selector_key_supported():
    """handler_config.search_selector (schema key, used by workflows) is honoured."""
    page = MockPage()
    page.item_texts["#sel .menu > .item"] = ["PO0147739 - 广州", "PO9999999 - x"]
    handler = _make_handler(page)

    field_config = {
        "selector": "#sel",
        "handler_config": {
            "search_selector": "#body_x_tabc_prxDelivery_prxprxDelivery_x_selOrder_search",
        },
    }
    result = handler.execute(field_config, "PO0147739 - 广州")

    assert result["success"] is True, result
    fills = [v for (sel, v) in page.fills
             if sel == "#body_x_tabc_prxDelivery_prxprxDelivery_x_selOrder_search"]
    assert fills == [""], fills
    press_calls = [t for (sel, t, _d) in page.press_seq
                   if sel == "#body_x_tabc_prxDelivery_prxprxDelivery_x_selOrder_search"]
    assert press_calls == ["PO0147739 - 广州"], press_calls


def test_legacy_search_input_selector_still_supported():
    """search_input_selector (legacy key) still takes precedence."""
    page = MockPage()
    page.item_texts["#sel .menu > .item"] = ["ABC123"]
    handler = _make_handler(page)

    field_config = {
        "selector": "#sel",
        "handler_config": {"search_input_selector": "#legacy_search"},
    }
    result = handler.execute(field_config, "ABC123")

    assert result["success"] is True, result
    press_calls = [t for (sel, t, _d) in page.press_seq if sel == "#legacy_search"]
    assert press_calls == ["ABC123"], press_calls
    assert not any(sel == "#sel_search" for (sel, _t, _d) in page.press_seq)
    assert not any(sel == "#sel_search" for (sel, _v) in page.fills)


def test_selector_can_be_data_selector_div():
    """A div[data-selector='X'] selector resolves and the search fill still happens.

    The real iValua SelectorControl is a visible wrapper div addressed by its
    data-selector attribute (the hidden input it wraps is never 'visible', so it
    must not be used as the click target). This verifies execute() succeeds with
    such a selector and the search input is located and filled.
    """
    page = MockPage()
    page.item_texts["div[data-selector='body_x_tabc_prxDelivery_prxprxDelivery_x_selOrder'] .menu > .item"] = [
        "PO0147739 - 广州",
        "PO9999999 - Another order",
    ]
    handler = _make_handler(page)

    field_config = {
        "selector": "div[data-selector='body_x_tabc_prxDelivery_prxprxDelivery_x_selOrder']",
        "handler_config": {
            "mode": "autocompletion",
            "search_selector": "#body_x_tabc_prxDelivery_prxprxDelivery_x_selOrder_search",
        },
    }
    result = handler.execute(field_config, "PO0147739 - 广州")

    assert result["success"] is True, result
    fills = [v for (sel, v) in page.fills
             if sel == "#body_x_tabc_prxDelivery_prxprxDelivery_x_selOrder_search"]
    assert fills == [""], fills
    press_calls = [t for (sel, t, _d) in page.press_seq
                   if sel == "#body_x_tabc_prxDelivery_prxprxDelivery_x_selOrder_search"]
    assert press_calls == ["PO0147739 - 广州"], press_calls
    # The visible wrapper div (data-selector) is the element waited on + clicked
    div_sel = "div[data-selector='body_x_tabc_prxDelivery_prxprxDelivery_x_selOrder']"
    assert (div_sel, None) in page.clicks, page.clicks


def test_backward_compat_fill_value_directly():
    """Without search_value, the field value itself is typed (old behaviour)."""
    page = MockPage()
    page.item_texts["#sel .menu > .item"] = ["ABC123", "XYZ789"]
    handler = _make_handler(page)

    field_config = {"selector": "#sel", "handler_config": {}}
    result = handler.execute(field_config, "ABC123")

    assert result["success"] is True, result
    # clear_before fill("") happens first, then the value is typed per keystroke
    fills = [v for (sel, v) in page.fills if sel == "#sel_search"]
    assert fills == [""], fills
    press_calls = [t for (sel, t, _d) in page.press_seq if sel == "#sel_search"]
    assert press_calls == ["ABC123"], press_calls
    # Exact match item clicked
    assert ("#sel .menu > .item", 0) in page.clicks, page.clicks
    # Evidence has no search_value key (unchanged shape)
    assert "search_value" not in result["evidence"]


def test_press_sequentially_used_for_search():
    """The search input receives press_sequentially (NOT fill) with the value,
    and the clear_before fill("") still happens first."""
    page = MockPage()
    page.item_texts["#sel .menu > .item"] = ["ABC123", "XYZ789"]
    handler = _make_handler(page)

    field_config = {"selector": "#sel", "handler_config": {}}
    result = handler.execute(field_config, "ABC123")

    assert result["success"] is True, result
    # clear_before fill("") happens first on the search input
    fills = [v for (sel, v) in page.fills if sel == "#sel_search"]
    assert fills == [""], fills
    # The value is typed via press_sequentially, never via fill
    press_calls = [t for (sel, t, _d) in page.press_seq if sel == "#sel_search"]
    assert press_calls == ["ABC123"], press_calls
    assert ("#sel_search", "ABC123") not in page.fills
    # The dropdown item is still selected by matching the value
    assert ("#sel .menu > .item", 0) in page.clicks, page.clicks


# ---------------------------------------------------------------------------
# Hidden input fallback
# ---------------------------------------------------------------------------

def test_hidden_input_fallback_on_no_items():
    """hidden_input_selector JS fallback still runs when no items appear."""
    page = MockPage()
    page.locator_counts["#sel .menu > .item"] = 0
    handler = _make_handler(page)

    field_config = {
        "selector": "#sel",
        "handler_config": {"hidden_input_selector": "#sel_hidden"},
    }
    result = handler.execute(field_config, "ABC123")

    assert result["success"] is True, result
    assert page.hidden_inputs, "hidden input should be set via JS fallback"
    assert page.hidden_inputs[0] == ["#sel_hidden", "ABC123"]


# ---------------------------------------------------------------------------
# Runner (for direct execution without pytest)
# ---------------------------------------------------------------------------

def _run_all():
    tests = [
        fn for name, fn in sorted(globals().items())
        if name.startswith("test_") and callable(fn)
    ]
    passed = failed = 0
    for fn in tests:
        try:
            fn()
            print(f"[PASS] {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {fn.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[FAIL] {fn.__name__}: (exception) {e!r}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if _run_all() else 1)
