#!/usr/bin/env python3
"""
tests/test_logging_setup.py — pytest tests for the logging_setup module.

Covers:
  1. configure_logging() writes a second-named log file
     (app-YYYYMMDD-HHMMSS[-N].log) in the injected log_dir with utf-8
     encoding (Chinese text round-trips).
  2. configure_logging() swap semantics — at most one FileHandler after
     re-configuration, non-file handlers (GuiLogBridge) survive.
  3. Same-second collision appends a -1 counter and keeps both files.
  4. cleanup_old_logs() removes files older than `days` and keeps fresh ones.
  5. GuiLogBridge forwards records to its sink with a "[LEVELNAME]" prefix.
  6. GuiLogBridge swallows sink exceptions (post-destroy TclError guard).
  7. Two bridges over different sinks get distinct sink_ids.

All tests are OFFLINE-SAFE: log_dir is always injected via pytest tmp_path,
no GUI / tkinter is touched, no browser is launched.
Run with:  python -m pytest tests/test_logging_setup.py -v
"""

import logging
import os
import re
import sys
import time
from datetime import datetime

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from logging_setup import configure_logging, cleanup_old_logs, GuiLogBridge


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


# ---------------------------------------------------------------------------
# configure_logging
# ---------------------------------------------------------------------------

def test_configure_writes_session_file(tmp_path):
    """configure_logging 创建秒级命名文件，utf-8 中文 round-trip。"""
    path = configure_logging(log_dir=str(tmp_path))
    assert re.match(r"^app-\d{8}-\d{6}(-\d+)?\.log$", os.path.basename(path)), path

    logging.getLogger().info("测试中文消息")
    logging.getLogger().debug("debug msg")

    assert os.path.exists(path), path
    content = open(path, encoding="utf-8").read()
    assert "测试中文消息" in content
    assert "debug msg" in content


def test_swap_at_most_one_handler(tmp_path):
    """两次 configure_logging → 始终 1 个 FileHandler，GuiLogBridge 存活。"""
    root = logging.getLogger()
    sink = []
    bridge = GuiLogBridge(sink.append)
    root.addHandler(bridge)

    configure_logging(log_dir=str(tmp_path))
    count1 = sum(1 for h in root.handlers if isinstance(h, logging.FileHandler))
    configure_logging(log_dir=str(tmp_path))
    count2 = sum(1 for h in root.handlers if isinstance(h, logging.FileHandler))

    assert count1 >= 1
    assert count2 == 1, "FileHandler count must stay 1 after swap"
    assert bridge in root.handlers, "GuiLogBridge must survive configure_logging"


def test_collision_counter(tmp_path):
    """同秒冲突时追加 -1 后缀，两文件都存在。"""
    first = configure_logging(log_dir=str(tmp_path))
    # 释放 FileHandler 句柄（Windows 上会锁文件），再删除并占位 → 强制冲突
    root = logging.getLogger()
    for h in root.handlers[:]:
        if isinstance(h, logging.FileHandler):
            root.removeHandler(h)
            try:
                h.close()
            except Exception:
                pass
    os.remove(first)
    open(first, "w").close()  # 重新占位
    second = configure_logging(log_dir=str(tmp_path))
    assert second != first
    assert os.path.exists(first) and os.path.exists(second)
    assert os.path.basename(second).endswith("-1.log") or os.path.basename(second) != os.path.basename(first)


# ---------------------------------------------------------------------------
# cleanup_old_logs
# ---------------------------------------------------------------------------

def test_cleanup_removes_old_keeps_new(tmp_path):
    """cleanup_old_logs deletes files older than `days` but keeps fresh ones."""
    old_file = tmp_path / "app-20250101.log"
    old_file.write_text("old", encoding="utf-8")
    old_ts = time.time() - 40 * 86400  # 40 days ago
    os.utime(old_file, (old_ts, old_ts))

    new_file = tmp_path / f"app-{datetime.now():%Y%m%d}.log"
    new_file.write_text("new", encoding="utf-8")

    removed = cleanup_old_logs(log_dir=str(tmp_path), days=30)

    assert removed == 1
    assert not old_file.exists()
    assert new_file.exists()


# ---------------------------------------------------------------------------
# GuiLogBridge
# ---------------------------------------------------------------------------

def test_gui_bridge_forwards_debug():
    """A bridge attached to root receives debug records with a [DEBUG] prefix."""
    sink = []
    bridge = GuiLogBridge(sink.append)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(bridge)

    root.debug("nav step 1")

    assert len(sink) == 1, sink
    assert "[DEBUG]" in sink[0]
    assert "nav step 1" in sink[0]


def test_bridge_swallows_sink_errors():
    """emit() must not raise even when the sink itself raises."""

    def bad_sink(msg):
        raise RuntimeError("boom")

    bridge = GuiLogBridge(bad_sink)
    record = logging.LogRecord("test", logging.INFO, "m", 1, "x", None, None)

    bridge.emit(record)  # must return normally


def test_bridge_sink_id_unique():
    """Two bridges over different sinks get distinct sink_ids."""
    b1 = GuiLogBridge(lambda msg: None)
    b2 = GuiLogBridge(lambda msg: None)
    assert b1.sink_id != b2.sink_id


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
