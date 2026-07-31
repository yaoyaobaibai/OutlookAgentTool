# Security Note: Recorder Password Leak Fix

## The Leak

The recorder.py script had a **CVE-level password leak vulnerability** in the
`postback` event type. While the previous 3-layer filter caught:
- `event_type == "password"` events
- selectors matching `TextBox2` or `password`
- attrs containing `type="password"`

It **missed the `post_data` field** in `postback` events. This field contains
URL-encoded form submission data including raw passwords.

### Example of the leak

In `dist/recordings/recorder_log_20260730_181847.json` (and any other recording
of a login form):

```json
{
  "type": "postback",
  "url": "https://appcentral1-dev.ncs.co/GravityLogin/Login.aspx?_ts=...",
  "method": "POST",
  "post_data": "__EVENTTARGET=wt19&...&wt15=zemilytan&wt18=password1&...",
  "resource_type": "XHR"
}
```

**`wt18=password1`** — the password `password1` — was recorded in plaintext.

### Why the previous filter missed it

The 3-layer filter operates on:
1. DOM events (JS listener) — catches `input` and `password` events
2. `_on_dom_input()` Python handler — defense-in-depth
3. `ActionLogger.record()` — final check on event type

But `postback` events are created from **network responses**, not DOM events.
The DOM listeners never see them. The postback event creation site in
`recorder.py:_on_request()` was not protected.

### The Fix

Added a 4th layer: **`_redact_postdata()` function** that scrubs password
values from the `post_data` string before it's saved.

```python
import re

_POSTDATA_PASSWORD_RE = re.compile(
    r'(?:([&;])((?:password|passwd|pwd|secret|wt\d+)=))([^&;]*)',
    re.IGNORECASE
)

def _redact_postdata(post_data: str) -> str:
    """Redact password values in URL-encoded post_data string."""
    if not post_data:
        return post_data
    def replace(match):
        return f"{match.group(1)}{match.group(2)}[REDACTED]"
    return _POSTDATA_PASSWORD_RE.sub(replace, post_data)
```

### Detection patterns

The regex redacts values for keys matching (case-insensitive):
- `password`, `passwd`, `pwd`, `secret`
- `wt\d+` (OutSystems platform convention — all `wt1`, `wt2`, ... numeric keys
  are treated as potentially sensitive; both usernames and passwords get
  `wt\d+` IDs)

### Files cleaned

The following existing recording files had password leaks and were sanitized:

1. `dist/recordings/recorder_log_20260730_181847.json`
   - `wt15=zemilytan&wt18=password1` → `wt15=[REDACTED]&wt18=[REDACTED]`
   - Backup: `dist/recordings/recorder_log_20260730_181847.json.bak`

Other recordings in `recordings/` were checked and had postback events
without password patterns (no redactions needed).

**Note:** Four older recordings in the working `recordings/` directory
(`recorder_log_20260728_*.json`) contain `"value": "password123"` in
`"type": "password"` DOM input events. These are captured DOM input values
from pre-existing recordings (not postback leaks). These exist because the
recorder captures user input by design; the `"type": "password"` event type
is already filtered at record time but existing recordings retain historical
data. If these passwords are production credentials, sanitize these files too.

### How to verify

1. **Run inline tests** (in recorder.py):
   ```bash
   cd agent_tool/Auto fill form
   python recorder.py --run-tests
   ```
   Expected: 6/6 tests PASS.

2. **Search for postback password leaks**:
   ```bash
   grep -r "wt18=password" "agent_tool\Auto fill form\recordings\*.json" "agent_tool\Auto fill form\dist\recordings\*.json"
   ```
   Expected: 0 results (or only matches in `.bak` files).

3. **Run sanitizer in dry-run mode** to preview changes:
   ```bash
   cd "agent_tool/Auto fill form"
   python sanitize_postdata.py --dry-run
   ```

### Recovery if a leaked recording was committed to git

If you accidentally committed a recording with leaked passwords BEFORE this
fix, the password is in git history. To clean it:

1. **Do NOT just delete the file** — git retains history.
2. Use `git filter-repo` or `git filter-branch` to scrub the file from
   all commits:
   ```bash
   pip install git-filter-repo
   git filter-repo --path "agent_tool/Auto fill form/recordings/*.json" --invert-paths
   git filter-repo --path "agent_tool/Auto fill form/dist/recordings/*.json" --invert-paths
   ```
3. Force push (acceptable for security incidents):
   ```bash
   git push --force-with-lease
   ```
4. **Rotate the leaked password immediately** — assume it's compromised.

### Lessons learned

1. **Test data leaks, not just filtered events.** When recording user actions,
   think about ALL data paths: DOM events, network requests, form submissions.
2. **OutSystems platform uses `wt\d+` for ALL form fields** — usernames,
   passwords, hidden fields, all numeric IDs. This is why we redact ALL `wt\d+`
   keys (which also redacts usernames — an acceptable tradeoff).
3. **Defense in depth isn't enough if a path is missed.** The 3-layer filter
   was solid for what it covered, but missed the network-layer postback.
4. **Always sanitize, never just filter at record time.** Even if recorder
   filters correctly going forward, existing recordings need cleaning.

### Related files

- `recorder.py` — added `_redact_postdata()` + wired into `_on_request()`
- `sanitize_postdata.py` — one-shot sanitizer for existing recordings
- `PRODUCTION_RECORDING_SAFETY.md` — broader recording safety rules
