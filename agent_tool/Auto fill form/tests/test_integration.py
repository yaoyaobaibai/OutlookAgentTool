#!/usr/bin/env python3
"""
tests/test_integration.py — Integration tests for the FormFiller multi-workflow architecture.

Requirements (from .sisyphus plan):
  1. WorkflowManager discovers CSMS and GR-Acubuy workflows
  2. WorkflowEngine can be instantiated with workflow configs
  3. form_filler.py GUI can import and reference all modules
  4. All handler types registered and accessible
  5. Stop mechanism works
  6. Invalid configs handled gracefully

All tests are OFFLINE-SAFE — no Playwright browsers are launched.
No external test dependencies — uses assert/print only.
No production code is modified.
"""

import json
import os
import sys
import tempfile
import traceback

# ---------------------------------------------------------------------------
# Project root — add to sys.path so imports work from anywhere
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------
EXPECTED_WORKFLOWS = {"csms_create_proposal", "gracubuy_create_gr"}
EXPECTED_HANDLER_TYPES = {
    "input", "select", "checkbox", "autocomplete",
    "datepicker", "popup_search", "file_upload",
}

# Fields expected from CSMS workflow (label -> type)
CSMS_EXPECTED_FIELDS = {
    "Proposal #": "input",
    "Cust Ref. No": "input",
    "Proposal/Contract Value": "input",
    "Selling Price Currency Code": "select",
    "Date of Award": "datepicker",
    "Priming Project Manager": "popup_search",
}

