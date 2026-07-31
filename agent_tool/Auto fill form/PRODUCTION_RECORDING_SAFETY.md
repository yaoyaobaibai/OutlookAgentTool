# Production Recording Safety

## Context

Acubuy has no UAT environment. To enable automation, the user must do a
**one-time production recording** of a real GR submission flow. The
recording file will contain real production data:

- PO numbers
- Vendor / supplier names
- Quantities
- Amounts
- Internal comments

## The Rules

### 1. Original recordings NEVER go to git

The raw `recordings/recorder_log_*.json` files contain production data
and **MUST NOT be committed to the shared git repository**.

**Enforcement**: `.gitignore` blocks `agent_tool/Auto fill form/recordings/*.json`
and `*.json.bak`. Even if you try to `git add -f`, do not.

### 2. Only parameterized workflow.json is git-tracked

The converter (`recorder_to_workflow.py`) replaces all user-typed values
with `{{var_name}}` placeholders. The output is safe to commit because
it contains only **structure** (selectors, action types) — no actual data.

Example:
- Before parameterization: `{"value": "PO-2024-12345"}`
- After parameterization: `{"value": "{{po_number}}"}`

### 3. Provide actual values at runtime

When replaying, the user provides actual values via CLI args or a config file:

```bash
python replay_workflow.py workflow.json \
  --vars po_number=PO-2024-12345 \
  --vars vendor_name="Acme Corp" \
  --vars quantity=50
```

Or:

```bash
python replay_workflow.py workflow.json --vars-file /path/to/secret_vars.json
```

The vars file should NEVER be committed (add `*_vars.json` to `.gitignore`
if you create one).

### 4. .bak files are also sensitive

`sanitize_recording.py` creates a `.bak` backup of the original recording
before overwriting. The `.bak` contains the SAME production data as the
original. **Do not commit .bak files either** (already in `.gitignore`).

## The Workflow

```
1. User records on production Acubuy
   ↓ (file: recordings/recorder_log_YYYYMMDD_HHMMSS.json)
2. Run converter locally
   python recorder_to_workflow.py recordings/<file>.json workflow.json
   ↓ (file: workflow.json — parameterized, safe to commit)
3. User reviews workflow.json
   - Verify all `fill` values are `{{var}}` placeholders
   - Verify no real PO numbers / vendor names
4. Commit workflow.json
   git add workflow.json
   git commit -m "feat: add Acubuy GR workflow (parameterized)"
   git push
5. Run replay locally with secrets
   python replay_workflow.py workflow.json --vars-file secret_vars.json
```

## Pre-Commit Checklist

Before `git add` of any FormFiller file:

- [ ] No `recordings/*.json` in `git status`
- [ ] No `recordings/*.json.bak` in `git status`
- [ ] No `workflows/*_prod_*.json` in `git status`
- [ ] If adding a new workflow.json: verify `parameterized: true` flag is set
- [ ] If adding a new workflow.json: grep for known field patterns (PO, vendor, etc.) — should only find `{{...}}` placeholders, not actual values
- [ ] If vars file exists: ensure it's in `.gitignore` (e.g. `secret_vars.json`)

## What to do if a recording file was accidentally committed

1. **DO NOT PANIC** — but act fast.
2. Use `git filter-branch` or `git filter-repo` to remove the file from
   the entire git history.
3. Force push (this is the ONE time force push is acceptable):
   `git push --force-with-lease`
4. Rotate any secrets that may have been in the recording (PO numbers
   are not strictly secrets, but treat them as sensitive anyway).
5. Inform the team that a force push happened.
