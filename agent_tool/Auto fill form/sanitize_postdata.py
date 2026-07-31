# -*- coding: utf-8 -*-
"""One-shot sanitizer: scrub password leaks from existing recorder JSON files.

Background: The recorder.py 3-layer password filter (text type, password
type, TextBox2 selector) missed a 4th leak vector: postback.post_data field
contains URL-encoded form data including raw passwords. This script walks
existing .json recordings and redacts those values.

Usage:
    python sanitize_postdata.py             # sanitize all .json files
    python sanitize_postdata.py --dry-run   # show what would change, don't write
    python sanitize_postdata.py path/to/file.json  # specific file
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime


# Same regex as recorder.py (4th layer)
_POSTDATA_PASSWORD_RE = re.compile(
    r'(?:([&;])((?:password|passwd|pwd|secret|wt\d+)=))([^&;]*)',
    re.IGNORECASE
)


def _redact_postdata(post_data: str) -> str:
    if not post_data:
        return post_data
    def replace(match):
        return f"{match.group(1)}{match.group(2)}[REDACTED]"
    return _POSTDATA_PASSWORD_RE.sub(replace, post_data)


def sanitize_file(json_path: str, dry_run: bool = False) -> dict:
    """Sanitize a single recording JSON file. Returns stats."""
    if not os.path.isfile(json_path):
        return {"path": json_path, "error": "file not found"}
    
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            recording = json.load(f)
        except json.JSONDecodeError as e:
            return {"path": json_path, "error": f"JSON decode error: {e}"}
    
    events = recording.get("events", [])
    redactions_count = 0
    files_redacted = []
    
    for event in events:
        if event.get("type") == "postback":
            old_post_data = event.get("post_data", "")
            new_post_data = _redact_postdata(old_post_data)
            if new_post_data != old_post_data:
                redactions_count += 1
                files_redacted.append({
                    "selector": event.get("selector", "?"),
                    "ts": event.get("ts", "?"),
                })
                if not dry_run:
                    event["post_data"] = new_post_data
    
    if redactions_count > 0 and not dry_run:
        # Backup original BEFORE overwrite (if not already)
        backup_path = json_path + ".bak"
        if not os.path.isfile(backup_path):
            import shutil
            shutil.copy2(json_path, backup_path)
        
        # Write sanitized
        recording["sanitized_at"] = datetime.now().isoformat()
        recording["sanitized_by"] = "sanitize_postdata.py v1"
        recording["redactions_count"] = redactions_count
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(recording, f, ensure_ascii=False, indent=2)
    
    return {
        "path": json_path,
        "redactions_count": redactions_count,
        "files_redacted": files_redacted,
        "dry_run": dry_run,
    }


def main():
    parser = argparse.ArgumentParser(description="Scrub password leaks from recorder JSON files")
    parser.add_argument("paths", nargs="*",
                        help="Specific files to sanitize (default: scan all recordings/)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change, don't write")
    parser.add_argument("--roots", nargs="+",
                        default=[
                            os.path.join(os.path.dirname(__file__), "recordings"),
                            os.path.join(os.path.dirname(__file__), "dist", "recordings"),
                        ],
                        help="Root directories to scan (default: ./recordings and ./dist/recordings)")
    args = parser.parse_args()
    
    # Collect files to process
    files_to_process = []
    if args.paths:
        files_to_process = list(args.paths)
    else:
        for root in args.roots:
            if os.path.isdir(root):
                for f in os.listdir(root):
                    if f.endswith(".json") and not f.endswith(".bak.json"):
                        files_to_process.append(os.path.join(root, f))
    
    if not files_to_process:
        print("No .json files found to sanitize.")
        return 0
    
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Sanitizing {len(files_to_process)} file(s)...")
    print()
    
    total_redactions = 0
    for path in files_to_process:
        result = sanitize_file(path, dry_run=args.dry_run)
        if "error" in result:
            print(f"  ERROR: {result['path']}: {result['error']}")
        else:
            count = result["redactions_count"]
            total_redactions += count
            status = "would redact" if args.dry_run else "redacted"
            print(f"  {result['path']}: {count} post_data {status}")
            if count > 0:
                for entry in result["files_redacted"]:
                    print(f"    - ts={entry['ts']} selector={entry['selector']}")
    
    print()
    print(f"=== Summary ===")
    print(f"  Files scanned: {len(files_to_process)}")
    print(f"  Total redactions: {total_redactions}")
    if args.dry_run:
        print(f"  (Dry run — no changes written)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
