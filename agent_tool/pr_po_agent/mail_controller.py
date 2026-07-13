# -*- coding: utf-8 -*-
"""Mail Agent process controller for PRPOAgent.

Manages Mail Agent as a child process. PRPOAgent launches Mail Agent on
startup and stops it on exit. All subprocess calls must use
creationflags=0x08000000 to avoid a black cmd window popping up.

Logging is English ASCII per SKILL.md.
"""

import logging
import os
import subprocess
import sys
import threading
import time

logger = logging.getLogger(__name__)

# How long to wait between terminate() and kill() fallback
_STOP_TIMEOUT_SECONDS = 5


class MailAgentController:
    """Manages the Mail Agent child process.

    Usage:
        controller = MailAgentController()
        controller.start()         # launches if not running
        controller.is_running()    # True/False
        controller.restart()       # stop + start
        controller.stop()          # terminate + wait + kill
    """

    def __init__(self):
        self._proc = None
        self._lock = threading.Lock()
        self._cwd = self._resolve_cwd()

    @staticmethod
    def _resolve_cwd():
        """Where to launch the child from. Inside the pr_po_agent dir so
        the relative `agents.mail_agent` package is importable.
        """
        here = os.path.abspath(__file__)
        # mail_controller.py is at agent_tool/pr_po_agent/mail_controller.py
        # so the pr_po_agent dir is its parent.
        return os.path.dirname(here)

    def start(self):
        """Launch Mail Agent if not already running.

        Returns True if a new process was started, False if already running.
        """
        with self._lock:
            if self._proc is not None and self._proc.poll() is None:
                logger.info("Mail Agent already running (pid=%s)", self._proc.pid)
                return False
            # On Windows, sys.executable points to the Python interpreter
            # that runs PRPOAgent. We pass the same interpreter to the child
            # so it does not depend on PATH lookup.
            cmd = [sys.executable, "-m", "agents.mail_agent", "--run"]
            try:
                self._proc = subprocess.Popen(
                    cmd,
                    cwd=self._cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    # P0: hide console window on Windows. Without this flag a
                    # black cmd box would pop up whenever PRPOAgent starts.
                    creationflags=0x08000000,
                )
                logger.info(
                    "Mail Agent started (pid=%s, cmd=%s)", self._proc.pid, " ".join(cmd)
                )
                return True
            except OSError as e:
                logger.error("Failed to start Mail Agent: %s", e)
                self._proc = None
                return False

    def stop(self, timeout: float = _STOP_TIMEOUT_SECONDS):
        """Stop Mail Agent gracefully.

        Tries terminate() first, then waits up to `timeout` seconds. If the
        process is still alive, falls back to kill().
        """
        with self._lock:
            proc = self._proc
            self._proc = None
            if proc is None:
                return
            if proc.poll() is not None:
                logger.info("Mail Agent already exited (pid=%s, rc=%s)", proc.pid, proc.returncode)
                return
            try:
                proc.terminate()
            except Exception as e:
                logger.warning("terminate() failed: %s", e)
            try:
                proc.wait(timeout=timeout)
                logger.info("Mail Agent stopped gracefully (pid=%s, rc=%s)", proc.pid, proc.returncode)
            except subprocess.TimeoutExpired:
                logger.warning("Mail Agent did not stop in %.1fs, killing", timeout)
                try:
                    proc.kill()
                    proc.wait(timeout=2)
                except Exception as e:
                    logger.error("kill() failed: %s", e)

    def restart(self, timeout: float = _STOP_TIMEOUT_SECONDS):
        """Stop then start."""
        self.stop(timeout=timeout)
        return self.start()

    def is_running(self) -> bool:
        """Return True if the Mail Agent process is alive."""
        with self._lock:
            if self._proc is None:
                return False
            return self._proc.poll() is None

    def pid(self):
        """Return the child PID, or None."""
        with self._lock:
            if self._proc is None:
                return None
            return self._proc.pid

    def wait(self, timeout=None):
        """Block until Mail Agent exits (or timeout)."""
        with self._lock:
            proc = self._proc
        if proc is None:
            return None
        try:
            return proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return None
