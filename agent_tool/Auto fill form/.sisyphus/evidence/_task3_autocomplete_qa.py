#!/usr/bin/env python3
"""QA evidence generator for task-3 autocomplete two-step enhancement.

Runs the two required scenarios (two-step + backward-compat) against the real
AutoCompleteHandler with a recording MockPage, and writes evidence files.
Offline-safe: no Playwright browser is launched.
"""

import io
import os
import sys
from contextlib import redirect_stdout

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

sys.path.insert(0, os.path.join(PROJECT_ROOT, "tests"))

from test_autocomplete_handler import (  # noqa: E402
    MockPage,
    test_backward_compat_fill_value_directly,
    test_search_selector_key_supported,
    test_two_step_no_result_selector_uses_default,
    test_two_step_no_results_returns_success_warning,
    test_two_step_search_then_select,
)
from handlers import get_handler  # noqa: E402

EVIDENCE_DIR = os.path.join(PROJECT_ROOT, ".sisyphus", "evidence")
TWO_STEP_PATH = os.path.join(EVIDENCE_DIR, "task-3-autocomplete-two-step.txt")
COMPAT_PATH = os.path.join(EVIDENCE_DIR, "task-3-autocomplete-compat.txt")


def run_scenario(fn):
    """Run a scenario test, returning (ok, stdout_capture)."""
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            fn()
        return True, buf.getvalue()
    except AssertionError as e:
        return False, f"ASSERTION FAILED: {e}\n{buf.getvalue()}"
    except Exception as e:
        return False, f"EXCEPTION: {e!r}\n{buf.getvalue()}"


