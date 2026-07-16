# -*- coding: utf-8 -*-
"""Mail Agent controller for PRPOAgent.

Mail Agent runs IN-PROCESS as a daemon thread (not a subprocess) so it
works in both source mode and PyInstaller --onefile EXE mode (where
sys.executable is the EXE itself, not a Python interpreter).

The controller pre-imports the OutlookMonitor class and passes it to
MailAgent, sidestepping the sys.path shadowing problem.

Logging is English ASCII per SKILL.md.
"""

import logging
import os
import sys
import tempfile
import threading
import time

logger = logging.getLogger(__name__)


class MailAgentFilter(logging.Filter):
    """Only accept records from mail_agent-related loggers (added 2026-07-15).

    Prevents prpo_agent_ui and other unrelated loggers from polluting
    mail_agent.log.
    """
    def filter(self, record):
        name = record.name
        return (
            name == "mail_agent"
            or name == "mail_controller"
            or name.startswith("agents.mail_agent")
            or name.startswith("agents.")
        )


def _setup_logging():
    """Configure file logging for Mail Agent (PDFMergeTool pattern).

    File: log_YYYYMMDD_HHMMSS.log
    Dir:  %USERPROFILE%/PRPOAgent_logs/
    Each app launch creates a brand-new log file (mode="w", truncated).

    MailAgentFilter (from previous fix) only allows records from
    mail_agent-related loggers to reach this file - prevents prpo_agent_ui
    messages from polluting it.
    """
    from datetime import datetime

    log_dir = os.path.expandvars(os.path.expanduser(r"%USERPROFILE%/PRPOAgent_logs"))
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        log_dir = os.path.join(tempfile.gettempdir(), "PRPOAgent_logs")
        os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"log_{timestamp}.log")
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    fmt = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s: %(message)s"
    )
    try:
        fh = logging.FileHandler(log_file, encoding="utf-8", mode="w")
        fh.setFormatter(fmt)
        # Filter out non-mail_agent records
        fh.addFilter(MailAgentFilter())
        root.addHandler(fh)
    except Exception as e:
        sys.stderr.write("Failed to set up Mail Agent log: %s\n" % e)


def _bootstrap_outlook_monitor_class():
    """Get the OutlookMonitor class.

    Works in three modes:
    1. PyInstaller --onefile/--onedir frozen mode: use dotted import
       "outlook_agent.outlook_monitor" (PyInstaller loads via import hooks)
    2. Source mode with already-loaded modules: check sys.modules
    3. Source mode fresh: sys.path manipulation to add outlook_agent_dir

    The previous version only handled modes 2-3, which caused
    ModuleNotFoundError in PyInstaller mode (T5 failure root cause).
    """
    # PyInstaller frozen mode: use dotted import via PyInstaller's import hooks
    if getattr(sys, "frozen", False):
        try:
            from outlook_agent.outlook_monitor import OutlookMonitor
            return OutlookMonitor
        except ImportError as e:
            logger.warning("PyInstaller mode: failed to import outlook_agent.outlook_monitor: %s", e)
            return None

    # Fast path: already loaded modules (source mode)
    for modname in (
        "outlook_monitor",
        "outlook_agent.outlook_monitor",
        "agent_tool.outlook_agent.outlook_monitor",
    ):
        mod = sys.modules.get(modname)
        if mod is not None and hasattr(mod, "OutlookMonitor"):
            return mod.OutlookMonitor

    # Source-mode path manipulation
    here = os.path.abspath(__file__)
    pr_po_root = os.path.dirname(here)
    agent_tool_root = os.path.dirname(pr_po_root)
    outlook_agent_dir = os.path.join(agent_tool_root, "outlook_agent")

    cached_config = sys.modules.get("config")
    if cached_config is not None:
        try:
            cfg_file = getattr(cached_config, "__file__", "") or ""
            if os.path.abspath(pr_po_root) in os.path.abspath(cfg_file):
                del sys.modules["config"]
        except Exception:
            pass

    saved_pp_indices = [
        i for i, p in enumerate(sys.path)
        if os.path.abspath(p) == os.path.abspath(pr_po_root)
    ]
    for i in sorted(saved_pp_indices, reverse=True):
        del sys.path[i]
    if outlook_agent_dir not in sys.path:
        sys.path.insert(0, outlook_agent_dir)

    try:
        from outlook_monitor import OutlookMonitor
        return OutlookMonitor
    finally:
        if saved_pp_indices and pr_po_root not in sys.path:
            sys.path.insert(0, pr_po_root)
        if cached_config is not None and "config" not in sys.modules:
            sys.modules["config"] = cached_config


