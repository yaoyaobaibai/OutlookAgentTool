# -*- coding: utf-8 -*-
"""Mail Agent monitor.

Wraps the existing OutlookMonitor (in agent_tool.outlook_agent.outlook_monitor)
to apply YAML rules and write matched emails + attachments to the inbox.
"""

import json
import logging
import os
import sys
import threading
import time

# Force PyInstaller to bundle outlook_agent modules.
# Wrapped in try/except so we don't break anything if it's not available.
try:
    import outlook_agent.outlook_monitor  # noqa: F401
except ImportError:
    pass

logger = logging.getLogger(__name__)


def _project_root():
    # monitor.py is at agent_tool/pr_po_agent/agents/mail_agent/monitor.py
    # Up 4 levels gets to C:\Open AI Proj (project root)
    here = os.path.abspath(__file__)
    d = os.path.dirname(here)
    for _ in range(4):
        d = os.path.dirname(d)
    return d


def _import_outlook_monitor():
    """Import OutlookMonitor from outlook_agent.

    outlook_monitor.py does `from config import load_config`. When
    pr_po_agent/ is on sys.path, its config.py shadows outlook_agent's.
    Workaround: clear cached config, remove pr_po_agent from sys.path,
    prepend outlook_agent/, then import via full package path.
    """
    project_root = _project_root()
    outlook_agent_dir = os.path.abspath(os.path.join(project_root, "agent_tool", "outlook_agent"))
    pr_po_agent_dir = os.path.abspath(os.path.join(project_root, "agent_tool", "pr_po_agent"))

    cached_config = sys.modules.get("config")
    if cached_config is not None:
        cfg_file = getattr(cached_config, "__file__", "") or ""
        try:
            if pr_po_agent_dir in os.path.abspath(cfg_file):
                del sys.modules["config"]
        except Exception:
            pass

    saved_pp_indices = [i for i, p in enumerate(sys.path)
                        if os.path.abspath(p) == pr_po_agent_dir]
    for i in sorted(saved_pp_indices, reverse=True):
        del sys.path[i]
    if outlook_agent_dir not in sys.path:
        sys.path.insert(0, outlook_agent_dir)

    try:
        from agent_tool.outlook_agent.outlook_monitor import OutlookMonitor
    finally:
        if saved_pp_indices and pr_po_agent_dir not in sys.path:
            sys.path.insert(0, pr_po_agent_dir)
        if cached_config is not None and "config" not in sys.modules:
            sys.modules["config"] = cached_config
    return OutlookMonitor


def _resolve_path(template):
    return os.path.expandvars(os.path.expanduser(template))


