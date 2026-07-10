# -*- coding: utf-8 -*-
"""CLI entry point for Mail Agent.

Usage:
    python -m agents.mail_agent --check    Verify config and Outlook connection
    python -m agents.mail_agent --run      Start polling loop
    python -m agents.mail_agent --path     Print inbox path
    python -m agents.mail_agent --help     Show this help
"""

import argparse
import logging
import os
import sys
import time

logger = logging.getLogger("mail_agent")


# When this module is run as `python -m agents.mail_agent`, ensure the
# project root (C:\Open AI Proj) is on sys.path so we can import the
# package via `agents.mail_agent`.
def _ensure_project_root():
    here = os.path.abspath(__file__)
    # __main__.py is at agent_tool/pr_po_agent/agents/mail_agent/__main__.py
    # Up 4 levels = C:\Open AI Proj (project root)
    d = os.path.dirname(here)
    for _ in range(4):
        d = os.path.dirname(d)
    if d not in sys.path:
        sys.path.insert(0, d)
    # Also expose agent_tool/ so `from agent_tool.outlook_agent...` works
    # when invoked via `python -m agents.mail_agent` from pr_po_agent/.
    project_root = d
    agent_tool_dir = os.path.join(project_root, "agent_tool")
    if os.path.isdir(agent_tool_dir) and agent_tool_dir not in sys.path:
        sys.path.insert(0, agent_tool_dir)


def _setup_logging(level="INFO"):
    log_dir = os.path.expandvars(os.path.expanduser("%USERPROFILE%/PRPOAgent"))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "mail_agent.log")
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def _resolve_rules_path():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "rules.yaml"
    )


def _resolve_inbox_path():
    return os.path.join(
        os.path.expandvars(os.path.expanduser("%USERPROFILE%/PRPOAgent")), "inbox"
    )


def cmd_check(args):
    """Verify config and Outlook connection without starting the loop."""
    from agents.mail_agent.rules_engine import load_rules
    from agents.mail_agent.inbox_writer import get_inbox_root

    rules_path = _resolve_rules_path()
    data = load_rules(rules_path)
    rules = data.get("rules", [])
    enabled = [r for r in rules if r.get("enabled")]
    print("Mail Agent configuration check")
    print("  rules_file:        %s" % rules_path)
    print("  rules_loaded:      %d" % len(rules))
    print("  rules_enabled:     %d" % len(enabled))
    print("  inbox_path:        %s" % get_inbox_root())

    # Try connecting to Outlook
    try:
        from agents.mail_agent.monitor import MailAgent
        m = MailAgent(rules_path)
        try:
            m._connect_outlook()
            print("  outlook_connected: YES")
        except Exception as e:
            print("  outlook_connected: NO  (%s)" % e)
        return 0
    except Exception as e:
        print("  outlook_connected: NO  (%s)" % e)
        return 1


def cmd_path(args):
    print(_resolve_inbox_path())
    return 0


def cmd_run(args):
    from agents.mail_agent.monitor import MailAgent
    rules_path = _resolve_rules_path()
    if not os.path.isfile(rules_path):
        print("Rules file not found: %s" % rules_path)
        return 1

    print("=== Mail Agent v1.0.0-preview ===")
    print("  rules:    %s" % rules_path)
    print("  inbox:    %s" % _resolve_inbox_path())
    print("  log_file: %USERPROFILE%/PRPOAgent/mail_agent.log")
    print("  press Ctrl-C to stop")
    print("==================================")

    agent = MailAgent(rules_path)
    try:
        agent.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        agent.stop()
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m agents.mail_agent",
        description="Mail Agent - monitor Outlook and persist matched emails",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true",
                       help="Verify config and Outlook connection")
    group.add_argument("--run", action="store_true",
                       help="Start the polling loop")
    group.add_argument("--path", action="store_true",
                       help="Print the inbox path and exit")
    args = parser.parse_args(argv)

    _ensure_project_root()

    if args.path:
        return cmd_path(args)
    if args.check:
        _setup_logging("WARNING")  # quieter for --check
        return cmd_check(args)
    if args.run:
        _setup_logging("INFO")
        return cmd_run(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
