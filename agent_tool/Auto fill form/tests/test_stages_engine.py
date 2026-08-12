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

import logging
import os
import sys

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from handlers.base_handler import BaseHandler
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


# ---------------------------------------------------------------------------
# Retry + evidence.warning tests (regression for stale last_error after break)
# ---------------------------------------------------------------------------

class FlakyHandler(BaseHandler):
    """Fails on the first execute() call, succeeds on the second.

    Injected via engine._get_handler to exercise the retry path without a
    browser. Mirrors the production bug: attempt 0 fails (last_error set),
    attempt 1 succeeds, `break` must clear last_error so the post-loop
    ``if last_error and not last_error.get("success")`` guard does not
    misreport the field as FAILED.
    """

    def __init__(self, page, workflow_config):
        super().__init__(page, workflow_config)
        self.calls = 0

    def execute(self, field_config, value):
        self.calls += 1
        if self.calls == 1:
            return {"success": False, "message": "Element not found", "evidence": {}}
        return {
            "success": True,
            "message": f"Filled '{value}' into '{field_config.get('selector')}'",
            "evidence": {"selector": field_config.get("selector"), "value": value},
        }


class AlwaysFailHandler(BaseHandler):
    """Fails on every execute() call (all retries exhausted)."""

    def execute(self, field_config, value):
        return {"success": False, "message": "Element not found", "evidence": {}}


class WarningHandler(BaseHandler):
    """Succeeds but returns evidence.warning (e.g. autocomplete fallback)."""

    def execute(self, field_config, value):
        return {
            "success": True,
            "message": "Filled via fallback",
            "evidence": {
                "selector": field_config.get("selector"),
                "value": value,
                "warning": "No dropdown items appeared",
            },
        }


def _engine_with_handler(handler, page, config):
    """Build an engine whose _get_handler returns the given handler instance."""
    engine = WorkflowEngine(page, config)
    engine._get_handler = lambda field_type: handler
    return engine


def test_fail_then_succeed_not_misreported(monkeypatch):
    """Bug 1: a field that fails on attempt 0 then succeeds on attempt 1 must
    be reported as SUCCESS — the stale last_error must not trip the post-loop
    FAILED guard and raise WorkflowFieldError."""
    monkeypatch.setattr("workflow_engine.time.sleep", lambda s: None)
    page = MockPage()
    config = _base_config(
        fields={
            "Code": {
                "selector": "#code",
                "type": "input",
                "required": True,
                "post_fill": {"action": "click_button", "click_selector": "#submit"},
            },
        },
    )
    engine = _engine_with_handler(FlakyHandler(page, config), page, config)
    field_ends = []
    engine.register_callback("on_field_end", lambda name, result: field_ends.append(name))

    result = engine.execute(field_values={"Code": "A1"})

    # Not a failure: success=True and the engine did not raise/record FAILED
    assert result["success"] == 1, result
    assert result["failed"] == 0, result
    assert result["results"]["Code"]["success"] is True, result
    # on_field_end fired exactly once (only the successful attempt)
    assert field_ends == ["Code"], field_ends
    # post_fill still runs after the retried-but-successful field
    assert clicks(page) == ["#submit"], page.calls


def test_all_retries_failed_marks_field_failed(monkeypatch):
    """A field that fails on every attempt must still be reported as FAILED
    (regression guard: ensure the fix does not swallow real failures)."""
    monkeypatch.setattr("workflow_engine.time.sleep", lambda s: None)
    page = MockPage()
    config = _base_config(
        fields={
            "Code": {"selector": "#code", "type": "input", "required": True},
        },
    )
    engine = _engine_with_handler(AlwaysFailHandler(page, config), page, config)

    result = engine.execute(field_values={"Code": "A1"})

    # execute() swallows WorkflowFieldError into the result dict
    assert result["failed"] == 1, result
    assert result["success"] == 0, result
    assert "failed after 2 retries" in result.get("error", ""), result


def test_evidence_warning_is_logged(caplog):
    """Bug 2: a successful result carrying evidence.warning (autocomplete
    fallback / no dropdown items) must surface as a WARNING log line."""
    page = MockPage()
    config = _base_config(
        fields={
            "Code": {"selector": "#code", "type": "input", "required": True},
        },
    )
    engine = _engine_with_handler(WarningHandler(page, config), page, config)

    with caplog.at_level(logging.WARNING, logger="workflow_engine"):
        result = engine.execute(field_values={"Code": "A1"})

    # Warning does NOT change the success semantics
    assert result["success"] == 1, result
    assert result["failed"] == 0, result
    # The engine-level logger must surface the evidence warning
    warnings = [
        r.getMessage()
        for r in caplog.records
        if r.name == "workflow_engine" and r.levelno == logging.WARNING
    ]
    assert any("Code" in w and "No dropdown items appeared" in w for w in warnings), warnings


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
