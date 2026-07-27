
## 2026-07-23 20:11 - form_filler.py rewrite completed

- Rewrote form_filler.py from 1204 lines to 840 lines
- Removed ConfigManager class (replaced by WorkflowManager)
- Removed FieldEditorDialog (fields now come from workflow config)
- Removed manual add/edit/delete field buttons
- Added WorkflowSelector (Combobox) at top of window
- Added _on_workflow_changed handler that updates login URL and fields
- Added _load_fields_from_workflow using WorkflowManager.get_field_definitions()
- Added log panel (Text widget) with _log() method
- Added Stop button + _stop_execution() calling engine.stop()
- Added _build_field_values() for Excel data loading
- Uses WorkflowEngine with registered callbacks (on_field_start, on_field_end, on_error)
- Kept AttachmentManager and AttachmentDialog for backward compatibility
- Kept browser selection, chrome path, username/password, excel, attachments
- Field treeview now shows 4 columns: Label | Selector | Type | Required
- Start button text updates to match current workflow display name
- Added backward compatibility warning for legacy form_config.json
