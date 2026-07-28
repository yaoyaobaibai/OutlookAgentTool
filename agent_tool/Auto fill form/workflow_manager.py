"""
Workflow Manager - Workflow discovery, loading, switching, and persistence.

This module provides the WorkflowManager class that handles all workflow
management operations for the FormFiller multi-workflow architecture.
It is used by both the GUI (to populate the workflow dropdown) and the
WorkflowEngine (to get the current workflow config).
"""

import json
import os
import glob
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------

class WorkflowError(Exception):
    """Base exception for workflow errors."""
    pass


class WorkflowNotFoundError(WorkflowError):
    """Raised when workflow.json is not found for a given workflow name."""

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        super().__init__(f"Workflow '{name}' not found at: {path}")


class WorkflowValidationError(WorkflowError):
    """Raised when workflow.json fails schema validation."""

    def __init__(self, message: str, errors: list = None):
        self.validation_errors = errors or []
        detail = f"Workflow validation failed: {message}"
        if self.validation_errors:
            detail += "\n  - " + "\n  - ".join(self.validation_errors)
        super().__init__(detail)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class WorkflowInfo:
    """Basic information about a workflow."""
    name: str                       # Folder name (e.g., "csms_create_proposal")
    display_name: str               # From workflow.json workflow_name
    version: str                    # From workflow.json version
    description: str = ""           # From workflow.json description
    status: str = "active"          # From workflow.json status


@dataclass
class FieldDefinition:
    """Definition of a form field within a workflow."""
    label: str                      # Field name from workflow.json fields key
    selector: str                   # CSS selector
    field_type: str                 # input/select/autocomplete/datepicker/etc
    required: bool = False
    default_value: str = ""
    handler_config: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# WorkflowManager
# ---------------------------------------------------------------------------

