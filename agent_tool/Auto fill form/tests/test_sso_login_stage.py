#!/usr/bin/env python3
"""
tests/test_sso_login_stage.py — pytest tests for the `sso_login` stage of the
real GR-Acubuy workflow (workflows/gracubuy_gr_flow/workflow.json).

Covers:
  1. `sso_login` is stage zero with no fields / no post_fill.
  2. The full engine run executes the SSO navigation sequence in order:
     goto login page -> wait/click NCS Employee Login button -> wait for the
      homepage announcement marker #header_x_headerNavBar, THEN
     create_gr goto delivery_manage?Create (proving sso_login runs before
     create_gr).
  3. Already-logged-in tolerance: when the NCS button is missing (optional
     step), the engine skips it without failing.
  4. create_gr still opens delivery_manage?Create first.
  5. Top-level `login` block is pre-fill only (enabled=false, url set).

All tests are OFFLINE-SAFE: a MockPage records interactions, no browser is
launched and playwright.sync_api is never imported. The REAL workflow.json is
loaded (not an inline copy) and the REAL engine execution path is exercised.

Run with:  python -m pytest tests/test_sso_login_stage.py -v
"""

import json
import os
import sys

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from workflow_engine import WorkflowEngine

# ---------------------------------------------------------------------------
# Real workflow config (single source of truth — not an inline copy)
# ---------------------------------------------------------------------------

REAL_CONFIG_PATH = os.path.join(
    PROJECT_ROOT, "workflows", "gracubuy_gr_flow", "workflow.json"
)
with open(REAL_CONFIG_PATH, encoding="utf-8") as _f:
    REAL_CONFIG = json.load(_f)

LOGIN_URL = "https://singtel.ivalua.app/page.aspx/en/usr/login"
NCS_BUTTON = "#body_x_button_login_20240212134848558"
HEADER_NAV = "#header_x_headerNavBar"
CREATE_GR_URL = "https://singtel.ivalua.app/page.aspx/en/ord/delivery_manage?Create"


class MockLocator:
    """Playwright-like locator that records interactions on a MockPage.

    Structurally identical to tests/test_stages_engine.py::MockLocator, with
    one ADDITIVE method — press_sequentially — required because the real
    autocomplete handler types per-keystroke into iValua search inputs.
    """

    def __init__(self, page, selector):
        self.page = page
        self.selector = selector

    def count(self):
        return self.page.locator_counts.get(self.selector, 1)

    def wait_for(self, **kwargs):
        self.page.calls.append(("wait_for", self.selector, kwargs))
        return None

    def fill(self, value):
        self.page.calls.append(("fill", self.selector, str(value)))
        return None

    def click(self):
        # Failure injection: pretend the element does not exist (already-logged-in).
        if self.selector in self.page.fail_selectors:
            raise TimeoutError(f"Selector '{self.selector}' not found (mock)")
        self.page.calls.append(("click", self.selector))
        return None

    def press_sequentially(self, text, **kwargs):
        self.page.calls.append(("press_sequentially", self.selector, str(text)))
        return None

    @property
    def first(self):
        return self

    def nth(self, index):
        return self

    def text_content(self):
        return ""

    def all_inner_texts(self):
        return []


class MockPage:
    """Records page interactions as ordered ``(kind, *rest)`` tuples in .calls.

    Structurally identical to tests/test_stages_engine.py::MockPage, plus one
    ADDITIVE attribute — fail_selectors — a set of selectors that raise
    TimeoutError from wait_for_selector / locator().first.click(), simulating
    elements that are absent from the DOM.
    """

    def __init__(self):
        self.calls = []          # ordered trace of every page interaction
        self.locator_counts = {}  # selector -> count() override
        self.fail_selectors = set()  # selectors treated as "not present"

    def locator(self, selector):
        return MockLocator(self, selector)

    def goto(self, url, **kwargs):
        self.calls.append(("goto", url, kwargs))

    def wait_for_load_state(self, state, **kwargs):
        self.calls.append(("wait_for_load_state", state))

    def wait_for_selector(self, selector, **kwargs):
        # Failure injection: pretend the element never appears (already-logged-in).
        if selector in self.fail_selectors:
            raise TimeoutError(f"Selector '{selector}' not found (mock)")
        self.calls.append(("wait_for_selector", selector, kwargs))

    def wait_for_timeout(self, timeout):
        self.calls.append(("wait_for_timeout", timeout))

    def evaluate(self, script, *args):
        self.calls.append(("evaluate", script))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fills(page, selector=None):
    """Non-empty fill() values, optionally filtered by selector."""
    return [
        rest[1]
        for kind, *rest in page.calls
        if kind == "fill"
        and (selector is None or rest[0] == selector)
        and rest[1] != ""
    ]


