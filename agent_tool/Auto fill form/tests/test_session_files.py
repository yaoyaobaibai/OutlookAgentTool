#!/usr/bin/env python3
"""
tests/test_session_files.py — session-level E2E contract for logging_setup.

Verifies that two successive execution sessions produce two distinct log
files (second-level names), each containing its own session marker, and
that at most one FileHandler is attached to the root logger after the
second session starts.

OFFLINE-SAFE: log_dir is injected via pytest tmp_path, no GUI / tkinter is
touched, no browser is launched.
Run with:  python -m pytest tests/test_session_files.py -v
"""

import logging
import os
import sys
import time

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logging_setup import configure_logging, flush_file_handler


@pytest.fixture(autouse=True)
def _reset_root_logger():
    """Restore the root logger after every test to avoid cross-test pollution.

    - Closes any handlers added during the test (releases file handles so
      Windows does not keep the log file locked).
    - Restores the original handler list and level.
    """
    root = logging.getLogger()
    before_handlers = root.handlers[:]
    before_level = root.level
    yield
    for handler in root.handlers[:]:
        if handler not in before_handlers:
            try:
                handler.close()
            except Exception:
                pass
    root.handlers = before_handlers  # restore original handlers
    root.setLevel(before_level)      # restore original level


def test_two_sessions_two_files(tmp_path):
    """两次执行会话 → 两个不同日志文件，各自含自己的会话标记。"""
    # 会话 1
    p1 = configure_logging(log_dir=str(tmp_path))
    logging.getLogger().info("=== 会话开始: demo1 ===")
    flush_file_handler()
    # 强制不同秒
    time.sleep(1.1)
    # 会话 2
    p2 = configure_logging(log_dir=str(tmp_path))
    logging.getLogger().info("=== 会话开始: demo2 ===")
    flush_file_handler()

    assert p1 != p2
    assert os.path.exists(p1) and os.path.exists(p2)
    c1 = open(p1, encoding="utf-8").read()
    c2 = open(p2, encoding="utf-8").read()
    assert "=== 会话开始: demo1 ===" in c1
    assert "=== 会话开始: demo2 ===" in c2
    # 第一个文件内容未被截断（会话1标记仍在）
    assert "demo1" in c1
    # 最多 1 个 FileHandler
    root = logging.getLogger()
    fh = [h for h in root.handlers if isinstance(h, logging.FileHandler)]
    assert len(fh) == 1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
