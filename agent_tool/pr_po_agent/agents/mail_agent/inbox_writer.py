# -*- coding: utf-8 -*-
"""Inbox writer for Mail Agent.

Writes processed-email records (JSON) and downloaded attachments
to %USERPROFILE%/PRPOAgent/inbox/. All logging in English ASCII.
"""

import json
import logging
import os
import re

logger = logging.getLogger(__name__)

_INVALID_FN_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _resolve_path(template: str) -> str:
    """Resolve %USERPROFILE% style placeholders in a path template."""
    return os.path.expandvars(os.path.expanduser(template))


def get_inbox_root() -> str:
    """Return the inbox root path, creating it if it does not exist.

    Path resolution: %USERPROFILE%/PRPOAgent/inbox by default.
    """
    path = _resolve_path("%USERPROFILE%/PRPOAgent/inbox")
    os.makedirs(path, exist_ok=True)
    return path


def _sanitize_filename(name: str) -> str:
    """Strip invalid Windows filename characters; collapse spaces."""
    name = name.strip()
    name = _INVALID_FN_CHARS.sub("_", name)
    name = re.sub(r"\s+", "_", name)
    return name or "unnamed"


def write_email_record(email: dict, attachment_paths: list, inbox_root: str = None,
                       rule_name: str = "") -> str:
    """Write a JSON record of the processed email.

    Returns the full path to the JSON file.
    """
    if inbox_root is None:
        inbox_root = get_inbox_root()
    os.makedirs(inbox_root, exist_ok=True)

    message_id = _sanitize_filename(str(email.get("message_id", "unknown")))
    record_path = os.path.join(inbox_root, message_id + ".json")

    record = {
        "message_id": email.get("message_id", ""),
        "subject": email.get("subject", ""),
        "sender": email.get("sender_email", ""),
        "received_at": email.get("received_at", ""),
        "rule_name": rule_name,
        "attachments": list(attachment_paths or []),
    }
    with open(record_path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    logger.info("Wrote email record: %s (attachments=%d)", record_path, len(attachment_paths))
    return record_path


def write_attachment(message_id: str, attachment, attachments_dir: str = None) -> str:
    """Save one attachment to disk and return the saved path.

    `attachment` may be:
    - a file path (str/Path) -> copy to inbox/attachments/<id>/
    - a file-like object with .read() and .name
    - an Outlook COM Attachment object (uses .FileName and .SaveAsFile)
    """
    if attachments_dir is None:
        attachments_dir = os.path.join(get_inbox_root(), "attachments", _sanitize_filename(str(message_id)))
    os.makedirs(attachments_dir, exist_ok=True)

    # Resolve source path and filename
    if isinstance(attachment, (str, os.PathLike)):
        src_path = str(attachment)
        if not os.path.isfile(src_path):
            raise FileNotFoundError(src_path)
        base_name = os.path.basename(src_path)
        data = open(src_path, "rb").read()
    elif hasattr(attachment, "read") and hasattr(attachment, "name"):
        base_name = os.path.basename(attachment.name)
        data = attachment.read()
    elif hasattr(attachment, "FileName") and hasattr(attachment, "SaveAsFile"):
        # Outlook COM Attachment: FileName is full path after .SaveAsFile
        base_name = os.path.basename(attachment.FileName)
        data = attachment.SaveAsFile()  # returns bytes in modern Outlook
        if hasattr(data, "Read"):
            data = data.Read()
    else:
        raise TypeError("Unsupported attachment type: %s" % type(attachment).__name__)

    safe_name = _sanitize_filename(base_name)
    target_path = os.path.join(attachments_dir, safe_name)

    # Disambiguate if a same-named file already exists
    if os.path.exists(target_path):
        stem, ext = os.path.splitext(safe_name)
        i = 1
        while True:
            candidate = os.path.join(attachments_dir, "%s_%d%s" % (stem, i, ext))
            if not os.path.exists(candidate):
                target_path = candidate
                break
            i += 1

    if isinstance(data, bytes):
        with open(target_path, "wb") as f:
            f.write(data)
    else:
        with open(target_path, "wb") as f:
            f.write(data)
    logger.info("Saved attachment: %s", target_path)
    return target_path
