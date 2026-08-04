#!/usr/bin/env python3
"""
tests/test_file_upload_handler.py — Tests for FileUploadHandler, covering the
iValua HTML5 uploader pattern (set files directly on hidden input -> wait for
upload) plus the native mode.

Covers:
  1. html5_uploader with upload_button_selector + file_input_selector +
     wait_after_upload_ms -> upload button is NOT clicked (clicking it opens a
     native file dialog), hidden file input populated directly, and
     page.wait_for_timeout(wait_after_upload_ms) called.
  2. wait_after_upload_ms is the HIGHEST priority wait: it wins even when a
     wait_for_upload_selector is also configured.
  3. Fallback path: wait_for_upload_selector + wait_upload_timeout_ms (no
     wait_after_upload_ms) -> wait_for_selector(state="hidden") is used.
  4. Default path: no wait config -> wait_for_timeout(2000) (existing behaviour).
  5. Hidden-input fallback: when the configured file input has count()==0, the
     generic 'input[type="file"]' locator is used.
  6. Native mode unchanged: no button click, no wait_for_timeout, files set on
     the field selector directly.
  7. validate() does NOT require upload_button_selector for html5_uploader
     mode (the button is optional; selector/file_input_selector is enough).

All tests are OFFLINE-SAFE — a MockPage records interactions; no Playwright
browser is launched. Runnable directly or via pytest.
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

    def __init__(self, page, selector, index=None):
        self.page = page
        self.selector = selector
        self.index = index

    def count(self):
        return self.page.locator_counts.get(self.selector, 1)

    def wait_for(self, **kwargs):
        self.page.wait_for_calls.append((self.selector, kwargs))
        return None

    def click(self):
        self.page.clicks.append((self.selector, self.index))
        return None

    def set_input_files(self, value):
        self.page.file_inputs.append((self.selector, value))
        return None

    def nth(self, index):
        return MockLocator(self.page, self.selector, index)

    @property
    def first(self):
        return MockLocator(self.page, self.selector, 0)


class MockPage:
    """Records locator interactions so tests can assert what was clicked/uploaded."""

    def __init__(self):
        self.clicks = []          # [(selector, index_or_None)]
        self.file_inputs = []     # [(selector, value)] from set_input_files()
        self.timeouts = []        # wait_for_timeout(ms) calls
        self.wait_for_calls = []  # [(selector, kwargs)] from wait_for()
        self.selector_waits = []  # [(selector, kwargs)] from wait_for_selector()
        self.locator_counts = {}  # selector -> count()

    def locator(self, selector):
        return MockLocator(self, selector)

    def wait_for_timeout(self, ms):
        self.timeouts.append(ms)

    def wait_for_selector(self, selector, **kwargs):
        self.selector_waits.append((selector, kwargs))
        return None


def _make_handler(page):
    return get_handler("file_upload")(page, {})


def _fake_file(tmp_path, name="order.pdf"):
    """Create a real temp file (handler validates existence before dispatch)."""
    p = tmp_path / name
    p.write_bytes(b"%PDF-1.4 test")
    return str(p)


# ---------------------------------------------------------------------------
# html5_uploader mode
# ---------------------------------------------------------------------------

IVALUA_CONFIG = {
    "mode": "html5_uploader",
    "upload_button_selector": "#body_x_tabc_prxDelivery_prxprxDelivery_x_file_delivery_20240807224049492_x_UploadButtonControl",
    "file_input_selector": "#fileselect_body_x_tabc_prxDelivery_prxprxDelivery_x_file_delivery_20240807224049492_x",
    "wait_after_upload_ms": 4000,
}


def test_html5_uploader_sets_input_waits_without_click(tmp_path):
    """Full iValua config: NO button click (avoids native file dialog), files set
    directly on the hidden input, wait 4000ms."""
    page = MockPage()
    handler = _make_handler(page)
    fpath = _fake_file(tmp_path)

    field_config = {"selector": "#delivery", "handler_config": dict(IVALUA_CONFIG)}
    result = handler.execute(field_config, fpath)

    assert result["success"] is True, result

    # 1. Upload button must NOT be clicked (clicking opens native file dialog)
    assert page.clicks == [], page.clicks

    # 2. Hidden file input received the file directly
    assert ("#fileselect_body_x_tabc_prxDelivery_prxprxDelivery_x_file_delivery_20240807224049492_x", fpath) in page.file_inputs, page.file_inputs

    # 3. Fixed wait used after set_input_files
    assert 4000 in page.timeouts, page.timeouts

    # No settle wait from a button click (500ms) — the click block is removed
    assert 500 not in page.timeouts, page.timeouts
    # wait_for_timeout(4000) must come after set_input_files, not before
    assert len([t for t in page.timeouts if t == 4000]) == 1

    # No selector-based wait used when wait_after_upload_ms is configured
    assert page.selector_waits == [], page.selector_waits


def test_html5_uploader_does_not_click_button(tmp_path):
    """Config with upload_button_selector + file_input_selector: NO click on the
    upload button; set_input_files WAS called on the file input."""
    page = MockPage()
    handler = _make_handler(page)
    fpath = _fake_file(tmp_path)

    field_config = {
        "selector": "#delivery",
        "handler_config": {
            "mode": "html5_uploader",
            "upload_button_selector": "#btn_upload",
            "file_input_selector": "#fileselect",
            "wait_after_upload_ms": 2500,
        },
    }
    result = handler.execute(field_config, fpath)

    assert result["success"] is True, result
    # The upload button selector is configured but must NOT be clicked
    assert page.clicks == [], page.clicks
    assert ("#btn_upload", None) not in page.clicks
    # Files were set directly on the hidden file input
    assert ("#fileselect", fpath) in page.file_inputs, page.file_inputs
    # Wait logic still runs
    assert 2500 in page.timeouts, page.timeouts


def test_wait_after_upload_ms_highest_priority(tmp_path):
    """wait_after_upload_ms wins even when wait_for_upload_selector is present."""
    page = MockPage()
    handler = _make_handler(page)
    fpath = _fake_file(tmp_path)

    field_config = {
        "selector": "#delivery",
        "handler_config": {
            "mode": "html5_uploader",
            "upload_button_selector": "#btn",
            "file_input_selector": "#fileselect",
            "wait_after_upload_ms": 4000,
            "wait_for_upload_selector": "#progress",
            "wait_upload_timeout_ms": 15000,
        },
    }
    result = handler.execute(field_config, fpath)

    assert result["success"] is True, result
    assert ("#fileselect", fpath) in page.file_inputs, page.file_inputs
    assert 4000 in page.timeouts, page.timeouts
    # Upload button is configured but must not be clicked
    assert page.clicks == [], page.clicks
    # The selector wait must NOT have been used
    assert page.selector_waits == [], page.selector_waits


def test_html5_fallback_wait_for_selector(tmp_path):
    """Without wait_after_upload_ms, wait_for_selector(state='hidden') is used."""
    page = MockPage()
    handler = _make_handler(page)
    fpath = _fake_file(tmp_path)

    field_config = {
        "selector": "#delivery",
        "handler_config": {
            "mode": "html5_uploader",
            "upload_button_selector": "#btn",
            "file_input_selector": "#fileselect",
            "wait_for_upload_selector": "#progress",
            "wait_upload_timeout_ms": 15000,
        },
    }
    result = handler.execute(field_config, fpath)

    assert result["success"] is True, result
    assert ("#progress", {"state": "hidden", "timeout": 15000}) in page.selector_waits, page.selector_waits
    # No fixed 2000ms wait in this branch
    assert 2000 not in page.timeouts, page.timeouts
    # Upload button is configured but must not be clicked
    assert page.clicks == [], page.clicks


def test_html5_default_wait_2000ms(tmp_path):
    """No wait config at all -> existing default wait_for_timeout(2000)."""
    page = MockPage()
    handler = _make_handler(page)
    fpath = _fake_file(tmp_path)

    field_config = {
        "selector": "#delivery",
        "handler_config": {
            "mode": "html5_uploader",
            "upload_button_selector": "#btn",
            "file_input_selector": "#fileselect",
        },
    }
    result = handler.execute(field_config, fpath)

    assert result["success"] is True, result
    assert 2000 in page.timeouts, page.timeouts
    assert page.selector_waits == [], page.selector_waits
    # Upload button is configured but must not be clicked
    assert page.clicks == [], page.clicks


def test_html5_hidden_input_fallback(tmp_path):
    """When the configured file input has count()==0, generic file input is used."""
    page = MockPage()
    page.locator_counts["#fileselect"] = 0
    handler = _make_handler(page)
    fpath = _fake_file(tmp_path)

    field_config = {
        "selector": "#delivery",
        "handler_config": {
            "mode": "html5_uploader",
            "upload_button_selector": "#btn",
            "file_input_selector": "#fileselect",
            "wait_after_upload_ms": 3000,
        },
    }
    result = handler.execute(field_config, fpath)

    assert result["success"] is True, result
    assert any(sel == 'input[type="file"]' for (sel, _v) in page.file_inputs), page.file_inputs
    assert ("#fileselect", fpath) not in page.file_inputs
    assert 3000 in page.timeouts, page.timeouts
    # Upload button is configured but must not be clicked
    assert page.clicks == [], page.clicks


# ---------------------------------------------------------------------------
# Native mode (must remain unchanged)
# ---------------------------------------------------------------------------

def test_native_mode_unchanged(tmp_path):
    """Native mode: no button click, no timeout waits, files set on selector."""
    page = MockPage()
    handler = _make_handler(page)
    fpath = _fake_file(tmp_path)

    field_config = {"selector": "#file_input", "type": "file_upload"}
    result = handler.execute(field_config, fpath)

    assert result["success"] is True, result
    assert ("#file_input", fpath) in page.file_inputs, page.file_inputs
    # wait_for(state='visible') called on the field selector
    assert ("#file_input", {"state": "visible", "timeout": 5000}) in page.wait_for_calls, page.wait_for_calls
    # NO button click, NO wait_for_timeout in native mode
    assert page.clicks == [], page.clicks
    assert page.timeouts == [], page.timeouts


def test_native_mode_unchanged_with_handler_config(tmp_path):
    """Even with html5-style handler_config keys, mode=native ignores them."""
    page = MockPage()
    handler = _make_handler(page)
    fpath = _fake_file(tmp_path)

    field_config = {
        "selector": "#file_input",
        "type": "file_upload",
        "handler_config": {
            "mode": "native",
            "upload_button_selector": "#btn",
            "file_input_selector": "#fileselect",
            "wait_after_upload_ms": 4000,
        },
    }
    result = handler.execute(field_config, fpath)

    assert result["success"] is True, result
    assert ("#file_input", fpath) in page.file_inputs, page.file_inputs
    assert page.clicks == [], page.clicks
    assert page.timeouts == [], page.timeouts
    # The html5-specific selectors were NOT used
    assert ("#btn", None) not in page.clicks
    assert ("#fileselect", fpath) not in page.file_inputs


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_validate_html5_no_upload_button_required():
    """validate() does NOT require upload_button_selector for html5_uploader mode.
    The button is optional — files are set directly on the hidden input."""
    page = MockPage()
    handler = _make_handler(page)

    # html5_uploader WITHOUT upload_button_selector is now VALID (selector fallback)
    errors = handler.validate({"selector": "#s", "handler_config": {"mode": "html5_uploader"}})
    assert errors == [], errors

    # html5_uploader with file_input_selector is valid too
    errors = handler.validate({
        "selector": "#s",
        "handler_config": {"mode": "html5_uploader", "file_input_selector": "#fileselect"},
    })
    assert errors == [], errors

    # html5_uploader with the (now optional) upload_button_selector stays valid
    errors = handler.validate({
        "selector": "#s",
        "handler_config": {"mode": "html5_uploader", "upload_button_selector": "#btn"},
    })
    assert errors == [], errors

    # Native mode needs no upload button
    errors = handler.validate({"selector": "#s", "handler_config": {"mode": "native"}})
    assert errors == [], errors

    # Base validate() still requires a selector: html5_uploader with neither
    # selector nor file_input_selector errors
    errors = handler.validate({"handler_config": {"mode": "html5_uploader"}})
    assert any("selector" in e for e in errors), errors


# ---------------------------------------------------------------------------
# Runner (for direct execution without pytest)
# ---------------------------------------------------------------------------

def _run_all():
    import pathlib
    import tempfile
    tests = [
        fn for name, fn in sorted(globals().items())
        if name.startswith("test_") and callable(fn)
    ]
    passed = failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        for fn in tests:
            try:
                fn(tmp_path) if "tmp_path" in fn.__code__.co_varnames else fn()
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
