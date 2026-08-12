"""
WorkflowEngine - Core orchestrator for the FormFiller automation flow.

The WorkflowEngine reads a workflow config (as produced by WorkflowManager),
uses field handlers from the handlers/ package, and drives Playwright to
execute navigation, login, and form field filling in a coordinated flow.

Typical usage:
    from workflow_manager import WorkflowManager
    from workflow_engine import WorkflowEngine

    wm = WorkflowManager()
    config = wm.load_workflow("csms_create_proposal")

    engine = WorkflowEngine(page, config)
    engine.register_callback("on_step_start", lambda name: print(f"Starting {name}"))
    result = engine.execute(username="user", password="pass", field_values={...})
"""

import logging
import time
from typing import Any, Callable, Optional

import logging_setup
from handlers import get_handler

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------

class WorkflowEngineError(Exception):
    """Base exception for workflow engine errors."""
    pass


class WorkflowNavigationError(WorkflowEngineError):
    """Raised when a navigation step fails and is not marked optional."""
    pass


class WorkflowFieldError(WorkflowEngineError):
    """Raised when a field fill operation fails after all retries."""
    pass


# ---------------------------------------------------------------------------
# WorkflowEngine
# ---------------------------------------------------------------------------

class WorkflowEngine:
    """Orchestrates the entire automation flow by interpreting a workflow config.

    The engine is a pure logic component:
    - It does NOT create browser instances (caller provides the page).
    - It does NOT discover or load workflows (WorkflowManager does that).
    - It does NOT contain GUI code.

    Args:
        page: A Playwright sync page object (from playwright.sync_api).
        workflow_config: A dict loaded from a workflow.json (via WorkflowManager).
    """

    def __init__(self, page, workflow_config: dict):
        self.page = page
        self.config = workflow_config
        self.is_running = False
        self.results: dict[str, dict] = {}  # field_name -> {"success": bool, "message": str}
        self.callbacks: dict[str, Callable] = {}  # event_name -> callable

    # ------------------------------------------------------------------
    # Event Callbacks
    # ------------------------------------------------------------------

    def register_callback(self, event: str, callback: Callable):
        """Register an event callback.

        Supported events:
            on_step_start(step_name)     - Fired when a major step begins.
            on_step_end(step_name)       - Fired when a major step completes.
            on_field_start(field_name)   - Fired before a field is processed.
            on_field_end(field_name, result) - Fired after a field is processed.
            on_error(field_or_step, error)   - Fired on any error.

        Args:
            event: Event name string.
            callback: Callable to invoke when the event fires.
        """
        self.callbacks[event] = callback

    def _emit(self, event: str, *args, **kwargs):
        """Emit an event to the registered callback (if any)."""
        callback = self.callbacks.get(event)
        if callback is not None:
            callback(*args, **kwargs)

    # ------------------------------------------------------------------
    # Main Entry Point
    # ------------------------------------------------------------------

    def execute(self, username: str = "", password: str = "", field_values: dict = None) -> dict:
        """Execute the complete workflow.

        Flow:
            1. Login  (if enabled in config)
            2. Navigation steps
            3. Field iteration with dependency resolution

        Args:
            username: Login username (required if login is enabled).
            password: Login password (required if login is enabled).
            field_values: Dict of field_name -> value overrides. Values
                          not provided will use the config's default_value
                          or be skipped.

        Returns:
            dict: Summary with keys:
                total       - number of fields processed
                success     - number of successful fields
                failed      - number of failed fields
                results     - per-field result dicts
                error       - (only if engine-level error occurred)
        """
        self.is_running = True
        field_values = field_values or {}

        try:
            # --- Step 1: Login ---
            self._emit("on_step_start", "login")
            self.execute_login(username, password)
            self._emit("on_step_end", "login")

            stages = self.config.get("stages")
            if stages:
                # --- Multi-stage execution: each stage runs its own
                #     navigation + field subset + post_fill, in order. ---
                self._emit("on_step_start", "stages")
                self._execute_stages(stages, field_values)
                self._emit("on_step_end", "stages")
                # Top-level post_fill runs after ALL stages complete
                self._handle_post_fill(self.config.get("post_fill", {}))
            else:
                # --- Step 2: Navigation ---
                self._emit("on_step_start", "navigation")
                self.execute_navigation()
                self._emit("on_step_end", "navigation")

                # --- Step 3: Fields ---
                self._emit("on_step_start", "fields")
                self.execute_fields(field_values)
                self._emit("on_step_end", "fields")

            return self.get_results()

        except (WorkflowNavigationError, WorkflowFieldError) as e:
            logger.error("Workflow execution failed: %s", e)
            self._emit("on_error", "engine", str(e))
            return {**self.get_results(), "error": str(e)}
        except Exception as e:
            logger.exception("Unexpected workflow error: %s", e)
            self._emit("on_error", "engine", str(e))
            return {**self.get_results(), "error": f"Unexpected error: {e}"}
        finally:
            self.is_running = False

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def execute_login(self, username: str = "", password: str = "") -> bool:
        """Execute automated login using config's fallback selectors.

        The login section of the config should look like::

            "login": {
                "enabled": true,
                "url": "https://example.com/login",
                "fallback_selectors": {
                    "username": ["#username", "input[name='username']"],
                    "password": ["#password", "input[name='password']"],
                    "submit":   ["button[type='submit']", "#loginBtn"]
                }
            }

        If ``enabled`` is false (or absent) the login step is skipped.

        Args:
            username: Login username.
            password: Login password.

        Returns:
            True if login completed or was skipped; may raise on failure.
        """
        login_config = self.config.get("login", {})
        if not login_config.get("enabled", True):
            logger.info("Login disabled — skipping")
            return True

        url = login_config.get("url", "")
        if url:
            logger.info("Navigating to login URL: %s", url)
            self.page.goto(url, timeout=90000)
            self.page.wait_for_load_state("load", timeout=90000)

        fallbacks = login_config.get("fallback_selectors", {})
        user_selectors = fallbacks.get("username", [])
        pass_selectors = fallbacks.get("password", [])
        submit_selectors = fallbacks.get("submit", [])

        if not user_selectors and not pass_selectors:
            logger.info("No login selectors configured — skipping fill")
            return True

        username_filled = self._try_fill_selectors(user_selectors, username)
        password_filled = self._try_fill_selectors(pass_selectors, password)

        if username_filled and password_filled:
            for sel in submit_selectors:
                if self.page.locator(sel).first.count() > 0:
                    logger.info("Clicking login submit button: %s", sel)
                    self.page.locator(sel).first.click()
                    self.page.wait_for_load_state("networkidle")
                    break
        else:
            logger.warning(
                "Login fields not fully filled (username=%s, password=%s)",
                username_filled, password_filled,
            )

        return True

    def _try_fill_selectors(self, selectors: list, value: str) -> bool:
        """Try a list of CSS selectors in order and fill the first match.

        Args:
            selectors: List of CSS selector strings (tried in order).
            value: Value to fill into the matched element.

        Returns:
            True if a selector matched and was filled, False otherwise.
        """
        for sel in selectors:
            try:
                locator = self.page.locator(sel).first
                if locator.count() > 0:
                    locator.wait_for(state="visible", timeout=5000)
                    locator.fill("")
                    if value:
                        locator.fill(str(value))
                    logger.debug("Filled '%s' into selector '%s'", logging_setup.mask_value(value), sel)
                    return True
            except Exception:
                continue
        return False

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def execute_navigation(self, nav_steps=None) -> bool:
        """Execute navigation steps defined in the workflow config.

        Each step is a dict with at least an ``action`` key.
        Supported actions:

            - **goto**:          Navigate to a URL.
                                 Params: ``url``, ``wait_until`` (default ``networkidle``).
            - **click**:         Click the first matching element.
                                 Params: ``selector``.
            - **wait_selector**: Wait for a selector to appear.
                                 Params: ``selector``, ``timeout``.
            - **wait_time**:     Pause execution. Params: ``timeout``.
            - **evaluate**:      Run JavaScript. Params: ``script``.

        Each step can have ``optional: true`` to skip failures gracefully.

        Args:
            nav_steps: Optional list of navigation steps to execute. When
                       omitted (or None), falls back to the config's
                       top-level ``navigation`` array.

        Raises:
            WorkflowNavigationError: If a non-optional step fails.

        Returns:
            True if all steps completed (or optional steps failed).
        """
        if nav_steps is None:
            nav_steps = self.config.get("navigation", [])
        if not nav_steps:
            logger.info("No navigation steps configured")
            return True

        for i, step in enumerate(nav_steps):
            action = step.get("action", "")
            optional = step.get("optional", False)
            timeout = step.get("timeout", 10000)

            logger.debug("Navigation step %d: '%s' (optional=%s)", i + 1, action, optional)

            try:
                if action == "goto":
                    url = step.get("url", "")
                    wait_until = step.get("wait_until", "networkidle")
                    self.page.goto(url, wait_until=wait_until, timeout=step.get("timeout", 30000))

                elif action == "click":
                    selector = step.get("selector", "")
                    self.page.locator(selector).first.click()

                elif action == "wait_selector":
                    selector = step.get("selector", "")
                    self.page.wait_for_selector(selector, timeout=timeout)

                elif action == "wait_time":
                    self.page.wait_for_timeout(timeout)

                elif action == "evaluate":
                    script = step.get("script", "")
                    self.page.evaluate(script)

                else:
                    logger.warning("Unknown navigation action '%s' — skipping", action)

            except Exception as e:
                if optional:
                    logger.warning(
                        "Optional navigation step '%s' failed: %s — continuing", action, e
                    )
                    continue
                raise WorkflowNavigationError(
                    f"Navigation step {i + 1} action '{action}' failed: {e}"
                )

        return True

    # ------------------------------------------------------------------
    # Field Iteration
    # ------------------------------------------------------------------

    def execute_fields(self, field_values: dict, fields_config: dict = None) -> dict:
        """Iterate over fields, resolve dependencies, call handlers.

        Fields are processed in dependency order (topological sort based on
        ``depends_on``). Each field is filled via its registered handler with
        automatic retry.

        Args:
            field_values: Dict of field_name -> value. Missing fields fall
                          back to the config's ``default_value``.
            fields_config: Optional dict of field_name -> config to process.
                           When omitted (or None), falls back to the config's
                           top-level ``fields`` map. Stage execution passes a
                           resolved subset here.

        Returns:
            dict: Per-field results (``{field_name: {"success": bool, ...}}``).

        Raises:
            WorkflowFieldError: If a required field fails after all retries.
        """
        if fields_config is None:
            fields_config = self.config.get("fields", {})
        if not fields_config:
            logger.info("No fields configured")
            return self.results

        # Sort fields by dependency so that dependents come after their prerequisites
        ordered = self._order_fields_by_dependency(fields_config)

        for field_name in ordered:
            if not self.is_running:
                logger.info("Execution stopped mid-flight")
                break

            field_config = fields_config[field_name]
            value = field_values.get(field_name, field_config.get("default_value", ""))

            # Skip fields with no value when they are not required
            if not value and not field_config.get("required", False):
                logger.debug("Skipping optional field '%s' (no value)", field_name)
                continue

            self._emit("on_field_start", field_name)

            # Resolve the handler
            field_type = field_config.get("type", "input")
            handler = self._get_handler(field_type)

            logger.info("Field '%s' (type=%s): start", field_name, field_type)

            # Execute with retry
            retries = handler.retry_count()
            last_error: Optional[dict] = None

            for attempt in range(retries + 1):
                try:
                    result = handler.execute(field_config, value)
                    if result.get("success"):
                        self.results[field_name] = result
                        logger.info("Field '%s': success - %s", field_name, logging_setup.mask_message(result.get("message", "")))
                        # Surface non-fatal evidence warnings (e.g. autocomplete
                        # fallback / no dropdown items) without affecting success
                        # semantics or triggering a retry.
                        warning = result.get("evidence", {}).get("warning")
                        if warning:
                            logger.warning("Field '%s': %s", field_name, warning)
                        self._emit("on_field_end", field_name, result)
                        # Clear the stale failure from an earlier attempt so the
                        # post-loop guard does not misreport a retried success.
                        last_error = None
                        break
                    last_error = result
                except Exception as e:
                    last_error = {"success": False, "message": str(e)}

                if attempt < retries:
                    logger.debug(
                        "Retrying field '%s' (attempt %d/%d)",
                        field_name, attempt + 1, retries,
                    )
                    time.sleep(1)

            # If all retries failed, emit error and raise
            if last_error and not last_error.get("success"):
                self.results[field_name] = last_error
                logger.warning("Field '%s': FAILED - %s", field_name, logging_setup.mask_message(last_error.get("message", "")))
                self._emit("on_error", field_name, last_error)
                raise WorkflowFieldError(
                    f"Field '{field_name}' failed after {retries} retries: "
                    f"{last_error.get('message', 'unknown error')}"
                )

            # Handle post-fill action (e.g. click a CRM button after filling)
            post_fill = field_config.get("post_fill", {})
            if post_fill:
                try:
                    self._handle_post_fill(post_fill)
                except Exception as e:
                    logger.warning("Post-fill action failed for '%s': %s", field_name, e)

        return self.results

    def _execute_stages(self, stages: list, field_values: dict):
        """Execute a multi-stage workflow sequentially.

        Each stage runs, in order:
            1. its own navigation steps,
            2. the subset of top-level fields it references,
            3. its own post_fill action (if any).

        ``field_values`` is shared across every stage. Stage ``fields`` is a
        string array of names referencing keys in the config's top-level
        ``fields`` map (single source of truth).

        Args:
            stages: List of stage dicts, each with optional ``name``,
                    ``navigation``, ``fields`` (string array) and ``post_fill``.
            field_values: Dict of field_name -> value, shared by all stages.

        Raises:
            WorkflowFieldError: If a stage references an unknown field name.
            WorkflowNavigationError: If a non-optional navigation step fails.
        """
        all_fields = self.config.get("fields", {})

        for stage in stages:
            stage_name = stage.get("name", "")
            self._emit("on_step_start", f"stage:{stage_name}")

            # Stage-specific navigation
            self.execute_navigation(stage.get("navigation", []))

            # Resolve the stage's field subset from the top-level fields map
            resolved: dict[str, dict] = {}
            for fname in stage.get("fields", []):
                if fname not in all_fields:
                    raise WorkflowFieldError(
                        f"Stage '{stage_name}' references unknown field '{fname}'"
                    )
                resolved[fname] = all_fields[fname]

            self.execute_fields(field_values, fields_config=resolved)

            # Stage-level post-fill (only when a non-empty action is defined)
            post_fill = stage.get("post_fill", {})
            if post_fill:
                self._handle_post_fill(post_fill)

            self._emit("on_step_end", f"stage:{stage_name}")

    def _get_handler(self, field_type: str):
        """Get a handler instance for the given field type.

        Uses the handlers package's registry. Each handler receives the
        page and the full workflow config.

        Args:
            field_type: Handler type string (e.g. "input", "select").

        Returns:
            BaseHandler instance.

        Raises:
            WorkflowFieldError: If the handler type is unknown.
        """
        try:
            handler_cls = get_handler(field_type)
            return handler_cls(self.page, self.config)
        except KeyError as e:
            raise WorkflowFieldError(
                f"Unknown field type '{field_type}'. Available types: "
                f"{self._list_handler_types()}"
            ) from e

    @staticmethod
    def _list_handler_types() -> list:
        """List all registered handler type names."""
        try:
            from handlers import list_handler_types
            return list_handler_types()
        except ImportError:
            return []

    def _order_fields_by_dependency(self, fields_config: dict) -> list:
        """Topological sort of field names based on ``depends_on``.

        A field that declares ``depends_on: "other_field"`` will appear
        after ``other_field`` in the returned list.

        Args:
            fields_config: The ``fields`` section from the workflow config dict.

        Returns:
            list[str]: Field names in dependency order.
        """
        ordered: list[str] = []
        visited: set[str] = set()

        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            field = fields_config.get(name, {})
            dep = field.get("depends_on")
            if dep and dep in fields_config:
                visit(dep)
            ordered.append(name)

        for name in fields_config:
            visit(name)

        return ordered

    # ------------------------------------------------------------------
    # Post-Fill Actions
    # ------------------------------------------------------------------

    def _handle_post_fill(self, post_fill: dict):
        """Handle a post-fill action defined in a field config.

        Supported actions:

            - **click_button**:   Click a button. Params: ``click_selector``.
            - **click_and_wait**: Click a button then wait for a selector.
                                  Params: ``click_selector``, ``wait_selector``,
                                  ``wait_state`` (default ``hidden``), ``timeout``.
            - **wait**:           Pause. Params: ``timeout_ms``.

        Args:
            post_fill: Post-fill action dict from the field config.
        """
        action = post_fill.get("action", "")

        if action == "click_button":
            selector = post_fill.get("click_selector", "")
            if selector:
                logger.debug("Post-fill: clicking '%s'", selector)
                self.page.locator(selector).first.click()

        elif action == "click_and_wait":
            click_sel = post_fill.get("click_selector", "")
            wait_sel = post_fill.get("wait_selector", "")
            wait_state = post_fill.get("wait_state", "hidden")
            timeout = post_fill.get("timeout", 15000)

            if click_sel:
                self.page.locator(click_sel).first.click()

            if wait_sel:
                try:
                    self.page.wait_for_selector(wait_sel, state=wait_state, timeout=timeout)
                except Exception:
                    logger.debug("Post-fill wait_for_selector timed out — falling back to hard wait")
                    self.page.wait_for_timeout(3000)

        elif action == "wait":
            timeout = post_fill.get("timeout_ms", 2000)
            self.page.wait_for_timeout(timeout)

        else:
            logger.warning("Unknown post-fill action '%s' — ignoring", action)

    # ------------------------------------------------------------------
    # Control & Results
    # ------------------------------------------------------------------

    def stop(self):
        """Request a graceful stop of the current execution.

        The engine will finish the current field and then exit the field
        loop. Already-submitted fields will be included in results.
        """
        logger.info("Stop requested — engine will halt after current field")
        self.is_running = False

    def get_results(self) -> dict:
        """Get a summary of execution results.

        Returns:
            dict: Summary with keys:
                total   - number of fields processed
                success - count of successful fields
                failed  - count of failed fields
                results - per-field result dicts
        """
        success_count = sum(
            1 for r in self.results.values() if r.get("success")
        )
        fail_count = sum(
            1 for r in self.results.values() if not r.get("success")
        )
        return {
            "total": len(self.results),
            "success": success_count,
            "failed": fail_count,
            "results": dict(self.results),
        }