class MailAgentThread:
    """Runs Mail Agent's polling loop in a background thread."""

    def __init__(self, rules_path, outlook_monitor_class=None):
        self.rules_path = rules_path
        self._outlook_monitor_class = outlook_monitor_class
        self._stop_event = threading.Event()
        self._thread = None
        self._agent = None

    def start(self):
        if self._thread and self._thread.is_alive():
            logger.info("Mail Agent thread already running")
            return False
        try:
            from agents.mail_agent.monitor import MailAgent
        except Exception as e:
            logger.error("Failed to import MailAgent: %s", e, exc_info=True)
            return False
        self._agent = MailAgent(
            self.rules_path, outlook_monitor_class=self._outlook_monitor_class
        )
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name="MailAgentThread"
        )
        self._thread.start()
        logger.info("Mail Agent thread started")
        return True

    def stop(self, timeout=5.0):
        if not self._thread:
            return
        logger.info("Stopping Mail Agent thread")
        self._stop_event.set()
        if self._agent is not None:
            try:
                self._agent.stop(timeout=timeout)
            except Exception as e:
                logger.warning("agent.stop failed: %s", e)
        self._thread.join(timeout=timeout)
        if self._thread.is_alive():
            logger.warning("Mail Agent thread did not stop in %.1fs", timeout)
        self._thread = None

    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    def _run_loop(self):
        try:
            interval = 120
            try:
                interval = int(
                    self._agent._rules_data.get("settings", {}).get(
                        "poll_interval_seconds", 120
                    )
                )
            except Exception:
                pass
            logger.info("Mail Agent poll loop started (interval=%ds)", interval)
            while not self._stop_event.is_set():
                try:
                    self._agent.run_once()
                except Exception as e:
                    logger.error("Mail Agent poll cycle error: %s", e)
                slept = 0.0
                while slept < interval and not self._stop_event.is_set():
                    time.sleep(0.5)
                    slept += 0.5
            logger.info("Mail Agent poll loop exited")
        except Exception as e:
            logger.error("Mail Agent thread crashed: %s", e, exc_info=True)


class MailAgentController:
    """Public API for managing Mail Agent lifecycle from PRPOAgent."""

    def __init__(self, rules_path=None):
        self._lock = threading.Lock()
        self._impl = None
        if rules_path is None:
            # PyInstaller frozen mode: rules.yaml is extracted to _MEIPASS
            if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
                rules_path = os.path.join(
                    sys._MEIPASS, "agents", "mail_agent", "rules.yaml"
                )
            else:
                # Source mode: resolve relative to this file
                here = os.path.abspath(__file__)
                pr_po_root = os.path.dirname(here)
                rules_path = os.path.join(
                    pr_po_root, "agents", "mail_agent", "rules.yaml"
                )
            logger.info("Mail Agent rules_path=%s", rules_path)
            if not os.path.isfile(rules_path):
                logger.error("rules.yaml missing: %s", rules_path)
                raise FileNotFoundError(
                    "rules.yaml not found at expected path: %s" % rules_path
                )
        self.rules_path = rules_path
        self._outlook_monitor_class = _bootstrap_outlook_monitor_class()
        if self._outlook_monitor_class is None:
            logger.warning("OutlookMonitor class not pre-loaded; Mail Agent may fail to connect")
        # Safety net: ensure log file is set up early (before start() is called)
        _setup_logging()

    def start(self):
        with self._lock:
            if self._impl is not None and self._impl.is_running():
                return False
            _setup_logging()
            self._impl = MailAgentThread(
                self.rules_path,
                outlook_monitor_class=self._outlook_monitor_class,
            )
            return self._impl.start()

    def stop(self, timeout=5.0):
        with self._lock:
            if self._impl is None:
                return
            self._impl.stop(timeout=timeout)
            self._impl = None

    def is_running(self):
        with self._lock:
            return self._impl is not None and self._impl.is_running()

    def pid(self):
        import os
        return os.getpid()
