# WorkflowEngine Notepad

## Learnings

- The handlers package uses a registry pattern: `get_handler(type)` returns a **class**, not an instance. The engine must instantiate with `cls(page, workflow_config)`.
- Handlers return dicts with `{"success": bool, "message": str, "evidence": dict}` — the engine checks `result.get("success")`.
- `BaseHandler.retry_count()` defaults to 2 (3 total attempts including first try).
- Workflow config fields use `depends_on` for ordering — the engine implements topological sort.
- All handler `execute()` methods catch exceptions internally and return error dicts — the engine's retry loop handles both exception-based and result-based failures.
- The engine uses `_try_fill_selectors` pattern (tried selectors in order, first match wins) for login fields.
- Navigation supports: goto, click, wait_selector, wait_time, evaluate.
- Post-fill actions support: click_button, click_and_wait, wait.
