#!/usr/bin/env python3
"""
tests/test_input_handler.py — Tests for InputHandler's iframe support.

Covers:
  1. iframe_selector present -> element resolved via page.frame_locator(iframe_selector)
     and filled on a frame-scoped locator; no bare top-level page.locator() call.
  2. No handler_config -> existing behaviour unchanged: page.locator() on top scope,
     frame_locator never called, value still filled.

All tests are OFFLINE-SAFE — a MockPage records interactions; no Playwright browser
is launched. Runnable directly (`python tests/test_input_handler.py`) or via pytest
(`python -m pytest tests/test_input_handler.py -v`).
"""

import os
import sys

# Project root — add to sys.path so `handlers` imports from anywhere
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from handlers import get_handler


class MockLocator:
    """Playwright-like locator that records interactions on a MockPage."""

    def __init__(self, page, scope):
        self.page = page
        self.scope = scope  # label used in fills: e.g. "#field" or "frame:#field"

    def count(self):
        return 1

    def wait_for(self, **kwargs):
        return None

    def fill(self, value):
        self.page.fills.append((self.scope, str(value)))
        return None


class MockFrameLocator:
    """Playwright-like FrameLocator: scopes .locator() results to the frame."""

    def __init__(self, page, frame_sel):
        self.page = page
        self.frame_sel = frame_sel

    def locator(self, sel):
        self.page.frame_locator_calls.append((self.frame_sel, sel))
        return MockLocator(self.page, f"frame:{sel}")


class MockPage:
    """Records locator/frame_locator/fill interactions."""

    def __init__(self):
        self.locator_calls = []          # [("locator", sel)]
        self.frame_locator_calls = []    # [(frame_sel, inner_sel)] from MockFrameLocator.locator
        self.fills = []                  # [(scope, value)]

    def locator(self, selector):
        self.locator_calls.append(("locator", selector))
        return MockLocator(self, selector)

    def frame_locator(self, selector):
        self.locator_calls.append(("frame_locator", selector))
        return MockFrameLocator(self, selector)


def _make_handler(page):
    return get_handler("input")(page, {})


# ---------------------------------------------------------------------------
# Iframe support
# ---------------------------------------------------------------------------

def test_iframe_present():
    """iframe_selector -> element resolved inside the frame, not on top-level page."""
    page = MockPage()
    handler = _make_handler(page)

    field_config = {
        "selector": "#body_x_txtQuantity",
        "handler_config": {"iframe_selector": "#modalFrame"},
    }
    result = handler.execute(field_config, "100")

    assert result["success"] is True, result
    # frame_locator("#modalFrame") was called with the configured iframe selector
    assert ("frame_locator", "#modalFrame") in page.locator_calls, page.locator_calls
    # The inner field was scoped to the frame
    assert ("#modalFrame", "#body_x_txtQuantity") in page.frame_locator_calls, page.frame_locator_calls
    # Fill happened on the frame-scoped locator
    assert ("frame:#body_x_txtQuantity", "") in page.fills, page.fills
    assert ("frame:#body_x_txtQuantity", "100") in page.fills, page.fills
    # No bare top-level locator for the inner field selector
    assert ("locator", "#body_x_txtQuantity") not in page.locator_calls, page.locator_calls
    # Evidence records the iframe selector
    assert result["evidence"]["iframe"] == "#modalFrame", result["evidence"]


def test_no_iframe_uses_page_locator():
    """Without handler_config -> existing behaviour: top-level page.locator() + fill."""
    page = MockPage()
    handler = _make_handler(page)

    field_config = {"selector": "#field"}
    result = handler.execute(field_config, "123")

    assert result["success"] is True, result
    # Top-level locator called for the field selector
    assert ("locator", "#field") in page.locator_calls, page.locator_calls
    # frame_locator never called
    assert not [c for c in page.locator_calls if c[0] == "frame_locator"], page.locator_calls
    assert page.frame_locator_calls == [], page.frame_locator_calls
    # Fill value recorded on the plain top-level scope
    assert ("#field", "") in page.fills, page.fills
    assert ("#field", "123") in page.fills, page.fills
    # Evidence has no iframe key (unchanged shape)
    assert "iframe" not in result["evidence"], result["evidence"]


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
