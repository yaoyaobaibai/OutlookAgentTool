# -*- coding: utf-8 -*-
"""Build FormFiller.exe with PyInstaller --onefile.

Mirrors agent_tool/pr_po_agent/build.py structure.

Usage:
    python build.py              # standard build (clean + build + verify + smoke)
    python build.py --no-clean   # skip cleanup
    python build.py --no-test    # skip smoke test
    python build.py --exclude-test  # skip *_test workflows when copying
    python build.py --verbose    # show pyinstaller stdout in real-time
    python build.py --help       # show usage
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime


# UTF-8 stdout/stderr (Windows cp1252 cannot encode CJK paths)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, Exception):
    # Python < 3.7 fallback
    pass


# ---------------------------------------------------------------------------
# ANSI color helpers (only used if stdout is a terminal)
# ---------------------------------------------------------------------------

def _ansi(code: str) -> str:
    return code if hasattr(sys.stdout, "isatty") and sys.stdout.isatty() else ""


RED = _ansi("\033[91m")
GREEN = _ansi("\033[92m")
YELLOW = _ansi("\033[93m")
CYAN = _ansi("\033[96m")
GRAY = _ansi("\033[90m")
RESET = _ansi("\033[0m")

IS_WINDOWS = sys.platform == "win32"

# Windows: hide subprocess console windows
CREATION_FLAGS = 0x08000000 if IS_WINDOWS else 0


# ---------------------------------------------------------------------------
# Log helpers
# ---------------------------------------------------------------------------

def _ts() -> str:
    """Timestamp for log lines."""
    return datetime.now().strftime("%H:%M:%S")


def _info(msg: str) -> None:
    print(f"{GRAY}[{_ts()}]{RESET} {msg}")


def _ok(msg: str) -> None:
    print(f"{GRAY}[{_ts()}]{RESET} {GREEN}{msg}{RESET}")


def _warn(msg: str) -> None:
    print(f"{GRAY}[{_ts()}]{RESET} {YELLOW}WARN: {msg}{RESET}")


def _fail(msg: str) -> None:
    print(f"{GRAY}[{_ts()}]{RESET} {RED}FAIL: {msg}{RESET}")


# ---------------------------------------------------------------------------
# Step helpers
# ---------------------------------------------------------------------------

def _step_header(num: int, total: int, title: str) -> None:
    print(f"\n{CYAN}[{num}/{total}] {title}...{RESET}")


def _kill_processes(name: str = "FormFiller") -> None:
    """Kill all processes with given image name (Windows only)."""
    if not IS_WINDOWS:
        _info(f"Non-Windows: skipping kill {name}.exe")
        return
    try:
        subprocess.run(
            ["taskkill", "/f", "/im", f"{name}.exe"],
            capture_output=True,
            creationflags=CREATION_FLAGS,
            check=False,
        )
    except FileNotFoundError:
        _warn(f"taskkill not found; cannot kill {name}.exe")


def _clean_dirs(root_dir: str) -> None:
    """Delete dist/, build/, __pycache__/ recursively."""
    for target in ("dist", "build"):
        path = os.path.join(root_dir, target)
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
            _info(f"Removed: {path}")

    count = 0
    for dirpath, dirnames, _ in os.walk(root_dir):
        if "__pycache__" in dirnames:
            full = os.path.join(dirpath, "__pycache__")
            shutil.rmtree(full, ignore_errors=True)
            count += 1
    if count:
        _info(f"Removed {count} __pycache__ directories")


# ---------------------------------------------------------------------------
# Workflow copy helpers
# ---------------------------------------------------------------------------

# Files/dirs to never copy into dist/workflows/ (noise filter)
_WORKFLOW_IGNORES = shutil.ignore_patterns(
    "__pycache__", "*.pyc", "*.pyo", "*.bak", "*.tmp", ".DS_Store"
)


def _is_noise(name: str) -> bool:
    """True for files we never ship (caches, backups, temp, macOS junk)."""
    return (
        name in ("__pycache__", ".DS_Store")
        or name.endswith((".pyc", ".pyo", ".bak", ".tmp"))
    )


def _validate_workflow_json(workflow_json: str, validator_py: str) -> None:
    """Validate a workflow.json against the schema. Warn on failure, never block."""
    if not os.path.isfile(validator_py):
        _warn(f"validate_workflow.py not found at {validator_py}; skipping schema check")
        return
    result = subprocess.run(
        [sys.executable, validator_py, workflow_json],
        capture_output=True,
        text=True,
        check=False,
        creationflags=CREATION_FLAGS,
    )
    if result.returncode == 0:
        _info(f"schema OK: {os.path.relpath(workflow_json, os.path.dirname(os.path.dirname(workflow_json)))}")
    else:
        _warn(f"schema validation FAILED for {workflow_json}")
        for line in result.stdout.splitlines()[-5:]:
            _info(f"  {line}")


def _copy_workflows(root_dir: str, exclude_test: bool = False) -> None:
    """Copy workflows/ into dist/workflows/ with per-workflow logging.

    - Logs each workflow dir as OK: copied workflows/<name>/ or SKIP: <reason>
    - Includes *_test workflows by default (excluded via --exclude-test)
    - Filters noise (__pycache__/, *.pyc, *.bak, *.tmp, .DS_Store)
    - Validates workflows/schema/ and workflows/settings.json exist
    - Validates each workflow.json against the schema (warn only)
    """
    workflows_src = os.path.join(root_dir, "workflows")
    workflows_dst = os.path.join(root_dir, "dist", "workflows")

    if not os.path.isdir(workflows_src):
        _warn(f"workflows/ not found at {workflows_src}")
        return

    # 7a. Validate workflows/schema/ exists (workflow_manager depends on it)
    schema_dir = os.path.join(workflows_src, "schema")
    if not os.path.isdir(schema_dir):
        _warn(f"workflows/schema/ not found at {schema_dir} -- workflow_manager needs it")
    validator_py = os.path.join(schema_dir, "validate_workflow.py")

    # 7b. Validate settings.json exists; print current_workflow
    settings_path = os.path.join(workflows_src, "settings.json")
    current_workflow = "?"
    if os.path.isfile(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                current_workflow = json.load(f).get("current_workflow", "?")
        except (OSError, ValueError) as e:
            _warn(f"Could not read settings.json: {e}")
        _ok(f"settings.json found (current_workflow: {current_workflow})")
    else:
        _warn(f"settings.json not found at {settings_path}")

    # 7c. Copy top-level non-noise files (settings.json, README.md, ...)
    os.makedirs(workflows_dst, exist_ok=True)
    for entry in sorted(os.listdir(workflows_src)):
        src = os.path.join(workflows_src, entry)
        if os.path.isfile(src) and not _is_noise(entry):
            shutil.copy2(src, os.path.join(workflows_dst, entry))
            _ok(f"OK: copied workflows/{entry}")

    # 7d. Copy each workflow directory (excluding noise)
    copied = 0
    prod_count = 0
    test_count = 0
    for name in sorted(os.listdir(workflows_src)):
        src = os.path.join(workflows_src, name)
        if not os.path.isdir(src):
            continue

        # schema/ is runtime infrastructure for workflow_manager -- copy it,
        # but it is not a workflow (no count, no per-workflow validation)
        if name == "schema":
            schema_dst = os.path.join(workflows_dst, "schema")
            try:
                shutil.copytree(src, schema_dst, dirs_exist_ok=True, ignore=_WORKFLOW_IGNORES)
                _ok("OK: copied workflows/schema/")
            except OSError as e:
                _warn(f"SKIP: workflows/schema/ (copy failed: {e})")
            continue

        # 7e. Optionally skip *_test workflows
        is_test = name.endswith("_test")
        if is_test and exclude_test:
            _info(f"SKIP: workflows/{name}/ (excluded by --exclude-test)")
            continue

        dst = os.path.join(workflows_dst, name)
        try:
            shutil.copytree(src, dst, dirs_exist_ok=True, ignore=_WORKFLOW_IGNORES)
        except OSError as e:
            _warn(f"SKIP: workflows/{name}/ (copy failed: {e})")
            continue

        _ok(f"OK: copied workflows/{name}/")
        copied += 1
        if is_test:
            test_count += 1
        else:
            prod_count += 1

        # 7f. Validate workflow.json against schema (warn on fail, don't block)
        workflow_json = os.path.join(src, "workflow.json")
        if os.path.isfile(workflow_json):
            _validate_workflow_json(workflow_json, validator_py)

    # 7g. Summary
    _ok(f"Copied {copied} workflows ({prod_count} production + {test_count} test)")


# ---------------------------------------------------------------------------
# Main build function
# ---------------------------------------------------------------------------

def build(args: argparse.Namespace) -> int:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)
    # Total steps: 4 (preflight) + cleanup + build + verify + smoke + copy configs
    total_steps = 4
    if not args.no_clean:
        total_steps += 1
    total_steps += 1  # build
    total_steps += 1  # verify
    if not args.no_test:
        total_steps += 1  # smoke
    total_steps += 1  # copy default configs
    total_steps += 1  # copy workflows/

    print(f"{CYAN}=== FormFiller.exe Build ==={RESET}")
    _info(f"Project dir: {root_dir}")

    # =======================================================================
    # [1] Pre-flight checks
    # =======================================================================
    step = 1
    _step_header(step, total_steps, "Pre-flight checks")
    step += 1

    # 1a. Verify we're in the right directory
    form_filler_py = os.path.join(root_dir, "form_filler.py")
    if not os.path.isfile(form_filler_py):
        _fail(f"form_filler.py not found at {form_filler_py}")
        _fail("Are you running from agent_tool/采购/自动填充网页表单信息/?")
        return 1
    _ok("form_filler.py found")

    # 1b. Verify PyInstaller is importable
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import PyInstaller; print(PyInstaller.__version__)"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            _fail("PyInstaller not importable")
            _fail(f"stderr: {result.stderr.strip()}")
            return 1
        version = result.stdout.strip()
        _ok(f"PyInstaller {version} available")
    except FileNotFoundError:
        _fail("Python interpreter not found")
        return 1

    # 1c. Verify Playwright is importable
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import importlib.metadata; print(importlib.metadata.version('playwright'))"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            _fail("Playwright not importable")
            _fail(f"stderr: {result.stderr.strip()}")
            return 1
        pw_version = result.stdout.strip()
        _ok(f"Playwright {pw_version} available")
    except FileNotFoundError:
        _fail("Python interpreter not found")
        return 1

    # 1d. Kill existing FormFiller processes
    _kill_processes("FormFiller")
    time.sleep(0.5)

    # =======================================================================
    # [2] Cleanup (unless --no-clean)
    # =======================================================================
    if not args.no_clean:
        _step_header(step, total_steps, "Cleanup")
        step += 1
        _clean_dirs(root_dir)
    else:
        _info("Cleanup SKIPPED (--no-clean)")

    # =======================================================================
    # [3] Build
    # =======================================================================
    _step_header(step, total_steps, "Building FormFiller.exe")
    step += 1

    # Proven PyInstaller command -- DO NOT modify flags without retesting
    pyi_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "FormFiller",
        "--paths", ".",
        "--hidden-import=tkinter",
        "--hidden-import=playwright.sync_api",
        "--hidden-import=playwright._impl._driver",
        "--hidden-import=playwright._impl._registry",
        "--collect-all=playwright",
        "form_filler.py",
    ]

    if args.verbose:
        _info(f"Command: {' '.join(pyi_cmd)}")

    _info("Running PyInstaller (this may take 1-3 minutes)...")

    if args.verbose:
        # Stream output in real-time
        process = subprocess.Popen(
            pyi_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=CREATION_FLAGS,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
        process.wait()
        exit_code = process.returncode
        captured_stdout = ""
        captured_stderr = ""
    else:
        result = subprocess.run(
            pyi_cmd,
            capture_output=True,
            text=True,
            check=False,
            creationflags=CREATION_FLAGS,
        )
        exit_code = result.returncode
        captured_stdout = result.stdout
        captured_stderr = result.stderr

    if exit_code != 0:
        _fail(f"PyInstaller exited with code {exit_code}")
        if not args.verbose:
            print(f"\n{GRAY}--- stdout (last 50 lines) ---{RESET}")
            for line in captured_stdout.splitlines()[-50:]:
                print(f"  {line}")
            if captured_stderr.strip():
                print(f"\n{GRAY}--- stderr (last 30 lines) ---{RESET}")
                for line in captured_stderr.splitlines()[-30:]:
                    print(f"  {line}")
        return exit_code

    _ok("PyInstaller completed successfully")

    # =======================================================================
    # [4] Verify EXE
    # =======================================================================
    _step_header(step, total_steps, "Verifying EXE")
    step += 1

    if IS_WINDOWS:
        exe_path = os.path.join(root_dir, "dist", "FormFiller.exe")
    else:
        exe_path = os.path.join(root_dir, "dist", "FormFiller")

    if not os.path.isfile(exe_path):
        _fail(f"EXE not found at {exe_path}")
        _fail("Check PyInstaller output above for errors")
        return 1

    size_bytes = os.path.getsize(exe_path)
    size_mb = size_bytes / (1024 * 1024)
    mtime = datetime.fromtimestamp(os.path.getmtime(exe_path))

    _ok(f"EXE:    {exe_path}")
    _ok(f"Size:   {size_mb:.2f} MB ({size_bytes:,} bytes)")
    _info(f"Time:   {mtime.strftime('%Y-%m-%d %H:%M:%S')}")

    if size_mb < 20:
        _warn(f"Size {size_mb:.2f} MB < 20 MB -- Playwright may not be bundled")
    elif size_mb > 50:
        _warn(f"Size {size_mb:.2f} MB > 50 MB -- unexpected bloat?")
    else:
        _ok("Size within expected 20-50 MB range")

    # =======================================================================
    # [5] Optional smoke test
    # =======================================================================
    if not args.no_test:
        _step_header(step, total_steps, "Smoke test")
        step += 1

        # Ensure no FormFiller.exe running
        _kill_processes("FormFiller")
        time.sleep(0.5)

        _info("Launching EXE for 10 seconds...")
        try:
            proc = subprocess.Popen(
                [exe_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=CREATION_FLAGS,
            )
        except Exception as e:
            _warn(f"Could not launch EXE: {e}")
            proc = None

        if proc is not None:
            time.sleep(10)
            # Kill the test process
            _kill_processes("FormFiller")
            time.sleep(0.5)

            # Find latest log
            log_dir = os.path.expandvars(r"%USERPROFILE%\FormFiller_logs")
            if IS_WINDOWS and os.path.isdir(log_dir):
                log_files = sorted(
                    [f for f in os.listdir(log_dir) if f.startswith("log_") and f.endswith(".log")],
                    reverse=True,
                )
                if log_files:
                    latest = os.path.join(log_dir, log_files[0])
                    _info(f"Latest log: {latest}")
                else:
                    _info("No log file found in %USERPROFILE%\\FormFiller_logs")
            else:
                _info("Log dir not found (non-Windows or first run)")

            _ok("Smoke test: EXE launched and ran for 10s. Check log for details.")
    else:
        _info("Smoke test SKIPPED (--no-test)")

    # =======================================================================
    # [6] Copy default configs to dist
    # =======================================================================
    _step_header(step, total_steps, "Copying default configs to dist")
    step += 1

    for cfg_name in ("form_config.json", "attachment_config.json"):
        src_cfg = os.path.join(root_dir, cfg_name)
        dst_cfg = os.path.join(root_dir, "dist", cfg_name)
        if os.path.isfile(src_cfg):
            shutil.copy2(src_cfg, dst_cfg)
            _ok(f"Copied: {cfg_name}")
        else:
            _info(f"Skipped (not found): {cfg_name}")

    # =======================================================================
    # [7] Copy workflows/ directory to dist (for dynamic importlib loading)
    # =======================================================================
    _step_header(step, total_steps, "Copying workflows/ directory to dist")
    step += 1

    _copy_workflows(root_dir, exclude_test=args.exclude_test)

    # =======================================================================
    # Summary
    # =======================================================================
    print(f"\n{CYAN}{'=' * 60}{RESET}")
    print(f"{GREEN}BUILD SUCCESS{RESET}")
    print(f"  EXE:  {exe_path}")
    print(f"  Size: {size_mb:.2f} MB")
    print(f"{CYAN}{'=' * 60}{RESET}")

    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build FormFiller.exe with PyInstaller --onefile",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python build.py                 standard build (clean + build + verify + smoke)
  python build.py --no-clean      skip cleanup (incremental)
  python build.py --no-test       skip smoke test
  python build.py --exclude-test  skip *_test workflows when copying
  python build.py --verbose       show pyinstaller stdout in real-time
""",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Skip pre-build cleanup (dist/, build/, __pycache__/)",
    )
    parser.add_argument(
        "--no-test",
        action="store_true",
        help="Skip post-build smoke test (launch EXE for 10s)",
    )
    parser.add_argument(
        "--exclude-test",
        action="store_true",
        help="Exclude *_test workflow directories when copying workflows/",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show PyInstaller stdout/stderr in real-time",
    )
    args = parser.parse_args()
    exit_code = build(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
