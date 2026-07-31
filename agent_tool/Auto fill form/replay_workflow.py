# -*- coding: utf-8 -*-
"""Replay a workflow.json using Playwright.

Connects to a persistent Chrome profile (so cookies/session persist).
Reads workflow.json steps and dispatches each via Playwright.

CLI:
    python replay_workflow.py <workflow.json> [chrome_profile_dir]

Default profile dir: %USERPROFILE%/AcubuyChromeProfile
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

from playwright.async_api import async_playwright

# Use the logging infrastructure from Plan B
try:
    from logging_setup import setup_logging
    _HAS_LOGGING = True
except ImportError:
    _HAS_LOGGING = False


DEFAULT_PROFILE_DIR = os.path.expandvars(r"%USERPROFILE%\AcubuyChromeProfile")
DEFAULT_OUTPUT_DIR = os.path.expandvars(r"%USERPROFILE%\AcubuyReplays")


def _setup_logger():
    """Initialize logger. Returns root logger."""
    if _HAS_LOGGING:
        logger, _ = setup_logging(log_dir_path=os.path.join(DEFAULT_OUTPUT_DIR, "logs"))
        return logger
    import logging
    logger = logging.getLogger("replay_workflow")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    return logger


_PLACEHOLDER_RE = re.compile(r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}")


def _substitute_placeholders(value, vars_dict, step_num=None, logger=None):
    """Replace {{key}} in value with vars_dict[key]. Return (new_value, missing_keys)."""
    if not isinstance(value, str):
        return value, []
    missing = []

    def replace(match):
        key = match.group(1)
        if key in vars_dict:
            return vars_dict[key]
        missing.append(key)
        return match.group(0)  # leave as {{key}} if no value

    new_value = _PLACEHOLDER_RE.sub(replace, value)
    if missing and logger:
        logger.warning(
            f"Step {step_num or '?'}: missing vars {missing} (placeholder left as-is)"
        )
    return new_value, missing


def _parse_vars_args():
    """Parse --vars key=value and --vars-file path.json into a dict."""
    parser = argparse.ArgumentParser(description="Replay a workflow.json with Playwright")
    parser.add_argument("workflow_path", help="Path to workflow.json")
    parser.add_argument(
        "profile_dir", nargs="?", default=DEFAULT_PROFILE_DIR,
        help=f"Chrome profile dir (default: {DEFAULT_PROFILE_DIR})",
    )
    parser.add_argument(
        "--vars", action="append", default=[],
        help="Variable substitution: --vars key=value (repeatable)",
    )
    parser.add_argument(
        "--vars-file", default=None,
        help="Path to JSON file with variables",
    )
    return parser.parse_args()


def _build_vars_dict(args) -> dict:
    """Build vars dict from --vars (list of key=value) and --vars-file (JSON)."""
    vars_dict = {}
    for kv in args.vars:
        if "=" not in kv:
            raise ValueError(f"--vars must be key=value, got: {kv}")
        k, v = kv.split("=", 1)
        vars_dict[k.strip()] = v
    if args.vars_file:
        with open(args.vars_file, "r", encoding="utf-8") as f:
            file_vars = json.load(f)
        vars_dict.update(file_vars)
    return vars_dict


async def _launch_chrome(profile_dir: str):
    """Launch Chrome with persistent profile."""
    os.makedirs(profile_dir, exist_ok=True)
    pw = await async_playwright().start()
    context = await pw.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )
    return pw, context


async def replay(workflow_path: str, profile_dir: str, vars_dict: dict, logger) -> int:
    """Replay a workflow.json. Returns 0 on success, non-zero on error."""
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    steps = workflow.get("steps", [])
    logger.info(f"Replaying workflow: {workflow.get('name', '?')} ({len(steps)} steps)")
    logger.info(f"Source recording: {workflow.get('source_recording', '?')}")
    logger.info(f"Recorded at: {workflow.get('recorded_at', '?')}")
    logger.info(f"Password events filtered: {workflow.get('password_events_filtered', 0)}")
    logger.info(f"Vars provided: {len(vars_dict)}")
    for k, v in vars_dict.items():
        logger.debug(f"  {k}={v!r}")
    if workflow.get("parameterized"):
        logger.info("Workflow is parameterized (uses {{var}} placeholders)")

    if not steps:
        logger.error("No steps in workflow")
        return 1

    pw, context = await _launch_chrome(profile_dir)
    try:
        # Use first existing page or create one
        page = context.pages[0] if context.pages else await context.new_page()
        skipped = 0

        for i, step in enumerate(steps, 1):
            action = step.get("action")

            # Substitute placeholders in all string fields
            step_for_log = {k: v for k, v in step.items()}
            for k in ("value", "url", "selector", "files"):
                if isinstance(step.get(k), str):
                    new_val, missing = _substitute_placeholders(
                        step[k], vars_dict, step_num=i, logger=logger
                    )
                    step[k] = new_val
                    if not missing:
                        logger.debug(f"Step {i}: substituted {k} {step[k]!r}")

            # Skip step if any required value still has placeholders
            has_unresolved = (
                isinstance(step.get("value"), str)
                and _PLACEHOLDER_RE.search(step["value"])
            )
            if has_unresolved:
                logger.warning(f"Step {i}: SKIPPED (unresolved placeholder in value)")
                skipped += 1
                continue

            logger.info(f"Step {i}/{len(steps)}: {action} {step_for_log}")

            if action == "goto":
                await page.goto(step.get("url", ""), wait_until="domcontentloaded", timeout=30000)
            elif action == "fill":
                await page.fill(step.get("selector", ""), step.get("value", ""), timeout=10000)
            elif action == "click":
                await page.click(step.get("selector", ""), timeout=10000)
            elif action == "select":
                # Try by value first, then by label
                try:
                    await page.select_option(step.get("selector", ""), value=step.get("value", ""))
                except Exception:
                    await page.select_option(step.get("selector", ""), label=step.get("value", ""))
            elif action == "file_upload":
                files = step.get("files", "")
                if isinstance(files, str):
                    files = files.split(",")
                await page.set_input_files(step.get("selector", ""), files)
            else:
                logger.warning(f"Unknown action: {action}, skipping")

        logger.info(f"Replay complete: {len(steps) - skipped} steps executed, {skipped} skipped")
        return 0
    finally:
        await context.close()
        await pw.stop()


def _run_inline_tests():
    """Quick unit tests for vars substitution. Run with: python replay_workflow.py --run-tests"""
    print("=== Testing _substitute_placeholders ===")

    # Test 1: simple substitution
    result, missing = _substitute_placeholders("{{po}}", {"po": "PO-999"})
    assert result == "PO-999", f"FAIL: {result!r}"
    assert missing == [], f"FAIL: {missing}"
    print("  Test 1 PASS: {{po}} -> PO-999")

    # Test 2: multiple vars
    result, missing = _substitute_placeholders("{{a}}-{{b}}", {"a": "x", "b": "y"})
    assert result == "x-y", f"FAIL: {result!r}"
    print("  Test 2 PASS: {{a}}-{{b}} -> x-y")

    # Test 3: missing var leaves placeholder
    result, missing = _substitute_placeholders("{{unknown}}", {})
    assert result == "{{unknown}}", f"FAIL: {result!r}"
    assert "unknown" in missing
    print("  Test 3 PASS: missing var left as placeholder")

    # Test 4: non-string input passes through
    result, missing = _substitute_placeholders(42, {})
    assert result == 42
    print("  Test 4 PASS: non-string passes through")

    # Test 5: build_vars_dict from CLI
    class FakeArgs:
        vars = ["a=1", "b=2"]
        vars_file = None
    v = _build_vars_dict(FakeArgs())
    assert v == {"a": "1", "b": "2"}, f"FAIL: {v}"
    print(f"  Test 5 PASS: --vars a=1 b=2 -> {v}")

    # Test 6: build_vars_dict from file
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"c": "3", "d": "4"}, f)
        tmp_path = f.name
    class FakeArgs2:
        vars = []
        vars_file = tmp_path
    v = _build_vars_dict(FakeArgs2())
    assert v == {"c": "3", "d": "4"}, f"FAIL: {v}"
    print(f"  Test 6 PASS: --vars-file -> {v}")

    print("=== All tests passed ===")


def main():
    args = _parse_vars_args()

    try:
        vars_dict = _build_vars_dict(args)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    logger = _setup_logger()
    logger.info(f"Workflow: {args.workflow_path}")
    logger.info(f"Chrome profile: {args.profile_dir}")

    exit_code = asyncio.run(replay(args.workflow_path, args.profile_dir, vars_dict, logger))
    sys.exit(exit_code)


if __name__ == "__main__":
    # Skip tests when called via main; only run when explicitly requested
    if "--run-tests" in sys.argv:
        sys.argv.remove("--run-tests")
        _run_inline_tests()
    else:
        main()
