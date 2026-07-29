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


def _selector_to_var_name(selector: str, fallback_counter: int) -> str:
    """Extract a human-readable var name from a CSS selector.
    
    Tries (in order):
    1. id attribute: '#fooBar' or 'input#fooBar' -> 'fooBar'
    2. name attribute: "input[name='poNumber']" -> 'poNumber'
    3. last class: 'div.poNumber' -> 'poNumber'
    4. last segment after ':' or '#': 'cssfinder:bar' -> 'bar'
    5. fallback: 'field_N' (counter)
    
    Returns: lowercase, underscore-separated identifier
    """
    # Try id="..." or #id patterns
    m = re.search(r'(?:#|\bid=[\'"])([A-Za-z][A-Za-z0-9_]*)', selector)
    if m:
        return _sanitize_var_name(m.group(1))
    
    # Try name="..." or name='...'
    m = re.search(r'\bname=[\'"]([A-Za-z][A-Za-z0-9_\-]*)[\'"]', selector)
    if m:
        return _sanitize_var_name(m.group(1))
    
    # Try last class: 'div.poNumber' or '.poNumber'
    m = re.search(r'\.([A-Za-z][A-Za-z0-9_\-]*)\s*(?::|$|\s)', selector + " ")
    if m:
        return _sanitize_var_name(m.group(1))
    
    # Try last segment after a separator
    parts = re.split(r'[:#.\s>]+', selector)
    parts = [p for p in parts if p and not p.startswith('[') and p not in ('input', 'select', 'textarea', 'button', 'form', 'div', 'span')]
    if parts:
        return _sanitize_var_name(parts[-1])
    
    return f"field_{fallback_counter}"


def _sanitize_var_name(name: str) -> str:
    """Convert to valid identifier: lowercase, underscores, alphanumeric only."""
    name = re.sub(r'[^A-Za-z0-9_]', '_', name)
    name = re.sub(r'_+', '_', name).strip('_')
    return name.lower() or 'field'


def _infer_type(value: str) -> str:
    """Infer the type of a value from its pattern."""
    if not value:
        return "string"
    # Number (int or float)
    if re.fullmatch(r'-?\d+', value):
        return "number"
    if re.fullmatch(r'-?\d+\.\d+', value):
        return "float"
    # Email
    if re.fullmatch(r'[^@]+@[^@]+\.[^@]+', value):
        return "email"
    # Date (YYYY-MM-DD or similar)
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        return "date"
    if re.fullmatch(r'\d{2}/\d{2}/\d{4}', value):
        return "date"
    return "string"


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


def convert_recording_to_workflow(
    input_path: str,
    output_path: str,
    parameterize: bool = True,
) -> dict:
    """Convert a recorder JSON file to a workflow.json file.
    
    If parameterize=True (default), all fill values are replaced with
    {{var_name}} placeholders. Use --no-parameterize to keep raw values
    (NOT recommended for production recordings).
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
    
    # Step 3: Map to workflow steps (with parameterization)
    steps = []
    seen_selectors = {}  # selector -> var_name
    fallback_counter = 0
    parameters = {}  # var_name -> {"type": ..., "selector": ...}
    
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
            selector = ev.get("selector", "")
            raw_value = ev.get("value", "")
            
            if parameterize:
                if selector in seen_selectors:
                    var_name = seen_selectors[selector]
                else:
                    fallback_counter += 1
                    var_name = _selector_to_var_name(selector, fallback_counter)
                    seen_selectors[selector] = var_name
                    parameters[var_name] = {
                        "type": _infer_type(raw_value),
                        "selector": selector,
                    }
                # Use placeholder
                display_value = f"{{{{{var_name}}}}}"
            else:
                display_value = raw_value
                # Also store original in parameters for reference
                if not parameters.get("__raw_values__"):
                    parameters["__raw_values__"] = {"warning": "raw values not parameterized"}
            
            steps.append({
                "action": "fill",
                "selector": selector,
                "value": display_value,
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
        "parameterized": parameterize,
        "parameters": parameters,
        "var_substitution_hint": (
            "All 'fill' step values use {{var}} placeholders. Provide actual values at runtime: "
            "python replay_workflow.py workflow.json --vars key1=value1 --vars key2=value2"
        ),
        "steps": steps,
    }
    
    if not parameterize:
        workflow["WARNING_RAW_VALUES"] = "Raw values present. Do NOT commit to git."
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    
    return workflow


def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(f"Usage: {sys.argv[0]} <input_recording.json> <output_workflow.json> [--no-parameterize]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    parameterize = "--no-parameterize" not in sys.argv
    
    workflow = convert_recording_to_workflow(input_path, output_path, parameterize=parameterize)
    
    print(f"Converted {input_path} -> {output_path}")
    print(f"  Steps: {workflow['step_count']}")
    print(f"  Password events filtered: {workflow['password_events_filtered']}")
    print(f"  Parameterized: {workflow['parameterized']}")
    if workflow['parameters']:
        print(f"  Parameters ({len(workflow['parameters'])}):")
        for k, v in workflow['parameters'].items():
            print(f"    {{{{{k}}}}}: type={v.get('type', '?')}")
    if workflow['steps']:
        print(f"  First step: {workflow['steps'][0]}")
        # Find first fill step
        for s in workflow['steps']:
            if s.get('action') == 'fill':
                print(f"  First fill step value: {s.get('value')}")
                break


if __name__ == "__main__":
    main()
