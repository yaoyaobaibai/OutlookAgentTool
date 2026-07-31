# -*- coding: utf-8 -*-
"""Build Recorder.exe with PyInstaller --onefile.

Mirrors agent_tool/Auto fill form/build.py structure.

Usage:
    python build_recorder.py            # standard build (clean + build + verify + smoke)
    python build_recorder.py --no-clean # skip cleanup
    python build_recorder.py --no-test  # skip smoke test
    python build_recorder.py --verbose   # show pyinstaller stdout in real-time
"""

import argparse
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


def _kill_processes(name: str = "Recorder") -> None:
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
# Main build function
# ---------------------------------------------------------------------------

def build(args: argparse.Namespace) -> int:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)
    # Total steps: 4 (preflight) + cleanup + build + verify + smoke
    total_steps = 4
    if not args.no_clean:
        total_steps += 1
    total_steps += 1  # build
    total_steps += 1  # verify
    if not args.no_test:
        total_steps += 1  # smoke

    mode_str = "console visible" if args.console else "console hidden (windowed)"
    print(f"{CYAN}=== Recorder.exe Build ({mode_str}) ==={RESET}")
    _info(f"Project dir: {root_dir}")

    # =======================================================================
    # [1] Pre-flight checks
    # =======================================================================
    step = 1
    _step_header(step, total_steps, "Pre-flight checks")
    step += 1

    # 1a. Verify recorder.py exists
    recorder_py = os.path.join(root_dir, "recorder.py")
    if not os.path.isfile(recorder_py):
        _fail(f"recorder.py not found at {recorder_py}")
        _fail("Are you running from agent_tool/Auto fill form/?")
        return 1
    _ok("recorder.py found")

    # 1b. Verify PyInstaller importable
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

    # 1c. Verify Playwright importable (use importlib.metadata since playwright.__version__ may not exist)
    try:
        result = subprocess.run(
            [sys.executable, "-c",
             "import importlib.metadata; print(importlib.metadata.version('playwright'))"],
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

    # 1d. Kill existing Recorder processes
    _kill_processes("Recorder")
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
    _step_header(step, total_steps, "Building Recorder.exe")
    step += 1

    # Build PyInstaller command
    pyi_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "Recorder",
        "--paths", ".",
    ]

    # --windowed is mutually exclusive with --console (default is console visible)
    if not args.console:
        pyi_cmd.append("--windowed")

    pyi_cmd.extend([
        "--hidden-import=tkinter",
        "--hidden-import=playwright.async_api",
        "--hidden-import=playwright._impl._driver",
        "--hidden-import=playwright._impl._registry",
        "--collect-all=playwright",
        "recorder.py",
    ])

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
        exe_path = os.path.join(root_dir, "dist", "Recorder.exe")
    else:
        exe_path = os.path.join(root_dir, "dist", "Recorder")

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

    if size_mb < 80:
        _warn(f"Size {size_mb:.2f} MB < 80 MB -- Playwright may not be bundled")
    elif size_mb > 100:
        _warn(f"Size {size_mb:.2f} MB > 100 MB -- unexpected bloat?")
    else:
        _ok("Size within expected 80-100 MB range")

    # =======================================================================
    # [5] Optional smoke test
    # =======================================================================
    if not args.no_test:
        _step_header(step, total_steps, "Smoke test")
        step += 1

        # Ensure no Recorder.exe running
        _kill_processes("Recorder")
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
            _kill_processes("Recorder")
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
        description="Build Recorder.exe with PyInstaller --onefile",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python build_recorder.py                  default: console visible (Python window shown)
  python build_recorder.py --windowed        console hidden (no Python window)
  python build_recorder.py --no-clean       skip cleanup (incremental)
  python build_recorder.py --no-test        skip smoke test
  python build_recorder.py --verbose        show pyinstaller stdout in real-time
""",
    )
    parser.add_argument(
        "--console",
        action="store_true",
        default=True,
        help="Show Python console window when EXE runs (default: enabled)",
    )
    parser.add_argument(
        "--windowed",
        dest="console",
        action="store_false",
        help="Hide Python console window (equivalent to --no-console)",
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
        "--verbose",
        action="store_true",
        help="Show PyInstaller stdout/stderr in real-time",
    )
    args = parser.parse_args()
    exit_code = build(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