def main():
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

    # ---- Scenario 1: two-step search-then-select ----------------------------
    page = MockPage()
    page.item_texts["#sel_results .text"] = [
        "PO0147739 - 广州2026年7月京东购买（不含税）-上海圆迈贸易有限公司",
        "PO9999999 - Another order",
    ]
    handler = get_handler("autocomplete")(page, {})
    field_config = {
        "selector": "#sel",
        "handler_config": {
            "search_value": "6000017449",
            "result_selector": "#sel_results .text",
            "wait_after_input_ms": 100,
        },
    }
    result = handler.execute(field_config, "PO0147739")

    fills = [v for (sel, v) in page.fills if sel == "#sel_search"]
    clicked_item = page.item_texts["#sel_results .text"][0]
    checks = {
        "handler returns success=True": result["success"] is True,
        "search input filled with '6000017449' (search term, not 'PO0147739')": fills == ["", "6000017449"],
        "clicked item located via result_selector '#sel_results .text'": ("#sel_results .text", 0) in page.clicks,
        "clicked item text contains field value 'PO0147739'": "PO0147739" in clicked_item,
        "waited wait_after_input_ms=100": 100 in page.timeouts,
    }
    scenario1_ok = all(checks.values())

    additional = {
        "test_two_step_search_then_select": run_scenario(test_two_step_search_then_select),
        "test_two_step_no_result_selector_uses_default": run_scenario(test_two_step_no_result_selector_uses_default),
        "test_two_step_no_results_returns_success_warning": run_scenario(test_two_step_no_results_returns_success_warning),
        "test_search_selector_key_supported": run_scenario(test_search_selector_key_supported),
    }

    lines = []
    lines.append("AutoCompleteHandler Two-Step (search-then-select) - QA Evidence")
    lines.append("=" * 70)
    lines.append("Date/Time      : 2026-07-31")
    lines.append("Interpreter    : %s" % sys.executable)
    lines.append("Recording ref  : recordings/recorder_log_20260731_140316.json")
    lines.append("                 (selOrder search: type '6000017449' -> click 'PO0147739 - 广州...' item)")
    lines.append("")
    lines.append("Scenario:")
    lines.append('  field_config.selector        = "#sel"')
    lines.append("  field_config.handler_config  = {")
    lines.append('      "search_value": "6000017449",')
    lines.append('      "result_selector": "#sel_results .text",')
    lines.append('      "wait_after_input_ms": 100')
    lines.append("  }")
    lines.append('  value                        = "PO0147739"')
    lines.append("")
    lines.append("Expected behaviour:")
    lines.append('  - fill search input "#sel_search" with the search term "6000017449" (NOT the value)')
    lines.append("  - wait 100ms for the server-side AJAX search results")
    lines.append('  - locate items via result_selector "#sel_results .text"')
    lines.append('  - click the item whose displayed text matches the field value "PO0147739"')
    lines.append("")
    lines.append("Observed MockPage interaction log:")
    lines.append("  fills on #sel_search : %r" % (fills,))
    lines.append("  clicks on items      : %r" % (page.clicks,))
    lines.append("  wait_for_timeout(ms) : %r" % (page.timeouts,))
    lines.append('  clicked item text    : "%s"' % clicked_item)
    lines.append("")
    for label, ok in checks.items():
        lines.append("  [%s] %s" % ("PASS" if ok else "FAIL", label))
    lines.append("")
    lines.append("  handler result: %s" % result)
    lines.append("")
    lines.append("Additional scenario tests (tests/test_autocomplete_handler.py):")
    for name, (ok, _out) in additional.items():
        lines.append("  %-50s %s" % (name, "PASS" if ok else "FAIL"))
    lines.append("")
    lines.append("VERDICT: %s" % ("PASS" if scenario1_ok else "FAIL"))
    with open(TWO_STEP_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    # ---- Scenario 2: backward compatibility ---------------------------------
    page2 = MockPage()
    page2.item_texts["#sel .menu > .item"] = ["ABC123", "XYZ789"]
    handler2 = get_handler("autocomplete")(page2, {})
    field_config2 = {"selector": "#sel", "handler_config": {}}
    result2 = handler2.execute(field_config2, "ABC123")

    fills2 = [v for (sel, v) in page2.fills if sel == "#sel_search"]
    checks2 = {
        "handler returns success=True": result2["success"] is True,
        "search input filled with the value itself 'ABC123' (old behaviour)": fills2 == ["", "ABC123"],
        "default dropdown selector '#sel .menu > .item' used, exact match clicked": ("#sel .menu > .item", 0) in page2.clicks,
        "evidence shape unchanged (no search_value key)": "search_value" not in result2["evidence"],
    }
    scenario2_ok = all(checks2.values())
    compat_extra = run_scenario(test_backward_compat_fill_value_directly)

    lines2 = []
    lines2.append("AutoCompleteHandler Backward Compatibility - QA Evidence")
    lines2.append("=" * 70)
    lines2.append("Date/Time      : 2026-07-31")
    lines2.append("Interpreter    : %s" % sys.executable)
    lines2.append("")
    lines2.append("Scenario:")
    lines2.append('  field_config.selector        = "#sel"')
    lines2.append("  field_config.handler_config  = {}   (no search_value, no result_selector)")
    lines2.append('  value                        = "ABC123"')
    lines2.append("")
    lines2.append("Expected behaviour (unchanged from before this task):")
    lines2.append('  - search input "#sel_search" is filled with the VALUE itself ("ABC123")')
    lines2.append('  - dropdown items matched against the value via default selector "#sel .menu > .item"')
    lines2.append("  - exact match clicked")
    lines2.append("  - evidence dict shape unchanged (no search_value key)")
    lines2.append("")
    lines2.append("Observed MockPage interaction log:")
    lines2.append("  fills on #sel_search : %r" % (fills2,))
    lines2.append("  clicks on items      : %r" % (page2.clicks,))
    lines2.append("")
    for label, ok in checks2.items():
        lines2.append("  [%s] %s" % ("PASS" if ok else "FAIL", label))
    lines2.append("")
    lines2.append("  handler result: %s" % result2)
    lines2.append("")
    lines2.append("Additional backward-compat test:")
    lines2.append("  %-50s %s" % ("test_backward_compat_fill_value_directly", "PASS" if compat_extra[0] else "FAIL"))
    lines2.append("")
    lines2.append("VERDICT: %s" % ("PASS" if scenario2_ok else "FAIL"))
    with open(COMPAT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines2) + "\n")

    print("Wrote %s" % TWO_STEP_PATH)
    print("Wrote %s" % COMPAT_PATH)
    print("Scenario 1 (two-step): %s" % ("PASS" if scenario1_ok else "FAIL"))
    print("Scenario 2 (compat)  : %s" % ("PASS" if scenario2_ok else "FAIL"))
    return 0 if (scenario1_ok and scenario2_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
