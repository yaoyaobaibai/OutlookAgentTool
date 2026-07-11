# -*- coding: utf-8 -*-
"""Rules engine for Mail Agent.

Loads YAML rules and matches incoming emails against them.
All logging is in English ASCII per SKILL.md.
"""

import logging
import re
import yaml

logger = logging.getLogger(__name__)


# Mapping of operator name to a comparator function.
# Each comparator takes (field_value: str, condition_value: str) -> bool.
def _op_equals(a, b):
    return a == b


def _op_not_equals(a, b):
    return a != b


def _op_contains(a, b):
    return b in a


def _op_not_contains(a, b):
    return b not in a


def _op_starts_with(a, b):
    return a.startswith(b)


def _op_ends_with(a, b):
    return a.endswith(b)


def _op_matches_regex(a, b):
    try:
        return re.search(b, a) is not None
    except re.error:
        logger.warning("Invalid regex pattern: %s", b)
        return False


_OPERATORS = {
    "equals": _op_equals,
    "not_equals": _op_not_equals,
    "contains": _op_contains,
    "not_contains": _op_not_contains,
    "starts_with": _op_starts_with,
    "ends_with": _op_ends_with,
    "matches_regex": _op_matches_regex,
}


def load_rules(path: str) -> dict:
    """Load rules from a YAML file.

    Returns a dict with keys: rules (list), settings (dict).
    Empty dict if the file does not exist or is invalid.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("Rules file not found: %s", path)
        return {"rules": [], "settings": {}}
    except yaml.YAMLError as e:
        logger.error("Failed to parse rules YAML: %s", e)
        return {"rules": [], "settings": {}}

    if not isinstance(data, dict):
        logger.error("Rules file root must be a mapping, got %s", type(data).__name__)
        return {"rules": [], "settings": {}}

    rules = data.get("rules") or []
    settings = data.get("settings") or {}
    logger.info("Loaded %d rules from %s", len(rules), path)
    return {"rules": rules, "settings": settings}


def get_enabled_rules(rules_data: dict) -> list:
    """Return only rules whose 'enabled' key is truthy."""
    rules = rules_data.get("rules") or []
    enabled = [r for r in rules if r.get("enabled", False)]
    logger.debug("Enabled rules: %d / %d", len(enabled), len(rules))
    return enabled


def _get_field(email: dict, field: str):
    """Look up a field on the email dict with case-insensitive header fallback."""
    if field in email:
        return email[field]
    # case-insensitive fallback for common header names
    lower_map = {k.lower(): k for k in email.keys()}
    return email.get(lower_map.get(field.lower(), ""), "")


def _check_single_condition(email: dict, condition: dict) -> bool:
    """Evaluate a single condition dict with 'field', 'op', 'value' keys.

    List-valued fields (e.g. attachment_names): a string op matches if
    ANY element of the list satisfies it. Empty list = no match.
    """
    field = condition.get("field", "")
    op_name = condition.get("op", "")
    expected = condition.get("value", "")

    if op_name not in _OPERATORS:
        logger.warning("Unknown operator: %s", op_name)
        return False

    actual = _get_field(email, field)
    if actual is None:
        actual = ""
    op = _OPERATORS[op_name]
    # List fields: any-item match semantics
    if isinstance(actual, (list, tuple)):
        if not actual:
            return False
        exp_str = str(expected)
        return any(op(str(x), exp_str) for x in actual if x is not None)
    return op(str(actual), str(expected))


def _check_conditions(email: dict, conditions: list) -> bool:
    """Conditions is a list of either:
    - single condition dicts (implicit AND)
    - compound dicts with 'all' (AND) or 'any' (OR) keys
    """
    for cond in conditions:
        if not isinstance(cond, dict):
            logger.warning("Skipping invalid condition: %s", cond)
            continue
        if "all" in cond:
            if not all(_check_conditions(email, [c]) for c in cond["all"]):
                return False
        elif "any" in cond:
            if not any(_check_conditions(email, [c]) for c in cond["any"]):
                return False
        else:
            if not _check_single_condition(email, cond):
                return False
    return True


def matches(email: dict, rule: dict) -> bool:
    """Return True if the email matches a single rule."""
    if not rule.get("enabled", False):
        return False
    name = rule.get("name", "<unnamed>")
    conditions = rule.get("conditions", [])
    if not isinstance(conditions, list) or not conditions:
        logger.debug("Rule %s has no conditions; skipping", name)
        return False
    result = _check_conditions(email, conditions)
    if result:
        logger.info("Email matched rule: %s (subject=%s sender=%s)",
                    name, email.get("subject", ""), email.get("sender_email", ""))
    return result


def get_first_match(email: dict, rules: list):
    """Return the first rule (from rules list) that matches the email, or None."""
    for rule in rules:
        if matches(email, rule):
            return rule
    return None