def fill_selectors(page):
    """Selector of every fill() call (including the clear) in order."""
    return [rest[0] for kind, *rest in page.calls if kind == "fill"]


def clicks(page):
    """Selectors clicked in order."""
    return [rest[0] for kind, *rest in page.calls if kind == "click"]


def gotos(page):
    """URLs navigated to in order."""
    return [rest[0] for kind, *rest in page.calls if kind == "goto"]


def waited_selectors(page):
    """Selectors passed to wait_for_selector in order."""
    return [rest[0] for kind, *rest in page.calls if kind == "wait_for_selector"]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_sso_login_is_stage_zero():
    """sso_login is the first stage, with no fields and no post_fill."""
    assert REAL_CONFIG["stages"][0]["name"] == "sso_login"
    assert REAL_CONFIG["stages"][0]["fields"] == []
    assert REAL_CONFIG["stages"][0]["post_fill"] == {}


def test_sso_login_navigation_sequence():
    """The full engine run executes SSO steps in order, then create_gr goto."""
    page = MockPage()
    engine = WorkflowEngine(page, REAL_CONFIG)
    result = engine.execute(field_values={})

    assert "error" not in result, result
    assert result["success"] >= 1, result

    # sso_login goto comes first, create_gr goto second (stage order proven)
    urls = gotos(page)
    assert urls[0] == LOGIN_URL, page.calls
    assert urls[1] == CREATE_GR_URL, page.calls

    # login goto must use wait_until="load" with timeout=60000 (from config)
    login_goto = [
        rest for kind, *rest in page.calls
        if kind == "goto" and rest[0] == LOGIN_URL
    ]
    assert login_goto, page.calls
    assert login_goto[0][1] == {"wait_until": "load", "timeout": 60000}, page.calls

    # wait sequence: NCS button -> homepage announcement marker -> txtCode
    waits = waited_selectors(page)
    assert waits[0] == NCS_BUTTON, page.calls
    assert waits[1] == HEADER_NAV, page.calls
    assert waits[2] == "#body_x_tabc_prxDelivery_prxprxDelivery_x_txtCode", page.calls

    # click sequence starts with the NCS button only
    assert clicks(page)[0] == NCS_BUTTON, page.calls


def test_sso_login_tolerates_already_logged_in():
    """When the NCS button is absent, the optional step is skipped."""
    page = MockPage()
    page.fail_selectors = {NCS_BUTTON}  # already logged in
    engine = WorkflowEngine(page, REAL_CONFIG)

    # The whole engine run must NOT raise despite the missing optional element
    result = engine.execute(field_values={})

    assert "error" not in result, result
    assert result["success"] >= 1, result

    # SSO completed: the non-optional homepage-marker wait still ran
    assert HEADER_NAV in waited_selectors(page), page.calls
    # The NCS button was never successfully waited on or clicked
    assert NCS_BUTTON not in waited_selectors(page), page.calls
    assert NCS_BUTTON not in clicks(page), page.calls
    # create_gr still proceeded to its own page
    assert CREATE_GR_URL in gotos(page), page.calls


def test_create_gr_goto_preserved():
    """create_gr still opens delivery_manage?Create as its first action."""
    create_gr = REAL_CONFIG["stages"][1]
    assert create_gr["name"] == "create_gr"
    assert create_gr["navigation"][0]["action"] == "goto"
    assert "delivery_manage?Create" in create_gr["navigation"][0]["url"]


def test_login_block_prefill_only():
    """Top-level login is pre-fill config only: disabled but with URL set."""
    assert REAL_CONFIG["login"]["enabled"] is False
    assert REAL_CONFIG["login"]["url"] == LOGIN_URL


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
