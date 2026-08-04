#!/usr/bin/env python3
"""
tests/test_stages_engine.py — pytest tests for WorkflowEngine multi-stage execution.

Covers:
  1. Config without `stages` -> identical single-round behaviour (regression).
  2. Config with 2 stages -> stages execute sequentially, each with its own
     navigation / field subset / step events.
  3. Stage-level post_fill (click_button) runs after that stage's fields and
     before the next stage's navigation.
  4. The same field_values dict drives every stage.
  5. A stage referencing an unknown field name -> WorkflowFieldError.

All tests are OFFLINE-SAFE: a MockPage records interactions, no browser is launched.
Run with:  python -m pytest tests/test_stages_engine.py -v
"""

import os
import sys

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from workflow_engine import WorkflowEngine, WorkflowFieldError


class MockLocator:
    """Playwright-like locator that records interactions on a MockPage."""

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
        self.page.calls.append(("click", self.selector))
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
    """Records page interactions as ordered ``(kind, *rest)`` tuples in .calls."""

    def __init__(self):
        self.calls = []          # ordered trace of every page interaction
        self.locator_counts = {}  # selector -> count() override

    def locator(self, selector):
        return MockLocator(self, selector)

    def goto(self, url, **kwargs):
        self.calls.append(("goto", url, kwargs))

    def wait_for_load_state(self, state, **kwargs):
        self.calls.append(("wait_for_load_state", state))

    def wait_for_selector(self, selector, **kwargs):
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


def _base_config(**overrides):
    config = {
        "login": {"enabled": False},
        "navigation": [],
        "fields": {},
    }
    config.update(overrides)
    return config


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_no_stages_uses_single_round():
    """Config without `stages` -> classic navigation + fields round (regression)."""
    page = MockPage()
    config = _base_config(
        navigation=[{"action": "goto", "url": "https://example.com/form"}],
        fields={
            "Name": {"selector": "#name", "type": "input", "required": True},
        },
    )
    engine = WorkflowEngine(page, config)
    events = []
    engine.register_callback("on_step_start", lambda n: events.append(f"start:{n}"))
    engine.register_callback("on_step_end", lambda n: events.append(f"end:{n}"))

    result = engine.execute(field_values={"Name": "Alice"})

    assert result["success"] == 1, result
    assert fills(page) == ["Alice"], page.calls
    assert gotos(page) == ["https://example.com/form"], page.calls
    # Classic single-round steps still fire
    assert "start:navigation" in events and "end:navigation" in events
    assert "start:fields" in events and "end:fields" in events
    # The stages path must not be used
    assert not any("stage" in e for e in events), events


def test_multi_stage_executes_in_order():
    """Two stages run sequentially, each with its own navigation + field subset."""
    page = MockPage()
    config = _base_config(
        fields={
            "A": {"selector": "#a", "type": "input", "required": True},
            "B": {"selector": "#b", "type": "input", "required": True},
            "C": {"selector": "#c", "type": "input", "required": True},
        },
        stages=[
            {
                "name": "Step One",
                "navigation": [{"action": "goto", "url": "https://one"}],
                "fields": ["A", "B"],
            },
            {
                "name": "Step Two",
                "navigation": [{"action": "goto", "url": "https://two"}],
                "fields": ["C"],
            },
        ],
    )
    engine = WorkflowEngine(page, config)
    events = []
    engine.register_callback("on_step_start", lambda n: events.append(f"start:{n}"))
    engine.register_callback("on_step_end", lambda n: events.append(f"end:{n}"))

    result = engine.execute(field_values={"A": "1", "B": "2", "C": "3"})

    assert result["success"] == 3, result
    # Each stage fills only its own subset, in stage order
    assert fills(page) == ["1", "2", "3"], page.calls
    assert fill_selectors(page) == ["#a", "#a", "#b", "#b", "#c", "#c"], page.calls
    # Per-stage navigation runs in order
    assert gotos(page) == ["https://one", "https://two"], page.calls
    # Stage events bracket each stage and occur in order
    assert events.index("start:stages") < events.index("start:stage:Step One")
    assert events.index("end:stage:Step One") < events.index("start:stage:Step Two")
    assert events.index("end:stage:Step Two") < events.index("end:stages")


def test_stage_post_fill_click():
    """Stage 1 post_fill click runs after its fields; stage 2 navigation follows."""
    page = MockPage()
    config = _base_config(
        fields={
            "A": {"selector": "#a", "type": "input", "required": True},
        },
        stages=[
            {
                "name": "Fill",
                "fields": ["A"],
                "post_fill": {"action": "click_button", "click_selector": "#submit"},
            },
            {
                "name": "Next",
                "fields": [],
                "navigation": [{"action": "wait_selector", "selector": "#next-page"}],
            },
        ],
    )
    engine = WorkflowEngine(page, config)
    result = engine.execute(field_values={"A": "hello"})

    assert result["success"] == 1, result
    # Stage-1 post_fill clicked the submit button
    assert clicks(page) == ["#submit"], page.calls
    # Stage-2 navigation waited for the next-page selector
    assert "#next-page" in waited_selectors(page), page.calls
    # Order: stage-1 field fill -> post_fill click -> stage-2 navigation wait
    kinds = [kind for kind, *_ in page.calls]
    assert kinds.index("fill") < kinds.index("click") < kinds.index("wait_for_selector")


def test_field_values_shared_across_stages():
    """The same field_values dict drives every stage."""
    page = MockPage()
    config = _base_config(
        fields={"X": {"selector": "#x", "type": "input", "required": True}},
        stages=[
            {"name": "S1", "fields": ["X"]},
            {"name": "S2", "fields": ["X"]},
        ],
    )
    engine = WorkflowEngine(page, config)
    result = engine.execute(field_values={"X": "shared"})

    # self.results is keyed per field name, so a field reused across stages
    # is reported once (overwritten) — the proof of sharing is in the fills
    assert result["success"] == 1, result
    # The shared field_values dict drove BOTH stages
    assert fills(page) == ["shared", "shared"], page.calls


def test_stage_missing_field_raises():
    """A stage referencing an unknown field name raises WorkflowFieldError."""
    page = MockPage()
    config = _base_config(
        fields={"X": {"selector": "#x", "type": "input", "required": True}},
        stages=[{"name": "S1", "fields": ["X", "Ghost"]}],
    )
    engine = WorkflowEngine(page, config)

    # The stage executor raises directly with a clear message
    with pytest.raises(WorkflowFieldError, match="Ghost"):
        engine._execute_stages(config["stages"], {"X": "1"})

    # The public execute() path surfaces the same error in the result dict
    result = engine.execute(field_values={"X": "1"})
    assert "Ghost" in result.get("error", ""), result


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