class WorkflowManager:
    """Manages workflow discovery, loading, switching, and persistence.

    The WorkflowManager scans the workflows/ directory for subdirectories
    containing workflow.json configuration files, provides methods to load
    and validate workflow configs, and persists the currently selected
    workflow to settings.json.
    """

    WORKFLOWS_DIR = "workflows"
    SETTINGS_FILE = "workflows/settings.json"
    SCHEMA_DIR = "workflows/schema"
    WORKFLOW_CONFIG_FILE = "workflow.json"

    def __init__(self, workflows_dir: str = None):
        """Initialize the WorkflowManager and discover available workflows.

        Args:
            workflows_dir: Base workflows directory path.
                           Defaults to WORKFLOWS_DIR ("workflows").
        """
        if workflows_dir is not None:
            self.WORKFLOWS_DIR = workflows_dir
            # Recompute dependent paths
            base = os.path.dirname(workflows_dir.rstrip("/\\"))
            if base and os.path.isabs(workflows_dir):
                self.SETTINGS_FILE = os.path.join(workflows_dir, "settings.json")
                self.SCHEMA_DIR = os.path.join(workflows_dir, "schema")
            else:
                self.SETTINGS_FILE = "workflows/settings.json"
                self.SCHEMA_DIR = "workflows/schema"

        self._workflows: list[WorkflowInfo] = []
        self._current_workflow: str = ""

        # Resolve absolute paths
        self._workflows_dir_abs = os.path.abspath(self.WORKFLOWS_DIR)
        self._settings_file_abs = os.path.abspath(self.SETTINGS_FILE)

        # Load persisted settings
        self._load_settings()

        # Discover available workflows
        self.discover_workflows()

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover_workflows(self) -> list[WorkflowInfo]:
        """Scan the workflows directory for subdirectories containing workflow.json.

        Skips directories starting with underscore or dot. Logs warnings
        for directories without a valid workflow.json.

        Returns:
            list[WorkflowInfo]: List of discovered workflow information.
        """
        self._workflows = []
        workflows_dir = self._workflows_dir_abs

        if not os.path.isdir(workflows_dir):
            logger.warning("Workflows directory not found: %s", workflows_dir)
            return self._workflows

        try:
            entries = sorted(os.listdir(workflows_dir))
        except PermissionError as e:
            logger.error("Cannot list workflows directory: %s", e)
            return self._workflows

        for entry in entries:
            # Skip directories starting with underscore or dot
            if entry.startswith("_") or entry.startswith("."):
                continue

            subdir = os.path.join(workflows_dir, entry)
            if not os.path.isdir(subdir):
                continue

            config_path = os.path.join(subdir, self.WORKFLOW_CONFIG_FILE)
            if not os.path.isfile(config_path):
                logger.warning(
                    "Skipping '%s': %s not found", entry, self.WORKFLOW_CONFIG_FILE
                )
                continue

            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)

                info = WorkflowInfo(
                    name=entry,
                    display_name=config.get("workflow_name", entry),
                    version=str(config.get("version", "0.0.0")),
                    description=config.get("description", ""),
                    status=config.get("status", "active"),
                )
                self._workflows.append(info)
                logger.info("Discovered workflow: %s v%s", info.display_name, info.version)

            except json.JSONDecodeError as e:
                logger.warning(
                    "Skipping '%s': Invalid JSON in %s - %s",
                    entry, self.WORKFLOW_CONFIG_FILE, e,
                )
            except Exception as e:
                logger.warning(
                    "Skipping '%s': Unexpected error reading %s - %s",
                    entry, self.WORKFLOW_CONFIG_FILE, e,
                )

        return self._workflows

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_workflows(self) -> list[dict]:
        """Return a list of workflow summaries for the GUI dropdown.

        Returns:
            list[dict]: Each entry contains {"name": str, "display_name": str}.
        """
        return [
            {
                "name": wf.name,
                "display_name": wf.display_name,
            }
            for wf in self._workflows
        ]

    # ------------------------------------------------------------------
    # Loading / Validation
    # ------------------------------------------------------------------

    def load_workflow(self, name: str) -> dict:
        """Load and validate a workflow.json by workflow name.

        Args:
            name: The workflow folder name (e.g., "csms_create_proposal").

        Returns:
            dict: Parsed workflow.json contents.

        Raises:
            WorkflowNotFoundError: If the workflow directory or workflow.json
                does not exist.
            WorkflowValidationError: If the workflow.json fails schema
                validation or cannot be parsed.
        """
        if not name:
            raise WorkflowNotFoundError(name="(empty)", path="")

        config_path = os.path.join(self._workflows_dir_abs, name, self.WORKFLOW_CONFIG_FILE)

        if not os.path.isfile(config_path):
            raise WorkflowNotFoundError(name=name, path=config_path)

        # Load JSON
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise WorkflowValidationError(
                f"Failed to parse {config_path}: {e}",
                errors=[str(e)],
            )

        # Attempt schema validation using validate_workflow module
        self._run_schema_validation(config_path, config)

        return config

    def _run_schema_validation(self, config_path: str, config: dict) -> None:
        """Run schema validation via validate_workflow if available.

        Attempts to import the validate_workflow module from the schema
        directory. If successful, calls its validate function. If the
        module is not available (e.g., not yet created), logs a warning
        and skips validation.

        Args:
            config_path: Path to the workflow.json file (for display).
            config: Parsed workflow configuration dict.

        Raises:
            WorkflowValidationError: If validation fails.
        """
        try:
            # Try importing validate_workflow from the schema directory
            import importlib.util
            import sys

            validator_path = os.path.join(
                self._workflows_dir_abs, "schema", "validate_workflow.py"
            )

            if os.path.isfile(validator_path):
                spec = importlib.util.spec_from_file_location(
                    "validate_workflow", validator_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules["validate_workflow"] = module
                    spec.loader.exec_module(module)

                    if hasattr(module, "validate"):
                        is_valid, errors = module.validate(config)
                        if not is_valid and errors:
                            raise WorkflowValidationError(
                                f"Schema validation failed for {config_path}",
                                errors=errors,
                            )
                        logger.info(
                            "Schema validation passed for %s", config_path
                        )
                    else:
                        logger.warning(
                            "validate_workflow module found but has no validate() function"
                        )
                else:
                    logger.warning(
                        "Could not load validate_workflow from %s", validator_path
                    )
            else:
                logger.warning(
                    "Schema validator not found at %s. Skipping validation.",
                    validator_path,
                )
        except WorkflowValidationError:
            raise
        except Exception as e:
            logger.warning(
                "Schema validation skipped due to error: %s", e
            )

    # ------------------------------------------------------------------
    # Workflow Info / Fields
    # ------------------------------------------------------------------

    def get_workflow_info(self, name: str) -> WorkflowInfo:
        """Get WorkflowInfo for a named workflow.

        Args:
            name: The workflow folder name.

        Returns:
            WorkflowInfo dataclass with workflow metadata.

        Raises:
            WorkflowNotFoundError: If the workflow is not in the discovered list.
        """
        for wf in self._workflows:
            if wf.name == name:
                return wf

        # If not found in discovered list, try loading directly
        try:
            config = self.load_workflow(name)
            info = WorkflowInfo(
                name=name,
                display_name=config.get("workflow_name", name),
                version=str(config.get("version", "0.0.0")),
                description=config.get("description", ""),
                status=config.get("status", "active"),
            )
            return info
        except WorkflowNotFoundError:
            raise WorkflowNotFoundError(name=name, path="")

    def get_field_definitions(self, name: str = None) -> list[FieldDefinition]:
        """Get field definitions for a workflow.

        Args:
            name: The workflow folder name. If None, uses the current workflow.

        Returns:
            list[FieldDefinition]: List of field definitions.

        Raises:
            WorkflowNotFoundError: If the workflow is not found.
            WorkflowValidationError: If the workflow config is invalid.
        """
        if name is None:
            name = self.get_current_workflow()
            if not name:
                return []

        config = self.load_workflow(name)
        fields_config = config.get("fields", {})
        definitions = []

        for field_name, field_cfg in fields_config.items():
            definitions.append(FieldDefinition(
                label=field_name,
                selector=field_cfg.get("selector", ""),
                field_type=field_cfg.get("type", "input"),
                required=field_cfg.get("required", False),
                default_value=field_cfg.get("default_value", ""),
                handler_config=field_cfg.get("handler_config", {}),
            ))

        return definitions

    # ------------------------------------------------------------------
    # Current Workflow Persistence
    # ------------------------------------------------------------------

    def get_current_workflow(self) -> str:
        """Get the name of the currently selected workflow.

        Returns:
            str: The workflow folder name, or empty string if none selected.
        """
        return self._current_workflow

    def set_current_workflow(self, name: str):
        """Set the current workflow and persist to settings.json.

        Args:
            name: The workflow folder name to set as current.

        Raises:
            WorkflowNotFoundError: If the named workflow does not exist.
        """
        # Verify workflow exists
        found = any(wf.name == name for wf in self._workflows)
        if not found:
            # Allow setting workflows not yet discovered (e.g., if manually defined)
            config_path = os.path.join(
                self._workflows_dir_abs, name, self.WORKFLOW_CONFIG_FILE
            )
            if not os.path.isfile(config_path):
                raise WorkflowNotFoundError(name=name, path=config_path)

        self._current_workflow = name
        self._save_settings()

    def validate_current_workflow(self) -> tuple:
        """Re-validate the current workflow configuration.

        Returns:
            tuple[bool, list]: (is_valid, errors). If no workflow is selected,
                returns (False, ["No workflow selected"]). If validation passes,
                returns (True, []).
        """
        name = self.get_current_workflow()
        if not name:
            return False, ["No workflow selected"]

        try:
            self.load_workflow(name)
            return True, []
        except WorkflowValidationError as e:
            return False, e.validation_errors if e.validation_errors else [str(e)]
        except WorkflowNotFoundError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Unexpected error: {e}"]

    # ------------------------------------------------------------------
    # Internal Persistence
    # ------------------------------------------------------------------

    def _load_settings(self) -> None:
        """Load settings from settings.json into memory.

        Handles missing file gracefully by using defaults.
        """
        settings_path = self._settings_file_abs
        if not os.path.isfile(settings_path):
            logger.info("Settings file not found at %s. Using defaults.", settings_path)
            self._current_workflow = ""
            return

        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            self._current_workflow = settings.get("current_workflow", "")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Failed to load settings: %s. Using defaults.", e)
            self._current_workflow = ""

    def _save_settings(self) -> None:
        """Save current settings to settings.json.

        Creates the workflows directory if it does not exist.
        """
        settings_path = self._settings_file_abs
        settings_dir = os.path.dirname(settings_path)

        try:
            os.makedirs(settings_dir, exist_ok=True)

            settings = {
                "current_workflow": self._current_workflow,
                "workflow_list": [
                    {"name": wf.name, "display_name": wf.display_name}
                    for wf in self._workflows
                ],
            }

            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            logger.debug("Settings saved to %s", settings_path)
        except IOError as e:
            logger.error("Failed to save settings to %s: %s", settings_path, e)
