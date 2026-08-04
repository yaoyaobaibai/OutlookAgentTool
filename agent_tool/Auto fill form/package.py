# -*- coding: utf-8 -*-
"""Package FormFiller.exe + workflows + configs + docs into a versioned ZIP.

Standalone release script. Assumes build.py already produced dist/FormFiller.exe.

Usage:
    python package.py                       # build + package + verify
    python package.py --no-build            # skip build.py (assume dist/ ready)
    python package.py --exclude-test        # exclude *_test workflows
    python package.py --version 1.3.5       # override auto-detected version
    python package.py --output-dir C:\\Temp  # ZIP output directory
    python package.py --no-verify           # skip ZIP content check
    python package.py --verbose             # show per-file details
    python package.py --help                # show usage
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
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
# Noise filters (mirroring build.py refactor)
# ---------------------------------------------------------------------------

def _is_noise_dir(name: str) -> bool:
    """True for directories we never ship (caches, VCS, hidden)."""
    return name in ("__pycache__", ".git") or name.startswith(".")


def _is_noise_file(name: str) -> bool:
    """True for files we never ship (caches, backups, temp, macOS junk)."""
    if name in ("__pycache__", ".DS_Store", ".gitkeep"):
        return True
    return name.endswith((".pyc", ".pyo", ".bak", ".tmp"))


# ---------------------------------------------------------------------------
# Step functions
# ---------------------------------------------------------------------------

def run_build(root_dir: str, exclude_test: bool, verbose: bool) -> None:
    """Run build.py as a subprocess to regenerate dist/."""
    cmd = [sys.executable, "build.py"]
    if exclude_test:
        cmd.append("--exclude-test")
    if verbose:
        _info(f"Running: {' '.join(cmd)}")

    result = subprocess.run(
        cmd, cwd=root_dir, check=False, creationflags=CREATION_FLAGS,
    )
    if result.returncode != 0:
        _fail(f"build.py failed with exit code {result.returncode}")
        sys.exit(1)
    _ok("build.py completed")


def copy_docs(root_dir: str, verbose: bool) -> None:
    """Copy README / 使用说明 / 更新说明_* into dist/.

    Only copies files that actually exist; missing docs are warnings,
    not errors.
    """
    docs = [
        ("README.md", "README.md"),
        ("使用说明.txt", "使用说明.txt"),
    ]
    # Auto-detect update notes (e.g. 更新说明_v1.3.md)
    try:
        for fn in sorted(os.listdir(root_dir)):
            if fn.startswith("更新说明_v") and fn.endswith(".md"):
                docs.append((fn, fn))
                break
    except OSError:
        pass

    for src_name, dst_name in docs:
        src = os.path.join(root_dir, src_name)
        dst = os.path.join(root_dir, "dist", dst_name)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            _ok(f"Copied doc: {dst_name}")
        else:
            _warn(f"Doc not found: {src_name}")


def detect_version(root_dir: str) -> str:
    """Auto-detect version from form_filler.py or build.py.

    Priority:
      1. `__version__ = "X.Y.Z"` in source
      2. `# Version: X.Y.Z` comment
      3. `version = "X.Y.Z"` argument
      4. git short SHA (fallback)
      5. "0.0.0" (last resort)
    """
    candidates = [
        os.path.join(root_dir, "form_filler.py"),
        os.path.join(root_dir, "build.py"),
    ]
    patterns = [
        r'__version__\s*=\s*["\']([\d.]+)["\']',
        r'#\s*Version:\s*([\d.]+)',
        r'version\s*=\s*["\']([\d.]+)["\']',
    ]
    for path in candidates:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            for pattern in patterns:
                m = re.search(pattern, content)
                if m:
                    return m.group(1)
        except (OSError, UnicodeDecodeError):
            continue

    # Fallback: git short SHA
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root_dir, text=True, stderr=subprocess.DEVNULL,
        ).strip()
        if sha:
            return f"git-{sha}"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return "0.0.0"


def create_zip(
    source_dir: str, zip_path: str, exclude_test: bool, verbose: bool,
) -> None:
    """Create a ZIP from source_dir with noise filtering.

    - EXE stays at ZIP top level (users double-click to run)
    - Optionally excludes *_test workflows
    - Removes a pre-existing ZIP with the same name (idempotent)
    """
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)

    if os.path.exists(zip_path):
        os.remove(zip_path)
        if verbose:
            _info(f"Removed existing: {zip_path}")

    file_count = 0
    total_size = 0
    with zipfile.ZipFile(
        zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6,
    ) as zf:
        for root, dirs, files in os.walk(source_dir):
            # Skip noise directories in-place (prunes the walk)
            dirs[:] = [d for d in dirs if not _is_noise_dir(d)]

            for fname in sorted(files):
                if _is_noise_file(fname):
                    continue

                src = os.path.join(root, fname)
                arc = os.path.relpath(src, source_dir).replace(os.sep, "/")

                # Optionally skip test workflows (e.g. workflows/_test/...)
                if exclude_test:
                    if "/_test/" in arc or arc.startswith("_test/"):
                        continue

                zf.write(src, arc)
                file_count += 1
                total_size += os.path.getsize(src)

                if verbose:
                    _info(f"  + {arc}")

    zip_size = os.path.getsize(zip_path)
    _ok(f"Created ZIP: {zip_path}")
    if total_size:
        pct = zip_size * 100.0 / total_size
        _info(
            f"  Files: {file_count}, Original: {total_size/1024:.1f} KB, "
            f"Compressed: {zip_size/1024:.1f} KB ({pct:.1f}%)"
        )
    else:
        _info(f"  Files: {file_count}, Size: {zip_size/1024:.1f} KB")


def verify_zip(zip_path: str, verbose: bool) -> None:
    """Verify ZIP structure: EXE at top level + workflows/ present."""
    required = ["FormFiller.exe", "workflows/settings.json"]
    optional = [
        "form_config.json", "attachment_config.json",
        "README.md", "使用说明.txt",
    ]

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()

    for req in required:
        if req not in names:
            _fail(f"ZIP missing required file: {req}")
            sys.exit(1)

    _ok(f"Verified ZIP contains required files: {required}")

    found_optional = [o for o in optional if o in names]
    if found_optional:
        _info(f"Optional files: {found_optional}")

    if verbose:
        _info("ZIP contents:")
        for n in sorted(names):
            _info(f"  {n}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Package FormFiller.exe + workflows + configs + docs "
                    "into a versioned ZIP for end users.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python package.py                     build + package + verify
  python package.py --no-build          skip build.py (assume dist/ ready)
  python package.py --exclude-test      exclude *_test workflows
  python package.py --version 1.3.5     override auto-detected version
  python package.py --output-dir C:\\Temp  ZIP output directory
  python package.py --verbose           show per-file packing details
""",
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Version string for ZIP name (e.g. 1.3.5). "
             "Default: auto-detect from form_filler.py / build.py",
    )
    parser.add_argument(
        "--no-build",
        dest="build",
        action="store_false",
        help="Skip running build.py (assume dist/ is already built)",
    )
    parser.add_argument(
        "--build",
        dest="build",
        action="store_true",
        help="Run build.py before packaging (default)",
    )
    parser.set_defaults(build=True)
    parser.add_argument(
        "--exclude-test",
        action="store_true",
        help="Exclude *_test workflow directories from the ZIP",
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "release_package",
        ),
        help="ZIP output directory (default: agent_tool/release_package/)",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip ZIP content verification",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show per-file packing details",
    )
    args = parser.parse_args()

    root_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"{CYAN}=== FormFiller Package ==={RESET}")
    _info(f"Project dir: {root_dir}")

    # [1] Optional build
    if args.build:
        run_build(root_dir, exclude_test=args.exclude_test, verbose=args.verbose)
    else:
        _info("build.py SKIPPED (--no-build)")

    # [2] Verify dist/FormFiller.exe exists
    exe_path = os.path.join(root_dir, "dist", "FormFiller.exe")
    if not os.path.isfile(exe_path):
        _fail(f"FormFiller.exe not found at {exe_path}. Run --build first.")
        return 1

    # [3] Copy docs into dist/
    copy_docs(root_dir, verbose=args.verbose)

    # [4] Detect version
    version = args.version or detect_version(root_dir)
    _info(f"Version: {version}")

    # [5] Create ZIP
    date_str = datetime.now().strftime("%Y%m%d")
    zip_name = f"FormFiller_v{version}_{date_str}.zip"
    zip_path = os.path.join(args.output_dir, zip_name)

    create_zip(
        source_dir=os.path.join(root_dir, "dist"),
        zip_path=zip_path,
        exclude_test=args.exclude_test,
        verbose=args.verbose,
    )

    # [6] Verify
    if not args.no_verify:
        verify_zip(zip_path, verbose=args.verbose)

    # Summary
    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"\n{CYAN}{'=' * 60}{RESET}")
    print(f"{GREEN}PACKAGE SUCCESS{RESET}")
    print(f"  ZIP:  {zip_path}")
    print(f"  Size: {size_mb:.2f} MB")
    print(f"{CYAN}{'=' * 60}{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
