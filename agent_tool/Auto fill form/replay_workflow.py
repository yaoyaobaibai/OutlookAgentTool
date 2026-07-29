# -*- coding: utf-8 -*-
"""Replay a workflow.json using Playwright.

Connects to a persistent Chrome profile (so cookies/session persist).
Reads workflow.json steps and dispatches each via Playwright.

CLI:
    python replay_workflow.py <workflow.json> [chrome_profile_dir]

Default profile dir: %USERPROFILE%/AcubuyChromeProfile
"""

import asyncio
import json
import os
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


async def replay(workflow_path: str, profile_dir: str, logger) -> int:
    """Replay a workflow.json. Returns 0 on success, non-zero on error."""
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    steps = workflow.get("steps", [])
    logger.info(f"Replaying workflow: {workflow.get('name', '?')} ({len(steps)} steps)")
    logger.info(f"Source recording: {workflow.get('source_recording', '?')}")
    logger.info(f"Recorded at: {workflow.get('recorded_at', '?')}")
    logger.info(f"Password events filtered: {workflow.get('password_events_filtered', 0)}")

    if not steps:
        logger.error("No steps in workflow")
        return 1

    pw, context = await _launch_chrome(profile_dir)
    try:
        # Use first existing page or create one
        page = context.pages[0] if context.pages else await context.new_page()

        for i, step in enumerate(steps, 1):
            action = step.get("action")
            logger.info(f"Step {i}/{len(steps)}: {action} {step}")

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

        logger.info(f"Replay complete: {len(steps)} steps executed")
        return 0
    finally:
        await context.close()
        await pw.stop()


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(f"Usage: {sys.argv[0]} <workflow.json> [chrome_profile_dir]")
        print(f"Default profile dir: {DEFAULT_PROFILE_DIR}")
        sys.exit(1)

    workflow_path = sys.argv[1]
    profile_dir = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PROFILE_DIR

    logger = _setup_logger()
    logger.info(f"Workflow: {workflow_path}")
    logger.info(f"Chrome profile: {profile_dir}")

    exit_code = asyncio.run(replay(workflow_path, profile_dir, logger))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
