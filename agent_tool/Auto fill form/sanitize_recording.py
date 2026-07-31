# -*- coding: utf-8 -*-
"""One-time sanitizer: strip password events from existing recordings.

Reads a recorder JSON, removes all events that look like password inputs
(type="password" or selector contains TextBox2 or "password"), writes
sanitized version back to the same path. Original is backed up to .bak.

CLI:
    python sanitize_recording.py recordings/recorder_log_20260728_200430.json
"""

import json
import re
import sys
from datetime import datetime


_PASSWORD_PATTERNS = [
    re.compile(r"TextBox2\b", re.IGNORECASE),
    re.compile(r"password", re.IGNORECASE),
]


def _is_password_event(event: dict) -> bool:
    if event.get("type") == "password":
        return True
    selector = str(event.get("selector", ""))
    attrs = str(event.get("attrs", ""))
    for pattern in _PASSWORD_PATTERNS:
        if pattern.search(selector) or pattern.search(attrs):
            return True
    return False


def sanitize_recording(input_path: str) -> dict:
    """Strip password events from a recording JSON. Back up original to .bak.

    Returns a dict with sanitization stats.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        recording = json.load(f)
    
    raw_events = recording.get("events", [])
    total_before = len(raw_events)
    
    # Filter
    sanitized_events = [ev for ev in raw_events if not _is_password_event(ev)]
    password_count = total_before - len(sanitized_events)
    
    # Backup original
    backup_path = input_path + ".bak"
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(recording, f, ensure_ascii=False, indent=2)
    
    # Write sanitized
    recording["events"] = sanitized_events
    recording["total_events"] = len(sanitized_events)
    recording["sanitized_at"] = datetime.now().isoformat()
    recording["password_events_removed"] = password_count
    
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(recording, f, ensure_ascii=False, indent=2)
    
    return {
        "input_path": input_path,
        "backup_path": backup_path,
        "events_before": total_before,
        "events_after": len(sanitized_events),
        "password_events_removed": password_count,
    }


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <recording.json>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    stats = sanitize_recording(input_path)
    
    print(f"Sanitized: {stats['input_path']}")
    print(f"  Backup: {stats['backup_path']}")
    print(f"  Events: {stats['events_before']} -> {stats['events_after']}")
    print(f"  Password events removed: {stats['password_events_removed']}")


if __name__ == "__main__":
    main()
