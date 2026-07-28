# Learnings - Workflow Architecture Refactor

## Task 3: WorkflowManager

- The `validate_workflow` module from the schema directory may not exist during Task 3 execution (parallel task).
  The WorkflowManager gracefully handles this by attempting import and warning if unavailable.
- Settings persistence uses `os.makedirs(settings_dir, exist_ok=True)` to handle missing workflows/ directory.
- Discovery skips directories starting with `_` or `.` to avoid picking up schema/, _archive/, etc.
- Discovery logs WARNING for directories without workflow.json instead of raising exceptions.
- `set_current_workflow()` validates the workflow exists in the discovered list OR checks for the workflow.json
  on disk before persisting. This prevents saving invalid workflow names.
- Use `importlib.util.spec_from_file_location` for importing validate_workflow from a non-standard path
  (the workflows/schema/ directory), avoiding issues with Python's module resolution.
