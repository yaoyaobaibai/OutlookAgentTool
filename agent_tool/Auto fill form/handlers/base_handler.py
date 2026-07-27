"""
Abstract base class for all field type handlers.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseHandler(ABC):
    """Abstract base class for field type handlers."""

    def __init__(self, page, workflow_config: dict):
        self.page = page
        self.workflow_config = workflow_config

    @abstractmethod
    def execute(self, field_config: dict, value: str) -> dict:
        """
        Execute field filling.

        Args:
            field_config: Field configuration (from workflow.json fields[name])
            value: Value to fill

        Returns:
            {"success": bool, "message": str, "evidence": dict}
        """
        pass

    def validate(self, field_config: dict) -> list:
        """
        Validate field_config contains all required parameters.
        Returns list of error messages (empty = valid).
        """
        errors = []
        if "selector" not in field_config or not field_config.get("selector"):
            errors.append("Missing required 'selector' in field config")
        return errors

    def retry_count(self) -> int:
        """Default retry count for this handler type."""
        return 2

    def cleanup(self):
        """Optional cleanup after handler execution."""
        pass
