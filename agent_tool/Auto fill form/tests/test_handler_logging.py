#!/usr/bin/env python3
"""
tests/test_handler_logging.py — caplog 离线测试: 验证 handler 详细日志真实存在。

Covers:
  1. autocomplete dropdown items DEBUG 摘要 (dropdown items=2 first5=[...])
  2. autocomplete 无下拉项 -> WARNING "NO dropdown items appeared"
  3. autocomplete 无匹配项 -> DEBUG "fallback to first"
  4. input fill DEBUG 日志 ([input] ... + selector)
  5. 引擎字段摘要 INFO: "Field 'Name' (type=input): start" / "Field 'Name': success - ..."
  6. 引擎字段失败 WARNING: "Field 'X': FAILED - ..."
  7. mask_value 脱敏: 裸邮箱不出现在日志, 脱敏形式 (jo***@gmail.com) 出现

All tests are OFFLINE-SAFE — a MockPage records interactions; no Playwright
browser is launched. Uses only stdlib pytest + caplog (no third-party deps).
Run with:  python -m pytest tests/test_handler_logging.py -v
"""

import os
import sys

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from handlers import get_handler
from workflow_engine import WorkflowEngine


class MockLocator:
    """Playwright-like locator that records interactions on a MockPage.

    `index` is set when returned from nth()/first(); text_content() then reads
    the per-item text from page.item_texts[selector].
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
        self.press_seq = []       # [(selector, text, delay)]
        self.timeouts = []        # wait_for_timeout(ms) calls
        self.wait_for_calls = []  # [(selector, kwargs)]
        self.locator_counts = {}  # selector -> count()
        self.item_texts = {}      # selector -> [item texts]
        self.hidden_inputs = []   # [sel, val] pairs passed to evaluate()

    def locator(self, selector):
        return MockLocator(self, selector)

    def frame_locator(self, selector):
        # Fields inside an iframe: delegate to the same MockLocator
        return MockLocator(self, selector)

    def wait_for_timeout(self, ms):
        self.timeouts.append(ms)

    def evaluate(self, script, *args):
        self.hidden_inputs.append(args[0] if args else None)
        return None

    # --- engine / navigation stubs (unused when login disabled + no nav) ---
    def goto(self, url, **kwargs):
        pass

    def wait_for_load_state(self, state, **kwargs):
        pass

    def wait_for_selector(self, selector, **kwargs):
        pass


# ---------------------------------------------------------------------------
# autocomplete handler logs
# ---------------------------------------------------------------------------

def _autocomplete_config(**hc_overrides):
    hc = {"wait_after_input_ms": 0, "delay_between_chars": 0}
    hc.update(hc_overrides)
    return {"selector": "#sel", "handler_config": hc}


def test_autocomplete_logs_dropdown_items(caplog):
    """Dropdown item summary (dropdown items=2) + exact-match click are logged."""
    page = MockPage()
    items_sel = "#sel .menu > .item"
    page.locator_counts[items_sel] = 2
    page.item_texts[items_sel] = ["PO0147739", "PO0147740"]
    handler = get_handler("autocomplete")(page, {})

    caplog.set_level("DEBUG", logger="handlers.autocomplete_handler")
    result = handler.execute(_autocomplete_config(), "PO0147739")

    assert result["success"] is True, result
    assert "dropdown items=2" in caplog.text, caplog.text
    assert "exact match" in caplog.text, caplog.text
    # The matched item text appears (masked, not raw)
    assert "PO0147739" not in caplog.text, caplog.text
    assert "PO***" in caplog.text, caplog.text


def test_autocomplete_no_items_warning(caplog):
    """No dropdown items appeared -> WARNING is logged."""
    page = MockPage()
    items_sel = "#sel .menu > .item"
    page.locator_counts[items_sel] = 0
    handler = get_handler("autocomplete")(page, {})

    caplog.set_level("DEBUG", logger="handlers.autocomplete_handler")
    result = handler.execute(_autocomplete_config(), "PO0147739")

    # Handler still succeeds (warning path, not hard failure)
    assert result["success"] is True, result
    assert result["evidence"]["warning"] == "No dropdown items appeared"
    assert "NO dropdown items appeared" in caplog.text, caplog.text
    assert any(
        rec.levelno == 30 for rec in caplog.records
        if "NO dropdown items appeared" in rec.getMessage()
    ), caplog.text


def test_autocomplete_fallback_first_logged(caplog):
    """No exact/partial match -> DEBUG 'fallback to first' is logged."""
    page = MockPage()
    items_sel = "#sel .menu > .item"
    page.locator_counts[items_sel] = 2
    page.item_texts[items_sel] = ["ZZZ", "YYY"]
    handler = get_handler("autocomplete")(page, {})

    caplog.set_level("DEBUG", logger="handlers.autocomplete_handler")
    result = handler.execute(_autocomplete_config(), "ABC")

    assert result["success"] is True, result
    assert "fallback to first" in caplog.text, caplog.text


# ---------------------------------------------------------------------------
# input handler logs
# ---------------------------------------------------------------------------

def test_input_logs_fill(caplog):
    """InputHandler logs [input] start + fill message including the selector."""
    page = MockPage()
    handler = get_handler("input")(page, {})

    caplog.set_level("DEBUG", logger="handlers.input_handler")
    result = handler.execute({"selector": "#name"}, "Alice")

    assert result["success"] is True, result
    assert "[input]" in caplog.text, caplog.text
    assert "#name" in caplog.text, caplog.text
    # Value appears masked, not raw
    assert "Alice" not in caplog.text, caplog.text
    assert "Al***" in caplog.text, caplog.text


# ---------------------------------------------------------------------------
# workflow engine field summary logs
# ---------------------------------------------------------------------------

def _base_config(**overrides):
    config = {
        "login": {"enabled": False},
        "navigation": [],
        "fields": {},
    }
    config.update(overrides)
    return config


def test_engine_field_summary_info(caplog):
    """Engine logs INFO start + success summary for a filled field."""
    page = MockPage()
    config = _base_config(
        fields={
            "Name": {"selector": "#name", "type": "input", "required": True},
        },
    )
    engine = WorkflowEngine(page, config)

    caplog.set_level("INFO", logger="workflow_engine")
    result = engine.execute(field_values={"Name": "Alice"})

    assert result["success"] == 1, result
    assert "Field 'Name' (type=input): start" in caplog.text, caplog.text
    assert "Field 'Name': success" in caplog.text, caplog.text
    # Success message is masked in the log (no raw value leak)
    assert "Alice" not in caplog.text, caplog.text


def test_engine_field_failure_warning(caplog):
    """Engine logs WARNING FAILED summary when a field cannot be filled."""
    page = MockPage()
    page.locator_counts["#x"] = 0  # element does not exist
    config = _base_config(
        fields={
            "X": {"selector": "#x", "type": "input", "required": True},
        },
    )
    engine = WorkflowEngine(page, config)

    caplog.set_level("DEBUG", logger="workflow_engine")
    result = engine.execute(field_values={"X": "v"})

    # Engine catches WorkflowFieldError internally and reports it in the dict
    assert result["failed"] == 1, result
    assert "error" in result, result
    assert "Field 'X': FAILED" in caplog.text, caplog.text
    assert any(
        rec.levelno == 30 for rec in caplog.records
        if "FAILED" in rec.getMessage()
    ), caplog.text


# ---------------------------------------------------------------------------
# mask_value: no sensitive leak into logs
# ---------------------------------------------------------------------------

def test_mask_no_sensitive_leak(caplog):
    """A raw email never appears in logs; the masked form always does."""
    page = MockPage()
    items_sel = "#sel .menu > .item"
    page.locator_counts[items_sel] = 1
    page.item_texts[items_sel] = ["john.doe@gmail.com"]
    handler = get_handler("autocomplete")(page, {})

    caplog.set_level("DEBUG", logger="handlers.autocomplete_handler")
    result = handler.execute(_autocomplete_config(), "john.doe@gmail.com")

    assert result["success"] is True, result
    # Masked form appears for the matched item
    assert "jo***@gmail.com" in caplog.text, caplog.text
    # Raw email must never leak into any log record
    assert "john.doe@gmail.com" not in caplog.text, caplog.text


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
