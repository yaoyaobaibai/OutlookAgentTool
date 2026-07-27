#!/usr/bin/env python3
"""
Workflow Config Validator
Validates a workflow.json file against the workflow JSON Schema.

Usage:
    python validate_workflow.py <path-to-workflow.json>
    python validate_workflow.py <path-to-workflow.json> --schema <path-to-schema.json>

Exit codes:
    0 - Valid
    1 - Invalid (prints errors)
    2 - File not found or schema not found
"""

import json
import os
import sys

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path, description):
    """Load a JSON file, returning (data, error)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"{description} not found: {path}"
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in {description}: {e}"


# ---------------------------------------------------------------------------
# jsonschema library wrapper
# ---------------------------------------------------------------------------

def _validate_with_jsonschema(workflow, schema):
    """Try validating with the jsonschema library. Returns (valid, errors)."""
    try:
        import jsonschema
    except ImportError:
        return None  # signal "not available"

    try:
        jsonschema.validate(workflow, schema)
        return True, []
    except jsonschema.exceptions.ValidationError as e:
        # Collect the full error tree for detailed messages
        errors = []
        v = jsonschema.Draft7Validator(schema)
        for error in v.iter_errors(workflow):
            path = " -> ".join(str(p) for p in error.absolute_path) if error.absolute_path else "(root)"
            errors.append(f"  - [{path}] {error.message}")
        if not errors:
            errors.append(f"  - {e.message}")
        return False, errors


# ---------------------------------------------------------------------------
# Manual validation (fallback when jsonschema is not installed)
# ---------------------------------------------------------------------------

def _manual_validate(workflow, schema):
    """
    Simple manual validation that covers the main structural rules.
    Returns (valid, errors).
    """
    errors = []

    def _add_error(path, msg):
        errors.append(f"  - [{path}] {msg}")

    # --- 1. Check top-level type ---
    if not isinstance(workflow, dict):
        _add_error("(root)", "Root element must be a JSON object (dict)")
        return False, errors

    # --- 2. Required fields ---
    for req_field in ("workflow_name", "version", "fields"):
        if req_field not in workflow:
            _add_error("(root)", f"Required property '{req_field}' is missing")

    # --- 3. Check additionalProperties at each object level ---
    schema_props = schema.get("properties", {})

    for key in workflow:
        if key not in schema_props and schema.get("additionalProperties", True) is False:
            _add_error("(root)", f"Additional property '{key}' is not allowed")

    # --- 4. Type checks for top-level properties ---
    _check_prop(workflow, schema_props, "", errors, _add_error)

    # --- 5. Field configs ---
    if isinstance(workflow.get("fields"), dict):
        field_schema = schema_props.get("fields", {})
        field_item_schema = None
        if "$ref" in field_schema:
            ref_path = field_schema["$ref"].lstrip("#/$defs/")
            field_item_schema = schema.get("$defs", {}).get(ref_path, {})
        elif "additionalProperties" in field_schema:
            ref = field_schema["additionalProperties"]
            if isinstance(ref, dict) and "$ref" in ref:
                ref_path = ref["$ref"].lstrip("#/$defs/")
                field_item_schema = schema.get("$defs", {}).get(ref_path, {})

        for fname, fcfg in workflow["fields"].items():
            if not isinstance(fcfg, dict):
                _add_error(f"fields.{fname}", "Field config must be an object")
                continue
            if field_item_schema:
                _check_obj(fcfg, field_item_schema, f"fields.{fname}", errors, _add_error)

    # --- 6. Navigation steps ---
    if isinstance(workflow.get("navigation"), list):
        nav_schema = None
        nav_props = schema_props.get("navigation", {})
        items = nav_props.get("items", {})
        if "$ref" in items:
            ref_path = items["$ref"].lstrip("#/$defs/")
            nav_schema = schema.get("$defs", {}).get(ref_path, {})

        for i, step in enumerate(workflow["navigation"]):
            if not isinstance(step, dict):
                _add_error(f"navigation[{i}]", "Step must be an object")
                continue
            if nav_schema:
                _check_obj(step, nav_schema, f"navigation[{i}]", errors, _add_error)

    # --- 7. Login ---
    if isinstance(workflow.get("login"), dict):
        login_props = schema_props.get("login", {}).get("properties", {})
        _check_obj(workflow["login"], schema_props.get("login", {}), "login", errors, _add_error)

    # --- 8. handlers ---
    if isinstance(workflow.get("handlers"), dict):
        for hname, hcfg in workflow["handlers"].items():
            if not isinstance(hcfg, dict):
                _add_error(f"handlers.{hname}", "Handler config must be an object")

    # --- 9. attachment ---
    if isinstance(workflow.get("attachment"), dict):
        _check_obj(workflow["attachment"], schema_props.get("attachment", {}), "attachment", errors, _add_error)

    # --- 10. post_fill ---
    if isinstance(workflow.get("post_fill"), dict):
        _check_obj(workflow["post_fill"], schema_props.get("post_fill", {}), "post_fill", errors, _add_error)

    return len(errors) == 0, errors


def _check_prop(obj, prop_schemas, prefix, errors, add_err):
    """Check basic property types and enums."""
    for key, value in obj.items():
        if key not in prop_schemas:
            continue
        ps = prop_schemas[key]
        path = f"{prefix}.{key}" if prefix else key

        if isinstance(ps, dict):
            # Type check
            expected_type = ps.get("type")
            if expected_type == "string" and not isinstance(value, str):
                add_err(path, f"Expected string, got {type(value).__name__}")
            elif expected_type == "boolean" and not isinstance(value, bool):
                add_err(path, f"Expected boolean, got {type(value).__name__}")
            elif expected_type == "integer" and not isinstance(value, int):
                add_err(path, f"Expected integer, got {type(value).__name__}")
            elif expected_type == "number" and not isinstance(value, (int, float)):
                add_err(path, f"Expected number, got {type(value).__name__}")
            elif expected_type == "array" and not isinstance(value, list):
                add_err(path, f"Expected array, got {type(value).__name__}")
            elif expected_type == "object" and not isinstance(value, dict):
                add_err(path, f"Expected object, got {type(value).__name__}")

            # Enum check
            if "enum" in ps and isinstance(value, str):
                if value not in ps["enum"]:
                    add_err(path, f"Value '{value}' not in enum {ps['enum']}")

            # Pattern check
            if "pattern" in ps and isinstance(value, str):
                import re
                if not re.match(ps["pattern"], value):
                    add_err(path, f"String '{value}' does not match pattern {ps['pattern']}")


def _check_obj(obj, schema_obj, prefix, errors, add_err):
    """Validate an object against its schema definition (incl. required, additionalProperties)."""
    if not isinstance(obj, dict) or not isinstance(schema_obj, dict):
        return

    props = schema_obj.get("properties", {})
    required = schema_obj.get("required", [])
    additional = schema_obj.get("additionalProperties", True)

    # Check required
    for req in required:
        if req not in obj:
            add_err(prefix, f"Required property '{req}' is missing")

    # Check additional properties
    if additional is False:
        for key in obj:
            if key not in props and key not in required:
                add_err(prefix, f"Additional property '{key}' is not allowed")

    # Check each property
    _check_prop(obj, props, prefix, errors, add_err)

    # Recurse into nested objects with $ref
    for key, value in obj.items():
        if key not in props:
            continue
        ps = props[key]
        if isinstance(value, dict) and ps.get("type") == "object":
            # Check if this object has a $ref
            ref = ps.get("$ref")
            if ref:
                pass  # referenced schema handled elsewhere
            _check_obj(value, ps, f"{prefix}.{key}", errors, add_err)


# ---------------------------------------------------------------------------
# Main validation entry point
# ---------------------------------------------------------------------------

def validate_workflow(workflow_path, schema_path=None):
    """
    Validate a workflow.json file against the workflow JSON Schema.

    Parameters
    ----------
    workflow_path : str
        Path to the workflow JSON file.
    schema_path : str, optional
        Path to the JSON Schema file. If not provided, defaults to
        ``<this-script-dir>/workflow-schema.json``.

    Returns
    -------
    (is_valid: bool, errors: list of str)
    """
    # Resolve schema path
    if schema_path is None:
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workflow-schema.json")

    # Load files
    workflow, err = _load_json(workflow_path, "Workflow file")
    if err:
        return False, [err]

    schema, err = _load_json(schema_path, "Schema file")
    if err:
        return False, [err]

    # Try jsonschema library first
    result = _validate_with_jsonschema(workflow, schema)
    if result is not None:
        return result

    # Fallback to manual validation
    return _manual_validate(workflow, schema)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if len(sys.argv) < 2 else 0

    workflow_path = sys.argv[1]
    schema_path = None

    if len(sys.argv) >= 4 and sys.argv[2] == "--schema":
        schema_path = sys.argv[3]

    if not os.path.isfile(workflow_path):
        print(f"Error: workflow file not found: {workflow_path}", file=sys.stderr)
        return 2

    is_valid, errors = validate_workflow(workflow_path, schema_path)

    if is_valid:
        print(f"Valid: {workflow_path}")
        return 0
    else:
        print(f"Invalid: {workflow_path}")
        for err in errors:
            print(err)
        return 1


if __name__ == "__main__":
    sys.exit(main())
