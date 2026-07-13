# -*- coding: utf-8 -*-
"""Mail Agent controller for PRPOAgent.

Mail Agent runs IN-PROCESS as a daemon thread (not a subprocess) so it
works in both source mode and PyInstaller --onefile EXE mode (where
sys.executable is the EXE itself).

The controller pre-imports the OutlookMonitor class and passes it to
MailAgent, sidestepping the sys.path shadowing problem.

Logging is English ASCII per SKILL.md.
"""

import logging
import os
import sys
import threading
import time

logger = logging.getLogger(__name__)


def _setup_logging():
    """Configure file logging for Mail Agent.
    Mirrors the setup in agents/mail_agent/__main__.py.
    """
    log_dir = os.path.expandvars(os.path.expanduser(r"%USERPROFILE%/PRPOAgent"))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "mail_agent.log")
    root = logging.getLogger()
    # Avoid double-setup
    if not any(
        isinstance(h, logging.FileHandler)
        and getattr(h, "baseFilename", "").lower() == log_file.lower()
        for h in root.handlers
    ):
        root.setLevel(logging.INFO)
        fmt = logging.Formatter(
            "%(asctime)s %(name)s %(levelname)s: %(message)s"
        )
        try:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(fmt)
            root.addHandler(fh)
        except Exception as e:
            sys.stderr.write("Failed to set up Mail Agent log: %s\n" % e)


def _bootstrap_outlook_monitor_class():
    """Pre-import OutlookMonitor from outlook_agent.

    Mirrors the workaround in monitor.py. outlook_monitor.py does
    `from config import load_config`. When pr_po_agent/ is on sys.path,
    its config.py shadows outlook_agent/config.py. We work around that.
    """
    here = os.path.abspath(__file__)
    # mail_controller.py is at agent_tool/pr_po_agent/mail_controller.py
    # outlook_monitor.py is at agent_tool/outlook_agent/outlook_monitor.py
    pr_po_root = os.path.dirname(here)
    agent_tool_root = os.path.dirname(pr_po_root)
    outlook_agent_dir = os.path.join(agent_tool_root, "outlook_agent")

    # Snapshot
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
        import sys as _sys
        _dbg = open(_sys.path[0] + r"\..\..\mail_controller_debug.log", "a") if False else None
        def _log(msg):
            try:
                log_path = r"C:\Users\P1313993\AppData\Local\Temp\PRPOAgent.controller.log"
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(msg + "\n")
            except Exception:
                pass
        _log("MailAgentController.__init__ start")
        self._lock = threading.Lock()
        _log("lock created")
        self._impl = None
        _log("_impl = None")
        if rules_path is None:
            here = os.path.abspath(__file__)
            pr_po_root = os.path.dirname(here)
            rules_path = os.path.join(
                pr_po_root, "agents", "mail_agent", "rules.yaml"
            )
        self.rules_path = rules_path
        _log("rules_path=" + self.rules_path)
        _log("calling _bootstrap_outlook_monitor_class")
        self._outlook_monitor_class = _bootstrap_outlook_monitor_class()
        _log("bootstrap returned, class=%s" % bool(self._outlook_monitor_class))
        if self._outlook_monitor_class is None:
            logger.warning("OutlookMonitor class not pre-loaded; Mail Agent may fail to connect")
        _log("__init__ done")

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