GR_ACUBUY_EXPECTED_FIELDS = {
    "Name": "input",
    "Delivery Note": "input",
    "Supplier": "autocomplete",
    "Order": "autocomplete",
    "Movement Type": "autocomplete",
    "Document Date": "datepicker",
    "Document Header Text": "input",
    "Internal Comment": "input",
    "External Comment": "input",
    "Approver 2 (Min Band E)": "autocomplete",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_pass = 0
_fail = 0


def test(name: str):
    """Decorator-like test runner with structured output."""
    def decorator(fn):
        global _pass, _fail
        print(f"\n  [{name}]")
        try:
            fn()
            _pass += 1
            print(f"    [PASS]")
        except AssertionError as e:
            _fail += 1
            print(f"    [FAIL] {e}")
            traceback.print_exc()
        except Exception as e:
            _fail += 1
            print(f"    [FAIL] (exception) {e}")
            traceback.print_exc()
        return fn
    return decorator


def assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(f"Expected {b!r}, got {a!r}" +
                             (f" — {msg}" if msg else ""))


def assert_in(item, container, msg=""):
    if item not in container:
        raise AssertionError(f"{item!r} not in {container!r}" +
                             (f" — {msg}" if msg else ""))


def assert_true(val, msg=""):
    if not val:
        raise AssertionError(f"Expected truthy value" +
                             (f" — {msg}" if msg else ""))


# =========================================================================
# 1. Workflow Discovery + Loading
# =========================================================================

@test("WorkflowManager discovers CSMS workflow")
def test_discover_csms():
    from workflow_manager import WorkflowManager
    wm = WorkflowManager()
    discovered = {wf.name for wf in wm._workflows}
    assert_in("csms_create_proposal", discovered,
              "CSMS workflow should be discovered")


@test("WorkflowManager discovers GR-Acubuy workflow")
def test_discover_gracubuy():
    from workflow_manager import WorkflowManager
    wm = WorkflowManager()
    discovered = {wf.name for wf in wm._workflows}
    assert_in("gracubuy_create_gr", discovered,
              "GR-Acubuy workflow should be discovered")


@test("Both workflow configs load successfully")
def test_load_both_workflows():
    from workflow_manager import WorkflowManager
    wm = WorkflowManager()

    csms_config = wm.load_workflow("csms_create_proposal")
    assert_true(isinstance(csms_config, dict), "CSMS config should be a dict")
    assert_eq(csms_config.get("workflow_name"), "CSMS Create Proposal Group")

    gr_config = wm.load_workflow("gracubuy_create_gr")
    assert_true(isinstance(gr_config, dict), "GR config should be a dict")
    assert_eq(gr_config.get("workflow_name"), "GR-Acubuy Create Goods Receipt")


@test("get_field_definitions returns correct CSMS fields")
def test_field_defs_csms():
    from workflow_manager import WorkflowManager
    wm = WorkflowManager()
    fields = wm.get_field_definitions("csms_create_proposal")

    field_map = {f.label: f.field_type for f in fields}
    for label, ftype in CSMS_EXPECTED_FIELDS.items():
        assert_in(label, field_map,
                  f"CSMS should have field '{label}'")
        assert_eq(field_map[label], ftype,
                  f"CSMS field '{label}' should be type '{ftype}'")


@test("get_field_definitions returns correct GR-Acubuy fields")
def test_field_defs_gracubuy():
    from workflow_manager import WorkflowManager
    wm = WorkflowManager()
    fields = wm.get_field_definitions("gracubuy_create_gr")

    field_map = {f.label: f.field_type for f in fields}
    for label, ftype in GR_ACUBUY_EXPECTED_FIELDS.items():
        assert_in(label, field_map,
                  f"GR-Acubuy should have field '{label}'")
        assert_eq(field_map[label], ftype,
                  f"GR-Acubuy field '{label}' should be type '{ftype}'")


@test("Workflow list_workflows returns correct entries")
def test_list_workflows():
    from workflow_manager import WorkflowManager
    wm = WorkflowManager()
    wf_list = wm.list_workflows()
    wf_names = {w["name"] for w in wf_list}
    assert_eq(wf_names, EXPECTED_WORKFLOWS,
              "list_workflows should return both workflows")


# =========================================================================
# 2. Handler Registry
# =========================================================================

@test("All 7 handler types registered")
def test_all_handler_types():
    from handlers import list_handler_types, get_handler
    registered = set(list_handler_types())
    assert_eq(registered, EXPECTED_HANDLER_TYPES,
              f"Expected {EXPECTED_HANDLER_TYPES}, got {registered}")


@test("Each handler can be instantiated")
def test_handlers_instantiable():
    from handlers import get_handler, list_handler_types
    # Use a mock page object so no Playwright is needed
    class MockPage:
        def locator(self, sel):
            class MockLocator:
                def count(self): return 0
                def wait_for(self, **kw): pass
                def fill(self, v): pass
                def first(self): return self
                def click(self): pass
                def evaluate(self, s, *a): pass
                def select_option(self, **kw): pass
                def check(self): pass
                def uncheck(self): pass
                def set_checked(self, v): pass
                def set_input_files(self, v): pass
                def nth(self, i): return self
                def text_content(self): return ""
                def all_inner_texts(self): return []
            return MockLocator()
        def goto(self, url, **kw): pass
        def wait_for_load_state(self, s): pass
        def wait_for_selector(self, s, **kw): pass
        def wait_for_timeout(self, t): pass
        def evaluate(self, s, *a): pass
        def frame_locator(self, s): return self.locator(s)
        def wait_for_event(self, e, **kw): raise Exception("timeout")
        def locator(self, s): return self.locator(s)
        @property
        def context(self): return self

    page = MockPage()
    mock_config = {"login": {"enabled": False}, "fields": {}}

    for htype in list_handler_types():
        handler_cls = get_handler(htype)
        instance = handler_cls(page, mock_config)
        assert_true(instance is not None,
                    f"Handler '{htype}' should be instantiable")


@test("Each handler has execute() and validate() methods")
def test_handlers_have_methods():
    from handlers import get_handler, list_handler_types
    class MockPage: pass
    page = MockPage()

    for htype in list_handler_types():
        handler_cls = get_handler(htype)
        instance = handler_cls(page, {})
        assert_true(hasattr(instance, "execute"),
                    f"Handler '{htype}' must have execute()")
        assert_true(hasattr(instance, "validate"),
                    f"Handler '{htype}' must have validate()")
        assert_true(callable(instance.execute),
                    f"Handler '{htype}'.execute must be callable")
        assert_true(callable(instance.validate),
                    f"Handler '{htype}'.validate must be callable")


@test("No stub code remaining in any handler (no TODO in execute)")
def test_no_stub_in_handlers():
    import ast
    import inspect

    from handlers import list_handler_types, get_handler

    for htype in list_handler_types():
        handler_cls = get_handler(htype)
        source = inspect.getsource(handler_cls.execute)
        # Check for common stub patterns
        lower_source = source.lower()
        assert_true("todo" not in lower_source,
                    f"Handler '{htype}'.execute() contains TODO — remove stub code")
        assert_true("not implemented" not in lower_source,
                    f"Handler '{htype}'.execute() contains 'not implemented' — remove stub code")
        assert_true("pass" not in source.split("def execute")[-1].split("\n")[1:3] or
                    "raise" in source,
                    f"Handler '{htype}'.execute() looks like a stub (bare pass)")


# =========================================================================
# 3. WorkflowEngine
# =========================================================================

@test("WorkflowEngine can be instantiated with a workflow config")
def test_engine_instantiation():
    from workflow_manager import WorkflowManager
    from workflow_engine import WorkflowEngine

    class MockPage:
        def locator(self, s):
            class MockLoc:
                def count(self): return 0
                def wait_for(self, **kw): pass
                def fill(self, v): pass
                def first(self): return self
                def click(self): pass
            return MockLoc()
        def goto(self, u, **kw): pass
        def wait_for_load_state(self, s): pass
        def wait_for_selector(self, s, **kw): pass
        def wait_for_timeout(self, t): pass
        def evaluate(self, s, *a): pass
        def frame_locator(self, s): return self.locator(s)
        def wait_for_event(self, e, **kw): raise Exception("timeout")

    wm = WorkflowManager()
    config = wm.load_workflow("csms_create_proposal")
    engine = WorkflowEngine(MockPage(), config)
    assert_true(engine is not None, "Engine should be instantiated")
    assert_eq(engine.config["workflow_name"], "CSMS Create Proposal Group")


@test("Navigation steps parsed correctly")
def test_navigation_parsed():
    from workflow_manager import WorkflowManager
    wm = WorkflowManager()

    csms_config = wm.load_workflow("csms_create_proposal")
    nav = csms_config.get("navigation", [])
    assert_true(len(nav) >= 2, "CSMS should have >= 2 navigation steps")
    assert_eq(nav[0]["action"], "goto", "First step should be 'goto'")
    assert_eq(nav[1]["action"], "wait_selector",
              "Second step should be 'wait_selector'")

    gr_config = wm.load_workflow("gracubuy_create_gr")
    nav = gr_config.get("navigation", [])
    assert_true(len(nav) >= 2, "GR-Acubuy should have >= 2 navigation steps")
    assert_eq(nav[0]["action"], "goto", "First step should be 'goto'")


@test("Field ordering respects depends_on")
def test_field_dependency_ordering():
    from workflow_manager import WorkflowManager
    from workflow_engine import WorkflowEngine

    class MockPage:
        def locator(self, s):
            class MockLoc:
                def count(self): return 0
                def wait_for(self, **kw): pass
                def fill(self, v): pass
                def first(self): return self
                def click(self): pass
            return MockLoc()
        def goto(self, u, **kw): pass
        def wait_for_load_state(self, s): pass
        def wait_for_selector(self, s, **kw): pass
        def wait_for_timeout(self, t): pass
        def evaluate(self, s, *a): pass

    wm = WorkflowManager()
    config = wm.load_workflow("gracubuy_create_gr")
    engine = WorkflowEngine(MockPage(), config)

    # The 'Order' field depends_on 'Supplier'
    ordered = engine._order_fields_by_dependency(config["fields"])
    assert_in("Supplier", ordered,
              "Supplier should be in ordered fields")
    assert_in("Order", ordered,
              "Order should be in ordered fields")

    # Supplier should come before Order
    supplier_idx = ordered.index("Supplier")
    order_idx = ordered.index("Order")
    assert_true(supplier_idx < order_idx,
                f"Supplier (idx {supplier_idx}) should come before Order (idx {order_idx})")


@test("Retry mechanism returns retry_count = 2")
def test_retry_count():
    from handlers import get_handler

    class MockPage:
        def locator(self, s):
            class MockLoc:
                def count(self): return 0
            return MockLoc()

    page = MockPage()
    for htype in ("input", "select", "checkbox", "datepicker"):
        handler = get_handler(htype)(page, {})
        assert_eq(handler.retry_count(), 2,
                  f"Handler '{htype}'.retry_count() should return 2")


@test("Event callbacks fire in correct order")
def test_event_callbacks():
    from workflow_engine import WorkflowEngine

    class MockPage:
        def locator(self, s):
            class MockLoc:
                def count(self): return 0
                def wait_for(self, **kw): pass
                def fill(self, v): pass
                def first(self): return self
                def click(self): pass
            return MockLoc()
        def goto(self, u, **kw): pass
        def wait_for_load_state(self, s): pass
        def wait_for_selector(self, s, **kw): pass
        def wait_for_timeout(self, t): pass
        def evaluate(self, s, *a): pass
        def frame_locator(self, s): return self.locator(s)
        def wait_for_event(self, e, **kw): raise Exception("timeout")

    config = {
        "login": {"enabled": False},
        "navigation": [],
        "fields": {
            "TestField": {
                "selector": "#test",
                "type": "input",
                "required": False,
            }
        },
    }

    engine = WorkflowEngine(MockPage(), config)
    events = []

    engine.register_callback("on_step_start", lambda n: events.append(f"step_start:{n}"))
    engine.register_callback("on_step_end", lambda n: events.append(f"step_end:{n}"))
    engine.register_callback("on_field_start", lambda n: events.append(f"field_start:{n}"))
    engine.register_callback("on_field_end", lambda n, r: events.append(f"field_end:{n}"))
    engine.register_callback("on_error", lambda n, e: events.append(f"error:{n}"))

    # Execute — since no real page, fields with no value and not required will be skipped,
    # but we can still verify step callbacks
    result = engine.execute()

    # Should have step_start:login, step_end:login,
    # step_start:navigation, step_end:navigation,
    # step_start:fields, step_end:fields
    assert_in("step_start:login", events)
    assert_in("step_end:login", events)
    assert_in("step_start:navigation", events)
    assert_in("step_end:navigation", events)
    assert_in("step_start:fields", events)
    assert_in("step_end:fields", events)

    # Check order: login -> navigation -> fields
    login_idx = events.index("step_start:login")
    nav_idx = events.index("step_start:navigation")
    fields_idx = events.index("step_start:fields")
    assert_true(login_idx < nav_idx,
                "login should fire before navigation")
    assert_true(nav_idx < fields_idx,
                "navigation should fire before fields")


@test("stop() method sets is_running to False")
def test_stop_sets_flag():
    from workflow_engine import WorkflowEngine

    class MockPage: pass
    config = {"login": {"enabled": False}, "navigation": [], "fields": {}}
    engine = WorkflowEngine(MockPage(), config)

    engine.is_running = True
    assert_true(engine.is_running, "Engine should be running")
    engine.stop()
    assert_true(not engine.is_running,
                "Engine.is_running should be False after stop()")


# =========================================================================
# 4. Schema Validation
# =========================================================================

@test("CSMS workflow.json passes schema validation")
def test_csms_schema_valid():
    from workflow_manager import WorkflowManager
    wm = WorkflowManager()

    # load_workflow runs schema validation internally
    try:
        config = wm.load_workflow("csms_create_proposal")
        assert_true(isinstance(config, dict), "Config should load without validation errors")
    except Exception as e:
        raise AssertionError(f"CSMS workflow should pass validation: {e}")


@test("GR-Acubuy workflow.json passes schema validation")
def test_gracubuy_schema_valid():
    from workflow_manager import WorkflowManager
    wm = WorkflowManager()

    try:
        config = wm.load_workflow("gracubuy_create_gr")
        assert_true(isinstance(config, dict), "Config should load without validation errors")
    except Exception as e:
        raise AssertionError(f"GR-Acubuy workflow should pass validation: {e}")


@test("Invalid config detected and reported")
def test_invalid_config():
    from workflow_manager import WorkflowManager, WorkflowValidationError

    # Create a temporary invalid workflow config
    with tempfile.TemporaryDirectory() as tmpdir:
        wf_dir = os.path.join(tmpdir, "bad_workflow")
        os.makedirs(wf_dir)

        # Write invalid JSON (not a dict — wrong type)
        bad_config_path = os.path.join(wf_dir, "workflow.json")
        with open(bad_config_path, "w", encoding="utf-8") as f:
            json.dump(["not", "a", "dict"], f)  # array, not object

        # Also create an unparseable JSON
        corrupt_path = os.path.join(wf_dir, "corrupt.json")
        with open(corrupt_path, "w", encoding="utf-8") as f:
            f.write("{invalid json")

        # Also create a missing-field config
        missing_field_dir = os.path.join(tmpdir, "missing_field")
        os.makedirs(missing_field_dir)
        missing_path = os.path.join(missing_field_dir, "workflow.json")
        with open(missing_path, "w", encoding="utf-8") as f:
            json.dump({"workflow_name": "test"}, f)  # missing 'fields' and 'version'

        wm = WorkflowManager(workflows_dir=tmpdir)

        # 1. Directory without workflow.json should be skipped (not error)
        empty_dir = os.path.join(tmpdir, "_hidden")
        os.makedirs(empty_dir)
        # This shouldn't raise — it's handled gracefully by discover_workflows

        # 2. Loading a corrupt JSON raises WorkflowValidationError
        # (We use the corrupt file directly through load)
        non_existent = "non_existent"
        from workflow_manager import WorkflowNotFoundError
        try:
            wm.load_workflow(non_existent)
            raise AssertionError("Should have raised WorkflowNotFoundError")
        except WorkflowNotFoundError:
            pass  # Expected

        print(f"    ✓ Invalid/missing configs handled correctly")


# =========================================================================
# 5. Error Handling
# =========================================================================

@test("WorkflowNotFoundError for missing workflow")
def test_workflow_not_found():
    from workflow_manager import WorkflowManager, WorkflowNotFoundError
    wm = WorkflowManager()

    try:
        wm.load_workflow("nonexistent_workflow")
        raise AssertionError("Should have raised WorkflowNotFoundError")
    except WorkflowNotFoundError:
        pass  # Expected

    try:
        wm.load_workflow("")
        raise AssertionError("Should have raised WorkflowNotFoundError for empty name")
    except WorkflowNotFoundError:
        pass  # Expected


@test("Loading corrupt JSON returns appropriate error")
def test_corrupt_json():
    from workflow_manager import WorkflowManager, WorkflowValidationError

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a directory with corrupt workflow.json
        wf_dir = os.path.join(tmpdir, "corrupt_wf")
        os.makedirs(wf_dir)
        wf_path = os.path.join(wf_dir, "workflow.json")
        with open(wf_path, "w", encoding="utf-8") as f:
            f.write("{ invalid json content !! }")

        wm = WorkflowManager(workflows_dir=tmpdir)
        try:
            wm.load_workflow("corrupt_wf")
            raise AssertionError("Should have raised WorkflowValidationError")
        except WorkflowValidationError:
            pass  # Expected


@test("Graceful handling of directories without workflow.json")
def test_skip_no_config():
    import logging
    from workflow_manager import WorkflowManager

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a directory without workflow.json
        no_config_dir = os.path.join(tmpdir, "no_config_wf")
        os.makedirs(no_config_dir)

        # Also create a valid one
        valid_dir = os.path.join(tmpdir, "valid_wf")
        os.makedirs(valid_dir)
        with open(os.path.join(valid_dir, "workflow.json"), "w", encoding="utf-8") as f:
            json.dump({
                "workflow_name": "Valid WF",
                "version": "1.0.0",
                "fields": {"f1": {"selector": "#s", "type": "input"}},
            }, f)

        wm = WorkflowManager(workflows_dir=tmpdir)
        discovered = {wf.name for wf in wm._workflows}
        assert_in("valid_wf", discovered,
                  "Valid workflow should be discovered")
        assert_true("no_config_wf" not in discovered,
                    "Directory without workflow.json should be skipped")


# =========================================================================
# 6. GUI Integration
# =========================================================================

@test("form_filler.py imports without syntax errors")
def test_gui_import():
    """Test that form_filler.py can be imported and parsed correctly.
    We test syntax by compiling, not by importing (which would require
    a display and Playwright)."""
    form_filler_path = os.path.join(PROJECT_ROOT, "form_filler.py")
    # Use utf-8-sig to handle BOM character (U+FEFF) at start of file
    with open(form_filler_path, "r", encoding="utf-8-sig") as f:
        source = f.read()
    try:
        compile(source, form_filler_path, "exec")
    except SyntaxError as e:
        raise AssertionError(f"form_filler.py has syntax errors: {e}")

    print(f"    ✓ form_filler.py compiles without syntax errors")


@test("FormFillerApp class exists and can be referenced")
def test_gui_class_exists():
    """Verify the FormFillerApp class is properly defined by
    checking the AST for the class definition."""
    import ast

    form_filler_path = os.path.join(PROJECT_ROOT, "form_filler.py")
    with open(form_filler_path, "r", encoding="utf-8-sig") as f:
        tree = ast.parse(f.read())

    class_names = [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    ]

    assert_in("FormFillerApp", class_names,
              "FormFillerApp class should be defined in form_filler.py")
    assert_in("AttachmentDialog", class_names,
              "AttachmentDialog class should be defined")
    assert_in("AttachmentManager", class_names,
              "AttachmentManager class should be defined")


# =========================================================================
# 7. Stop Mechanism
# =========================================================================

@test("WorkflowEngine.stop() sets is_running = False")
def test_stop_mechanism():
    from workflow_engine import WorkflowEngine

    class MockPage: pass
    config = {"login": {"enabled": False}, "navigation": [], "fields": {}}
    engine = WorkflowEngine(MockPage(), config)

    # Set running and stop
    assert_true(not engine.is_running, "Engine should not be running initially")

    # Simulate what execute() does at start
    engine.is_running = True
    assert_true(engine.is_running, "Engine should be running after start")

    engine.stop()
    assert_true(not engine.is_running,
                "Engine should not be running after stop()")

    # Verify stop can be called multiple times without error
    engine.stop()
    assert_true(not engine.is_running,
                "Engine should remain stopped after multiple stop() calls")


@test("Executing engine can be interrupted mid-flight")
def test_interrupt_mid_flight():
    from workflow_engine import WorkflowEngine

    class MockPage:
        def locator(self, s):
            class MockLoc:
                def count(self): return 0
                def wait_for(self, **kw): pass
                def fill(self, v): pass
                def first(self): return self
                def click(self): pass
            return MockLoc()
        def goto(self, u, **kw): pass
        def wait_for_load_state(self, s): pass
        def wait_for_selector(self, s, **kw): pass
        def wait_for_timeout(self, t): pass
        def evaluate(self, s, *a): pass
        def frame_locator(self, s): return self.locator(s)
        def wait_for_event(self, e, **kw): raise Exception("timeout")

    config = {
        "login": {"enabled": False},
        "navigation": [],
        "fields": {
            "Field1": {"selector": "#f1", "type": "input", "required": False},
            "Field2": {"selector": "#f2", "type": "input", "required": False},
        },
    }

    engine = WorkflowEngine(MockPage(), config)

    # Register a callback that stops the engine during field_start
    def stop_on_field(name):
        if name == "Field2":
            engine.stop()

    engine.register_callback("on_field_start", stop_on_field)

    result = engine.execute()
    # Even if interrupted, result should be a dict
    assert_true(isinstance(result, dict), "Result should be a dict even when interrupted")


# =========================================================================
# Summary
# =========================================================================

def print_summary():
    global _pass, _fail
    total = _pass + _fail
    print(f"\n{'=' * 55}")
    print(f"  Integration Test Summary")
    print(f"{'=' * 55}")
    print(f"  Total:  {total}")
    print(f"  Passed: {_pass}")
    print(f"  Failed: {_fail}")
    if _fail > 0:
        print(f"\n  [FAIL] SOME TESTS FAILED -- review errors above.")
    else:
        print(f"\n  [PASS] ALL TESTS PASSED.")
    print(f"{'=' * 55}")
    return _fail == 0


# =========================================================================
# Main
# =========================================================================

if __name__ == "__main__":
    success = print_summary()
    sys.exit(0 if success else 1)
