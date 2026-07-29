# -*- coding: utf-8 -*-
"""Convert recorder JSON → declarative workflow.json.

Process:
1. Read recorder JSON events
2. Consolidate consecutive same-selector `text` events into single fill (take last value)
3. **FILTER OUT** password events entirely (defense-in-depth — recorder should also filter, but we filter here too)
4. Convert `click` events to `click` action
5. Convert `navigate` events to `goto` action (skip chrome:// new-tab-page, keep first real URL)
6. Convert `select` events to `select` action
7. Convert `file_input` to `file_upload` action
8. Output: workflow.json with steps array matching `workflows/csms_create_proposal/workflow.json` schema

Password detection (any match → filter):
- event type == "password"
- selector contains "TextBox2" (CSMS pattern) or "password" (case-insensitive)
- attrs contain `type="password"`

CLI:
    python recorder_to_workflow.py recordings/recorder_log_20260728_200430.json output_workflow.json
"""

import json
import os
import re
import sys
from datetime import datetime


# Patterns that identify password fields (defense-in-depth)
_PASSWORD_PATTERNS = [
    re.compile(r"TextBox2\b", re.IGNORECASE),       # CSMS pattern
    re.compile(r"password", re.IGNORECASE),         # generic
    re.compile(r"type\s*=\s*['\"]?password", re.IGNORECASE),  # attrs string
]


def _is_password_event(event: dict) -> bool:
    """Check if an event is a password field event. Returns True if so."""
    if event.get("type") == "password":
        return True
    selector = str(event.get("selector", ""))
    attrs = str(event.get("attrs", ""))
    for pattern in _PASSWORD_PATTERNS:
        if pattern.search(selector) or pattern.search(attrs):
            return True
    return False


def _is_chrome_internal_url(url: str) -> bool:
    """Skip chrome:// and chrome-untrusted:// URLs."""
    return url.startswith("chrome://") or url.startswith("chrome-untrusted://")


def _consolidate_text_events(events: list) -> list:
    """Merge consecutive text events on the same selector into single fill actions.
    
    Returns a new list of consolidated events. Other event types pass through unchanged.
    """
    result = []
    text_buffer = {}  # selector -> latest value (overwrites as we see new values)
    text_selector = None  # which selector the buffer is for
    
    def flush_text():
        nonlocal text_buffer, text_selector
        if text_buffer and text_selector is not None:
            result.append({
                "type": "input",
                "selector": text_selector,
                "value": text_buffer,
            })
        text_buffer = {}
        text_selector = None
    
    for ev in events:
        ev_type = ev.get("type")
        if ev_type == "text":
            selector = ev.get("selector", "")
            value = ev.get("value", "")
            if text_selector and text_selector != selector:
                # Switched selectors — flush previous
                flush_text()
            text_selector = selector
            text_buffer = value  # latest value wins
        else:
            flush_text()
            result.append(ev)
    
    flush_text()  # flush any trailing text buffer
    return result


def convert_recording_to_workflow(input_path: str, output_path: str) -> dict:
    """Convert a recorder JSON file to a workflow.json file.
    
    Returns the workflow dict (also written to output_path).
    """
    with open(input_path, "r", encoding="utf-8") as f:
        recording = json.load(f)
    
    raw_events = recording.get("events", [])
    recorded_at = recording.get("recorded_at", "")
    session_tag = recording.get("session_tag", "")
    
    # Step 1: Filter out password events (defense-in-depth)
    filtered_events = [ev for ev in raw_events if not _is_password_event(ev)]
    password_count = len(raw_events) - len(filtered_events)
    
    # Step 2: Consolidate text events
    consolidated = _consolidate_text_events(filtered_events)
    
    # Step 3: Map to workflow steps
    steps = []
    for ev in consolidated:
        ev_type = ev.get("type")
        if ev_type == "navigate":
            url = ev.get("url", "")
            if not _is_chrome_internal_url(url):
                steps.append({
                    "action": "goto",
                    "url": url,
                })
        elif ev_type == "input":
            steps.append({
                "action": "fill",
                "selector": ev.get("selector", ""),
                "value": ev.get("value", ""),
            })
        elif ev_type == "click":
            steps.append({
                "action": "click",
                "selector": ev.get("selector", ""),
            })
        elif ev_type == "select":
            steps.append({
                "action": "select",
                "selector": ev.get("selector", ""),
                "value": ev.get("value", ""),
            })
        elif ev_type == "file_input":
            files = ev.get("files", "")
            if files:
                steps.append({
                    "action": "file_upload",
                    "selector": ev.get("selector", ""),
                    "files": files,
                })
        # Other types (focus, blur, postback, etc.) — skip
    
    workflow = {
        "name": os.path.splitext(os.path.basename(input_path))[0],
        "source_recording": os.path.basename(input_path),
        "recorded_at": recorded_at,
        "session_tag": session_tag,
        "generated_at": datetime.now().isoformat(),
        "step_count": len(steps),
        "password_events_filtered": password_count,
        "steps": steps,
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    
    return workflow


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_recording.json> <output_workflow.json>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    workflow = convert_recording_to_workflow(input_path, output_path)
    
    print(f"Converted {input_path} -> {output_path}")
    print(f"  Steps: {workflow['step_count']}")
    print(f"  Password events filtered: {workflow['password_events_filtered']}")
    print(f"  First step: {workflow['steps'][0] if workflow['steps'] else '(none)'}")


if __name__ == "__main__":
    main()