class MailAgent:
    """Main Mail Agent class."""

    def __init__(self, rules_path, outlook_monitor_class=None):
        self.rules_path = rules_path
        # Optional pre-imported OutlookMonitor class. If None, monitor
        # will try to import it on first connect (works in source mode).
        # In PyInstaller EXE mode the parent should pre-import and pass
        # it in to avoid sys.path confusion inside the bundled module.
        self._outlook_monitor_class = outlook_monitor_class
        self._stop_event = threading.Event()
        self._thread = None
        self._processed_ids = set()
        self._processed_ids_path = os.path.join(
            _resolve_path("%USERPROFILE%/PRPOAgent"), "processed.json"
        )
        self._load_processed_ids()
        self._rules_data = {"rules": [], "settings": {}}
        self._load_rules()
        self._outlook = None

    def _load_rules(self):
        from agents.mail_agent.rules_engine import load_rules
        self._rules_data = load_rules(self.rules_path)
        return self._rules_data

    def _load_processed_ids(self):
        try:
            if os.path.exists(self._processed_ids_path):
                with open(self._processed_ids_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, list):
                        self._processed_ids = set(saved[-2000:])
                        logger.info("Loaded %d processed email IDs", len(self._processed_ids))
        except Exception as e:
            logger.warning("Failed to load processed IDs: %s", e)

    def _save_processed_ids(self):
        try:
            os.makedirs(os.path.dirname(self._processed_ids_path), exist_ok=True)
            with open(self._processed_ids_path, "w", encoding="utf-8") as f:
                json.dump(list(self._processed_ids)[-2000:], f, ensure_ascii=False)
        except Exception as e:
            logger.warning("Failed to save processed IDs: %s", e)

    def _connect_outlook(self):
        if self._outlook_monitor_class is not None:
            OutlookMonitor = self._outlook_monitor_class
        else:
            OutlookMonitor = _import_outlook_monitor()
        self._outlook = OutlookMonitor(keywords=[], match_mode="any")
        ok = self._outlook.connect()
        if not ok:
            raise RuntimeError("Failed to connect to Outlook")
        return self._outlook

    def start(self):
        if self._thread and self._thread.is_alive():
            logger.warning("MailAgent already running")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True,
                                         name="MailAgent")
        self._thread.start()
        logger.info("MailAgent started (thread=%s)", self._thread.name)

    def stop(self, timeout=5.0):
        logger.info("MailAgent stop requested")
        self._stop_event.set()
        if self._outlook is not None:
            try:
                self._outlook.stop()
            except Exception:
                pass
        if self._thread:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                logger.warning("MailAgent thread did not stop within %.1fs", timeout)

    def run_once(self):
        try:
            if self._outlook is None:
                self._connect_outlook()
            emails = self._outlook.poll_new_emails() or []
            logger.debug("Polled %d new emails", len(emails))
            for email in emails:
                self._process_email(email)
        except Exception as e:
            logger.error("Poll cycle error: %s", e, exc_info=True)

    def _poll_loop(self):
        interval = int(self._rules_data.get("settings", {}).get("poll_interval_seconds", 120))
        logger.info("MailAgent poll loop starting (interval=%ds)", interval)
        while not self._stop_event.is_set():
            self.run_once()
            slept = 0.0
            while slept < interval and not self._stop_event.is_set():
                time.sleep(0.5)
                slept += 0.5
        logger.info("MailAgent poll loop exited")

    def _process_email(self, email):
        from agents.mail_agent.rules_engine import get_enabled_rules, get_first_match
        from agents.mail_agent.inbox_writer import (
            get_inbox_root,
            write_email_record,
            write_attachment,
        )

        message_id = str(email.get("entry_id") or email.get("id") or email.get("message_id") or "")
        if not message_id:
            logger.warning("Email has no id; skipping: subject=%s",
                           email.get("subject", ""))
            return
        if message_id in self._processed_ids:
            logger.debug("Email already processed: %s", message_id)
            return

        rt = email.get("received_at") or email.get("received_time")
        try:
            rt_str = rt.strftime("%Y-%m-%dT%H:%M:%S") if hasattr(rt, "strftime") else str(rt)
        except Exception:
            rt_str = str(rt) if rt else ""
        # Extract attachment names for rule matching
        raw_att = email.get("attachments") or []
        att_names = []
        for a in raw_att:
            if isinstance(a, dict):
                n = a.get("name", "")
                if n:
                    att_names.append(n)
            elif isinstance(a, str) and a:
                att_names.append(a)

        normalized = {
            "message_id": message_id,
            "subject": email.get("subject", "") or "",
            "sender_email": email.get("sender_email", "") or email.get("sender", "") or "",
            "body": email.get("body", "") or "",
            "received_at": rt_str,
            "attachment_count": len(raw_att),
            "attachment_names": att_names,
        }

        rules = get_enabled_rules(self._rules_data)
        matched = get_first_match(normalized, rules)
        if not matched:
            logger.debug("No rule matched: %s", message_id)
            self._processed_ids.add(message_id)
            self._save_processed_ids()
            return

        rule_name = matched.get("name", "")
        actions = matched.get("actions", []) or []
        if "download_attachments" in actions:
            att_paths = self._download_attachments(message_id, email)
        else:
            att_paths = []

        inbox_root = get_inbox_root()
        write_email_record(
            email=normalized,
            attachment_paths=att_paths,
            inbox_root=inbox_root,
            rule_name=rule_name,
        )
        if "mark_as_processed" in actions or att_paths:
            self._processed_ids.add(message_id)
            self._save_processed_ids()
        logger.info("Processed email %s via rule %s (attachments=%d)",
                    message_id, rule_name, len(att_paths))

    def _download_attachments(self, message_id, email):
        """Save attachments for the matched email.

        OutlookMonitor.poll_new_emails() returns only attachment metadata
        (name/size/index). To get the actual binary, we re-fetch the full
        MailItem via Outlook COM by EntryID and call SaveAsFile on each
        attachment.
        """
        from agents.mail_agent.inbox_writer import write_attachment
        att_meta = email.get("attachments") or []
        if not att_meta:
            return []
        if self._outlook is None:
            return []
        # Re-fetch the live MailItem by EntryID
        try:
            import win32com.client
            entry_id = email.get("entry_id") or email.get("id") or message_id
            # Use OutlookMonitor's existing namespace if available
            namespace = getattr(self._outlook, "namespace", None)
            if namespace is None:
                logger.warning("No Outlook namespace available; cannot fetch attachments")
                return []
            mail_item = namespace.GetItemFromID(entry_id)
        except Exception as e:
            logger.warning("Failed to re-fetch mail %s: %s", message_id, e)
            return []
        try:
            attachments = mail_item.Attachments
        except Exception as e:
            logger.warning("Failed to access attachments: %s", e)
            return []
        saved = []
        for i in range(1, attachments.Count + 1):
            try:
                att = attachments.Item(i)
                # Use SaveAsFile to write the attachment to a temp path
                import tempfile
                tmpdir = tempfile.mkdtemp(prefix="mailagent_")
                saved_path = att.SaveAsFile(tmpdir)
                # Move into inbox/attachments/<id>/ using write_attachment
                target = write_attachment(message_id, saved_path)
                saved.append(target)
                # Clean up tempdir (write_attachment copied, original can be removed)
                try:
                    import shutil
                    shutil.rmtree(tmpdir, ignore_errors=True)
                except Exception:
                    pass
            except Exception as e:
                logger.warning("Failed to save attachment index %d: %s", i, e)
        return saved
