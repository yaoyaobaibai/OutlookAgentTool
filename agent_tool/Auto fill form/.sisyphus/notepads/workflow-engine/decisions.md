# WorkflowEngine Decisions

## Architecture Decisions

1. **Engine receives config dict, not WorkflowManager** — Keeps the engine stateless w.r.t. discovery. Caller (GUI) manages the WorkflowManager lifecycle and passes the parsed config.

2. **Handlers instantiated per-field** — `_get_handler()` creates a new handler instance for each field. This avoids stale state across fields but could be optimized with caching.

3. **Retry at engine level, not handler level** — The engine owns the retry loop rather than each handler. This gives consistent retry behavior, logging, and event emission.

4. **Event callbacks via dict registry** — Simple `dict[str, callable]` pattern. Not a formal event system. Sufficient for the GUI to hook progress updates.

5. **Exception inheritance chain** — `WorkflowEngineError` → `WorkflowNavigationError`, `WorkflowFieldError`. Navigation and field errors are distinct because they have different recovery semantics.

6. **No GUI/imports from form_filler** — Engine is pure logic. The `execute()` method returns a result dict rather than updating UI directly.

7. **post_fill failures are non-fatal** — Wrapped in try/except with warning log, since a missed button click shouldn't fail the field fill itself.
