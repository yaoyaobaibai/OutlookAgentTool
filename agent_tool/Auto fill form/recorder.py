"""
Browser Action Recorder — CDP-based user operation monitoring.

Records Chrome user interactions, builds CSS selectors, and exports
workflow-compatible JSON summaries for Playwright automation replay.
"""

import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime

from playwright.async_api import async_playwright


# ── Configuration ─────────────────────────────────────────────────────────

CDP_PORT = 9222
OUTPUT_DIR = "recordings"
SESSION_TAG = ""


# ── Helpers ───────────────────────────────────────────────────────────────

def _safe_print(*args, **kwargs):
    """Print with fallback for terminals that cannot handle Unicode (e.g. GBK on Windows)."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # retry with ASCII-safe output
        safe_args = [
            str(a).encode("ascii", errors="replace").decode("ascii") for a in args
        ]
        print(*safe_args, **kwargs)


# ── ANSI color helpers ─────────────────────────────────────────────────────

class _Colors:
    """Terminal ANSI color constants."""
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    @staticmethod
    def colorize(text, color, bold=False):
        prefix = _Colors.BOLD if bold else ""
        return f"{prefix}{color}{text}{_Colors.RESET}"


# ── Event-type colour map ─────────────────────────────────────────────────

_EVENT_STYLES = {
    "click": (_Colors.GREEN, True),
    "input": (_Colors.CYAN, False),
    "select": (_Colors.MAGENTA, False),
    "navigate": (_Colors.BLUE, True),
    "postback": (_Colors.YELLOW, True),
    "page_loaded": (_Colors.GREEN, False),
    "form_submit": (_Colors.YELLOW, False),
    "dialog": (_Colors.RED, False),
    "checkbox": (_Colors.MAGENTA, False),
    "frame_loaded": (_Colors.BLUE, False),
    "wait_visible": (_Colors.GREEN, False),
    "tab_switched": (_Colors.CYAN, False),
    "file_input": (_Colors.YELLOW, False),
    "hover": (_Colors.CYAN, False),
    "scroll": (_Colors.DIM, False),
    "context_menu": (_Colors.RED, False),
    "dblclick": (_Colors.GREEN, True),
    "keydown": (_Colors.CYAN, False),
    "focus": (_Colors.BLUE, False),
    "blur": (_Colors.BLUE, False),
    "popup_opened": (_Colors.YELLOW, True),
    "popup_closed": (_Colors.DIM, False),
    "hidden_input_change": (_Colors.MAGENTA, False),
    "value_changed": (_Colors.CYAN, False),
    "element_appeared": (_Colors.GREEN, False),
}

_EMOJI_MAP = {
    "click": "\U0001f5b1",
    "input": "\u2328\ufe0f",
    "select": "\U0001f4cb",
    "navigate": "\U0001f4c4",
    "postback": "\U0001f310",
    "page_loaded": "\u2705",
    "form_submit": "\U0001f4dd",
    "dialog": "\U0001f4ac",
    "checkbox": "\u2611\ufe0f",
    "frame_loaded": "\U0001f5bc",
    "wait_visible": "\U0001f441\ufe0f",
    "tab_switched": "\U0001f4cc",
    "file_input": "\U0001f4ce",
    "hover": "\u270b",
    "scroll": "\U0001f4dc",
    "context_menu": "\U0001f5a5",
    "dblclick": "\U0001f5b1\U0001f5b1",
    "keydown": "\u2328\ufe0f",
    "focus": "\U0001f3af",
    "blur": "\U0001f6aa",
    "popup_opened": "\U0001faa7",
    "popup_closed": "\U0001faa7",
    "hidden_input_change": "\U0001f441\ufe0f",
    "value_changed": "\U0001f4dd",
    "element_appeared": "\u2728",
}

_LABEL_MAP = {
    "click": "CLICK",
    "input": "INPUT",
    "select": "SELECT",
    "navigate": "NAVIGATE",
    "postback": "POSTBACK",
    "page_loaded": "PAGE LOADED",
    "form_submit": "FORM SUBMIT",
    "dialog": "DIALOG",
    "checkbox": "CHECKBOX",
    "frame_loaded": "FRAME LOADED",
    "wait_visible": "ELEMENT VISIBLE",
    "tab_switched": "TAB SWITCHED",
    "file_input": "FILE INPUT",
    "hover": "HOVER",
    "scroll": "SCROLL",
    "context_menu": "RIGHT-CLICK",
    "dblclick": "DBLCLICK",
    "keydown": "KEY",
    "focus": "FOCUS",
    "blur": "BLUR",
    "popup_opened": "POPUP OPENED",
    "popup_closed": "POPUP CLOSED",
    "hidden_input_change": "HIDDEN INPUT",
    "value_changed": "VALUE CHANGED",
    "element_appeared": "ELEMENT APPEARED",
}


# ── ActionLogger ───────────────────────────────────────────────────────────

class ActionLogger:
    """Records browser actions with timestamps and prints colourised output."""

    def __init__(self):
        self.events: list[dict] = []
        self._start_time: float | None = None

    # -----------------------------------------------------------------
    def start(self):
        """Begin the recording session (set reference timestamp)."""
        self._start_time = time.time()

    # -----------------------------------------------------------------
    def record(self, event_type: str, **details) -> dict:
        """Log a single action event.

        Parameters
        ----------
        event_type : str
            One of the supported action types (click, input, …).
        **details
            Arbitrary key-value pairs stored alongside the event.

        Returns
        -------
        dict
            The created event entry.
        """
        if self._start_time is None:
            self.start()

        elapsed = round(time.time() - self._start_time, 3)
        readable = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        entry: dict[str, object] = {
            "ts": elapsed,
            "time": readable,
            "type": event_type,
        }
        entry.update(details)
        self.events.append(entry)
        self._print_event(entry)
        return entry

    # -----------------------------------------------------------------
    def _print_event(self, entry: dict) -> None:
        """Print a single colour-coded event line to the terminal."""
        ev_type = entry.get("type", "")
        color, bold = _EVENT_STYLES.get(ev_type, (_Colors.RESET, False))
        emoji = _EMOJI_MAP.get(ev_type, "")
        label = _LABEL_MAP.get(ev_type, ev_type.upper())

        ts_str = _Colors.colorize(f"[{entry.get('time', '')}]", _Colors.DIM)
        type_str = _Colors.colorize(f"{emoji} {label}", color, bold=bold)

        details = self._format_details(ev_type, entry)
        _safe_print(f"  {ts_str} {type_str}  {details}")

    # -----------------------------------------------------------------
    @staticmethod
    def _format_details(ev_type: str, entry: dict) -> str:
        """Build the human-readable tail of a log line."""
        _ = ev_type
        selector = entry.get("selector", "")
        text = entry.get("text", "")
        value = entry.get("value", "")
        old_value = entry.get("old_value", "")
        new_value = entry.get("new_value", "")
        sel_text = entry.get("selected_text", "")
        url = entry.get("url", "")
        method = entry.get("method", "")
        title = entry.get("title", "")
        message = entry.get("message", "")
        state = entry.get("state", "")
        files = entry.get("files", "")
        key = entry.get("key", "")
        in_popup = entry.get("in_popup", False)
        popup_selector = entry.get("popup_selector", "")
        popup_type = entry.get("popup_type", "")

        parts = []

        if selector:
            parts.append(f"selector={selector}")
        if text:
            parts.append(f"text=\"{text}\"")
        if old_value:
            parts.append(f"from=\"{old_value}\"")
        if value:
            parts.append(f"value=\"{value}\"")
        if new_value:
            parts.append(f"new_value=\"{new_value}\"")
        if sel_text:
            parts.append(f"selected=\"{sel_text}\"")
        if url:
            parts.append(f"url={url}")
        if method:
            parts.append(f"method={method}")
        if title:
            parts.append(f"title=\"{title}\"")
        if message:
            parts.append(f"msg=\"{message}\"")
        if state:
            parts.append(f"state={state}")
        if files:
            parts.append(f"files={files}")
        if key:
            parts.append(f"key={key}")
        if in_popup:
            parts.append(f"in_popup={popup_type}")
            if popup_selector:
                parts.append(f"popup={popup_selector}")

        if parts:
            return _Colors.colorize(" | ".join(parts), _Colors.DIM)
        # fallback: show the raw details (excluding metadata keys)
        meta = {"ts", "time", "type", "selector", "text", "value", "old_value", "new_value",
                "selected_text", "url", "method", "title", "message", "state", "files",
                "key", "in_popup", "popup_selector", "popup_type"}
        extra = {k: v for k, v in entry.items() if k not in meta}
        if extra:
            return _Colors.colorize(json.dumps(extra, ensure_ascii=False), _Colors.DIM)
        return ""

    # -----------------------------------------------------------------
    def summary(self) -> None:
        """Print a workflow-friendly summary of all recorded events."""
        header = _Colors.colorize(
            "\n\u64cd\u4f5c\u6458\u8981 (\u53ef\u7528\u4e8e workflow.json)",
            _Colors.BOLD + _Colors.CYAN,
            bold=True,
        )
        _safe_print(header)
        _safe_print(_Colors.colorize("\u2500" * 60, _Colors.DIM))

        action_map = {
            "navigate": lambda e: f"\u2192 goto: {e.get('url', '')}",
            "wait_visible": lambda e: f"\u2192 wait_selector: {e.get('selector', '')}",
            "click": lambda e: "\u2192 click: {sel}  [{txt}]".format(
                sel=e.get("selector", ""), txt=e.get("text", "")
            ),
            "input": lambda e: "\u2192 fill: {sel}  <= '{val}'".format(
                sel=e.get("selector", ""), val=e.get("value", "")
            ),
            "select": lambda e: "\u2192 select: {sel}  <= '{val}'".format(
                sel=e.get("selector", ""), val=e.get("value", "")
            ),
            "postback": lambda e: f"\u2192 postback: {e.get('url', '')}",
        }

        for entry in self.events:
            ev_type = entry.get("type", "")
            formatter = action_map.get(ev_type)
            if formatter:
                line = formatter(entry)
                _safe_print(f"  {_Colors.colorize(line, _Colors.GREEN)}")
            else:
                # non-action events shown dimmed
                ts = entry.get("ts", "")
                label = _LABEL_MAP.get(ev_type, ev_type)
                line = f"  [{ts}s] {label}"
                _safe_print(f"  {_Colors.colorize(line, _Colors.DIM)}")

        _safe_print()

    # -----------------------------------------------------------------
    def save(self, filepath: str) -> None:
        """Export recorded events to a JSON file.

        Parameters
        ----------
        filepath : str
            Destination path for the JSON file.
        """
        session_tag = getattr(self, "session_tag", "")
        output = {
            "recorded_at": datetime.now().isoformat(),
            "total_events": len(self.events),
            "session_tag": session_tag,
            "events": list(self.events),
        }

        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(output, fh, ensure_ascii=False, indent=2)

        _safe_print(
            _Colors.colorize(
                f"\u2713 Saved {len(self.events)} events \u2192 {filepath}",
                _Colors.GREEN,
            )
        )


# ── SelectorBuilder ───────────────────────────────────────────────────────

class SelectorBuilder:
    """Static utility that builds the *best* CSS selector from DOM element data."""

    _PREFERRED_ATTRS = (
        "type",
        "role",
        "aria-label",
        "data-testid",
        "placeholder",
        "value",
    )

    @staticmethod
    def build(
        tag: str,
        attrs: dict[str, str],
        text: str = "",
        nth: int = -1,
    ) -> str:
        """Return the most specific CSS selector possible for the element.

        Parameters
        ----------
        tag : str
            HTML tag name (lowercase).
        attrs : dict
            Map of attribute name → value for the element.
        text : str
            Inner text content (may be empty).
        nth : int
            Zero-based index among siblings; ``-1`` means unused.

        Returns
        -------
        str
            A CSS selector string (e.g. ``#submit-btn``, ``div.btn-primary``).
        """
        selector = tag

        # 1. id — best possible anchor
        elem_id = attrs.get("id", "")
        if elem_id and not re.match(r"^\d", elem_id):
            return f"#{elem_id}"

        # 2. name
        name_val = attrs.get("name", "")
        if name_val:
            selector += f'[name="{name_val}"]'

        # 3. other semantic attributes
        for attr in SelectorBuilder._PREFERRED_ATTRS:
            val = attrs.get(attr, "")
            if val:
                selector += f'[{attr}="{val}"]'

        # 4. class (first 3 *meaningful* classes)
        cls_raw = attrs.get("class", "")
        if cls_raw:
            meaningful = [
                c
                for c in cls_raw.split()
                if len(c) > 1
                and not c.startswith("ui-")
                and not c.startswith("_")
            ]
            for c in meaningful[:3]:
                selector += f".{c}"

        # 5. text content (max 40 chars)
        txt_clean = text.strip()
        if txt_clean:
            txt_trunc = txt_clean[:40]
            # escape internal double-quotes
            txt_safe = txt_trunc.replace('"', '\\"')
            selector += f':has-text("{txt_safe}")'

        # 6. nth-child
        if nth >= 0:
            selector += f":nth-child({nth + 1})"

        return selector


# ── PageMonitor ────────────────────────────────────────────────────────────

class PageMonitor:
    """Monitors browser-level events via CDP: navigation, network, dialogs, tabs."""

    def __init__(self, page, logger: ActionLogger):
        self.page = page
        self.log = logger
        self._last_url = ""
        self._cdp = None

    async def start(self):
        """Initialize CDP session and start all listeners."""
        self._last_url = self.page.url
        self._cdp = await self.page.context.new_cdp_session(self.page)
        await self._setup_cdp_listeners()
        await self._inject_dom_listeners()
        self.log.record("page_loaded", url=self.page.url, title=await self.page.title())

    async def _setup_cdp_listeners(self):
        """Register all CDP event handlers and enable required domains."""

        # Event listeners (all use asyncio.ensure_future for async handlers)
        self._cdp.on("Page.frameNavigated", lambda params: asyncio.ensure_future(
            self._on_frame_navigated(params)
        ))
        self._cdp.on("Network.requestWillBeSent", lambda params: asyncio.ensure_future(
            self._on_request(params)
        ))
        self._cdp.on("Network.responseReceived", lambda params: asyncio.ensure_future(
            self._on_response(params)
        ))
        self._cdp.on("Page.javascriptDialogOpening", lambda params: asyncio.ensure_future(
            self._on_dialog(params)
        ))
        self._cdp.on("Target.targetCreated", lambda params: asyncio.ensure_future(
            self._on_target_created(params)
        ))

        # Enable CDP domains
        await self._cdp.send("Page.enable")
        await self._cdp.send("Network.enable")
        await self._cdp.send("Runtime.enable")
        await self._cdp.send("Target.setAutoAttach", {
            "autoAttach": True,
            "flatten": True,
            "waitForDebuggerOnStart": False,
        })

    # -----------------------------------------------------------------
    async def _inject_dom_listeners(self):
        """Inject DOM event listeners via CDP bindings (works with CSP and CDP connections)."""

        # Register CDP binding for JS -> Python communication
        await self._cdp.send("Runtime.addBinding", {"name": "recorderPush"})

        # Listen for binding calls
        self._cdp.on("Runtime.bindingCalled", lambda params: asyncio.ensure_future(
            self._on_cdp_binding(params)
        ))

        js_code = """
        (() => {
            if (window.__recorder_injected) return;
            window.__recorder_injected = true;

            // Use CDP binding instead of expose_function
            window.__recorder_push = function(type, data) {
                try { window.recorderPush(JSON.stringify({type: type, data: data})); } catch(e) {}
            };

            // --- Monkey-patch HTMLInputElement.value to catch ALL value changes ---
            (function() {
                try {
                    const inputProto = HTMLInputElement.prototype;
                    const textAreaProto = HTMLTextAreaElement.prototype;
                    const origInputDescriptor = Object.getOwnPropertyDescriptor(inputProto, 'value');
                    const origTextareaDescriptor = Object.getOwnPropertyDescriptor(textAreaProto, 'value');

                    function patchValueSetter(proto, descriptor, elementType) {
                        if (!descriptor || !descriptor.set) return;
                        const origSetter = descriptor.set;
                        Object.defineProperty(proto, 'value', {
                            set: function(val) {
                                const oldVal = this.value;
                                origSetter.call(this, val);
                                if (oldVal !== val && this.isConnected) {
                                    window.__recorder_push('value_changed', {
                                        selector: this.id ? '#' + this.id : (this.name ? '[name="' + this.name + '"]' : elementType),
                                        old_value: oldVal !== undefined && oldVal !== null ? oldVal.toString().substring(0, 200) : '',
                                        new_value: val !== undefined && val !== null ? val.toString().substring(0, 200) : '',
                                        input_id: this.id || '',
                                        input_name: this.name || '',
                                    });
                                }
                            },
                            get: function() {
                                return descriptor.get.call(this);
                            },
                            configurable: true,
                        });
                    }

                    patchValueSetter(inputProto, origInputDescriptor, 'input');
                    patchValueSetter(textAreaProto, origTextareaDescriptor, 'textarea');
                } catch(e) {
                    // Monkey-patch failed - value tracking degraded
                    console.warn('Value tracking patch failed:', e);
                }
            })();

            // --- Poll all inputs for value changes every 1 second (reliable fallback) ---
            (function() {
                try {
                    setInterval(function() {
                        document.querySelectorAll('input:not([type="hidden"]):not([type="file"]), textarea, select').forEach(function(el) {
                            var trackedKey = '__recorder_poll_' + (el.id || el.name || Math.random());
                            var oldVal = el[trackedKey];
                            var newVal = el.value;
                            if (oldVal !== undefined && oldVal !== newVal) {
                                window.__recorder_push('value_changed', {
                                    selector: el.id ? '#' + el.id : (el.name ? '[name="' + el.name + '"]' : el.tagName.toLowerCase()),
                                    old_value: oldVal !== null && oldVal !== undefined ? oldVal.toString().substring(0, 200) : '',
                                    new_value: newVal !== null && newVal !== undefined ? newVal.toString().substring(0, 200) : '',
                                    input_id: el.id || '',
                                    input_name: el.name || '',
                                });
                            }
                            el[trackedKey] = newVal;
                        });
                    }, 1000);
                } catch(e) {
                    // Polling failed - value tracking degraded
                }
            })();

            function getSelector(el) {
                if (!el || el === document || el === window) return 'document';
                let path = [];
                let cur = el;
                while (cur && cur !== document && cur !== window) {
                    let sel = cur.tagName ? cur.tagName.toLowerCase() : '';
                    if (cur.id) {
                        path.unshift('#' + CSS.escape(cur.id));
                        break;
                    }
                    if (cur.name) {
                        sel += '[name="' + cur.name + '"]';
                    }
                    if (cur.className && typeof cur.className === 'string') {
                        let cls = cur.className.trim().split(/\\s+/).filter(c => c && !c.startsWith('_') && c.length > 1);
                        if (cls.length) sel += '.' + cls.slice(0, 2).join('.');
                    }
                    path.unshift(sel);
                    cur = cur.parentElement;
                }
                return path.join(' > ');
            }

            function getText(el) {
                return (el.textContent || '').trim().substring(0, 100);
            }

            function getAttrs(el) {
                let attrs = {};
                for (let a of ['id', 'name', 'type', 'class', 'role', 'aria-label', 'placeholder', 'value', 'href', 'title', 'data-testid']) {
                    let v = el.getAttribute(a);
                    if (v) attrs[a] = v;
                }
                return attrs;
            }

            function isTrusted(e) { return e.isTrusted; }

            // --- Click ---
            document.addEventListener('click', (e) => {
                if (!isTrusted(e)) return;
                let el = e.target;
                let popupInfo = { in_popup: false, popup_selector: '', popup_type: '' };
                let cur = el;
                while (cur && cur !== document) {
                    let cls = cur.className || '';
                    if (typeof cls === 'string') {
                        if (cls.match(/(^|\\s)(modal|popup|dialog|overlay)(\\s|$)/i)) {
                            popupInfo = { in_popup: true, popup_selector: cur.id ? '#' + cur.id : cur.tagName.toLowerCase(), popup_type: 'modal' };
                            break;
                        }
                        if (cls.match(/(^|\\s)(dropdown|menu|select-dropdown|options)(\\s|$)/i)) {
                            popupInfo = { in_popup: true, popup_selector: cur.id ? '#' + cur.id : '.' + cls.split(/\\s+/).filter(c=>c&&!c.startsWith('_'))[0], popup_type: 'dropdown' };
                            break;
                        }
                        if (cls.match(/(^|\\s)(datepicker|calendar|picker)(\\s|$)/i)) {
                            popupInfo = { in_popup: true, popup_selector: cur.id ? '#' + cur.id : cur.tagName.toLowerCase(), popup_type: 'datepicker' };
                            break;
                        }
                    }
                    cur = cur.parentElement;
                }
                window.__recorder_push('click', {
                    selector: getSelector(el),
                    tag: el.tagName ? el.tagName.toLowerCase() : '',
                    text: getText(el),
                    attrs: JSON.stringify(getAttrs(el)),
                    x: e.clientX, y: e.clientY,
                    in_popup: popupInfo.in_popup,
                    popup_selector: popupInfo.popup_selector,
                    popup_type: popupInfo.popup_type,
                });
            }, true);

            // --- Input (with before/after) ---
            document.addEventListener('input', (e) => {
                if (!isTrusted(e)) return;
                let el = e.target;
                if (!el || !el.tagName) return;
                let tag = el.tagName.toLowerCase();
                if (tag === 'input' || tag === 'textarea') {
                    if (!el.__recorder_old_value) el.__recorder_old_value = el.defaultValue || '';
                    let oldVal = el.__recorder_old_value;
                    let newVal = el.value;
                    if (oldVal !== newVal) {
                        window.__recorder_push('input', {
                            selector: getSelector(el), tag: tag,
                            old_value: oldVal.substring(0, 200),
                            value: newVal.substring(0, 200),
                            type: el.type || 'text',
                        });
                        el.__recorder_old_value = newVal;
                    }
                }
            }, true);

            // --- Change (select/checkbox/file) ---
            document.addEventListener('change', (e) => {
                if (!isTrusted(e)) return;
                let el = e.target;
                if (!el || !el.tagName) return;
                let tag = el.tagName.toLowerCase();
                if (tag === 'select') {
                    window.__recorder_push('select', {
                        selector: getSelector(el),
                        value: Array.from(el.selectedOptions).map(o=>o.value).join(','),
                        selected_text: Array.from(el.selectedOptions).map(o=>o.text).join(','),
                    });
                } else if (el.type === 'checkbox' || el.type === 'radio') {
                    window.__recorder_push('checkbox', { selector: getSelector(el), state: el.checked ? 'checked' : 'unchecked', value: el.value });
                } else if (tag === 'input' && el.type === 'file') {
                    window.__recorder_push('file_input', { selector: getSelector(el), files: Array.from(el.files).map(f=>f.name).join(', ') || '(cleared)' });
                }
            }, true);

            // --- Submit ---
            document.addEventListener('submit', (e) => {
                if (!isTrusted(e)) return;
                window.__recorder_push('form_submit', { selector: getSelector(e.target), attrs: JSON.stringify(getAttrs(e.target)) });
            }, true);

            // --- Focus/Blur ---
            document.addEventListener('focusin', (e) => {
                if (!isTrusted(e)) return;
                let el = e.target;
                if (el.tagName && ['input','select','textarea'].includes(el.tagName.toLowerCase())) {
                    window.__recorder_push('focus', { selector: getSelector(el) });
                }
            }, true);
            document.addEventListener('focusout', (e) => {
                if (!isTrusted(e)) return;
                let el = e.target;
                if (el.tagName && ['input','select','textarea'].includes(el.tagName.toLowerCase())) {
                    window.__recorder_push('blur', { selector: getSelector(el) });
                }
            }, true);

            // --- Key events ---
            document.addEventListener('keydown', (e) => {
                if (!isTrusted(e)) return;
                let el = e.target;
                if (['Enter','Tab','Escape','F2','ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(e.key) && el.tagName) {
                    window.__recorder_push('keydown', { key: e.key === ' ' ? 'Space' : e.key, selector: getSelector(el) });
                }
            }, true);

            // --- MutationObserver ---
            if (window.MutationObserver) {
                let prevValues = new Map();
                let observer = new MutationObserver((mutations) => {
                    for (let m of mutations) {
                        if (m.type === 'attributes' && m.target) {
                            let el = m.target;
                            let attr = m.attributeName;
                            if (attr === 'class') {
                                let cls = el.className || '';
                                // Popup-related classes (standard + ASP.NET AJAX CalendarExtender)
                                let popupOpened = cls.match(/(^|\\s)(active|visible|open|show|ajax__calendar|calendar|datepicker|popup|modal|dialog|overlay|drop|menu|combo)(\\s|$)/i);
                                if (popupOpened) {
                                    let sel = el.id ? '#' + el.id : el.tagName.toLowerCase();
                                    window.__recorder_push('popup_opened', { selector: sel, tag: el.tagName.toLowerCase(), class_name: popupOpened[0].trim() });
                                }
                                if (m.oldValue) {
                                    let hadPopup = m.oldValue.match(/(active|visible|open|show|ajax__calendar|calendar|datepicker|popup|modal|dialog|overlay|drop|menu|combo)/i);
                                    let hasPopup = cls.match(/(active|visible|open|show|ajax__calendar|calendar|datepicker|popup|modal|dialog|overlay|drop|menu|combo)/i);
                                    if (hadPopup && !hasPopup) {
                                        let sel = el.id ? '#' + el.id : el.tagName.toLowerCase();
                                        window.__recorder_push('popup_closed', { selector: sel, tag: el.tagName.toLowerCase() });
                                    }
                                }
                            }
                            // NOTE: value attribute changes via setAttribute() — most widgets
                            // set .value directly (property), which does NOT trigger this observer.
                            // Primary value tracking is done via focusin/focusout handlers above.
                            // This MutationObserver path is a backup for code that uses setAttribute().
                            if (attr === 'value' && el.tagName === 'INPUT') {
                                let oldVal = prevValues.get(el) || '';
                                let newVal = el.value || '';
                                prevValues.set(el, newVal);
                                if (oldVal !== newVal) {
                                    let eventName = (el.type === 'hidden') ? 'hidden_input_change' : 'value_changed';
                                    window.__recorder_push(eventName, {
                                        selector: el.id ? '#' + el.id : (el.name ? '[name="' + el.name + '"]' : el.tagName.toLowerCase()),
                                        old_value: oldVal.substring(0, 200),
                                        new_value: newVal.substring(0, 200),
                                        input_id: el.id || '',
                                        input_name: el.name || '',
                                    });
                                }
                            }

                            // Track style.display changes (popup show/hide via display)
                            if (attr === 'style' && m.target) {
                                let el = m.target;
                                let oldStyle = m.oldValue || '';
                                let newStyle = el.getAttribute('style') || '';
                                let oldDisplay = oldStyle.match(/display\\s*:\\s*(none|block|inline|flex)/i);
                                let newDisplay = newStyle.match(/display\\s*:\\s*(none|block|inline|flex)/i);
                                if (oldDisplay && oldDisplay[1] === 'none' && newDisplay && newDisplay[1] !== 'none') {
                                    let sel = el.id ? '#' + el.id : el.tagName.toLowerCase();
                                    window.__recorder_push('popup_opened', { selector: sel, tag: el.tagName.toLowerCase() });
                                }
                                if (oldDisplay && oldDisplay[1] !== 'none' && newDisplay && newDisplay[1] === 'none') {
                                    let sel = el.id ? '#' + el.id : el.tagName.toLowerCase();
                                    window.__recorder_push('popup_closed', { selector: sel, tag: el.tagName.toLowerCase() });
                                }
                            }
                        }
                        for (let node of m.addedNodes || []) {
                            if (node.nodeType === 1) {
                                if (node.id) {
                                    window.__recorder_push('element_appeared', { selector: '#' + node.id, tag: node.tagName.toLowerCase() });
                                }
                                if (node.querySelectorAll) {
                                    node.querySelectorAll('[id]').forEach(el => {
                                        if (el.id) window.__recorder_push('element_appeared', { selector: '#' + el.id, tag: el.tagName.toLowerCase() });
                                    });
                                }
                                // Check if this new node looks like a popup/dialog
                                let nodeCls = node.className || '';
                                if (typeof nodeCls === 'string' && nodeCls.match(/(popup|modal|dialog|overlay|calendar|datepicker|menu|dropdown|combo|panel|window|layer)/i)) {
                                    let sel = node.id ? '#' + node.id : node.tagName.toLowerCase();
                                    window.__recorder_push('popup_opened', { selector: sel, tag: node.tagName.toLowerCase() });
                                }
                            }
                        }
                    }
                });
                observer.observe(document.body || document.documentElement, {
                    childList: true, attributes: true, attributeOldValue: true,
                    attributeFilter: ['class', 'style'], subtree: true,
                });
            }
        })();
        """

        # Use addScriptToEvaluateOnNewDocument so it runs on every page (handles SPA navigations)
        await self._cdp.send("Page.addScriptToEvaluateOnNewDocument", {"source": js_code})

        # Also evaluate on the current page immediately
        try:
            await self.page.evaluate(js_code)
        except Exception as e:
            self.log.record("log", message=f"JS injection eval warning: {e}")

    # ---- CDP Event Handlers ----

    async def _on_frame_navigated(self, params):
        """Handle page navigation (URL changes)."""
        frame = params.get("frame", {})
        url = frame.get("url", "")
        if not url or url == "about:blank":
            return
        if frame.get("parentId"):  # Sub-frame / iframe
            self.log.record("frame_loaded", url=url)
            return
        # Main frame navigation
        if url != self._last_url:
            self.log.record("navigate", url=url)
            self._last_url = url

    async def _on_request(self, params):
        """Handle network requests — detect POST (postback)."""
        req = params.get("request", {})
        method = req.get("method", "GET")
        url = req.get("url", "")
        if method == "POST":
            post_data = req.get("postData", "")
            self.log.record("postback",
                url=url,
                method=method,
                post_data=post_data[:500] if post_data else "",
                resource_type=params.get("type", ""),
            )

    async def _on_response(self, params):
        """Handle network responses — detect page loads."""
        resp = params.get("response", {})
        url = resp.get("url", "")
        status = resp.get("status", 0)
        mime = (resp.get("mimeType", "") or "")
        if status == 200 and "text/html" in mime:
            self.log.record("page_loaded", url=url, status=status)

    async def _on_dialog(self, params):
        """Handle JavaScript dialogs (alert/confirm/prompt)."""
        self.log.record("dialog",
            type=params.get("type", ""),
            message=params.get("message", ""),
        )

    async def _on_target_created(self, params):
        """Handle new tabs / popup windows."""
        target_info = params.get("targetInfo", {})
        if target_info.get("type") == "page":
            url = target_info.get("url", "")
            title = target_info.get("title", "")
            if url and url != "about:blank":
                self.log.record("tab_switched", url=url, title=title)

    # -----------------------------------------------------------------
    async def _on_cdp_binding(self, params):
        """Receive events from CDP Runtime.bindingCalled."""
        try:
            name = params.get("name", "")
            if name != "recorderPush":
                return
            payload = params.get("payload", "{}")
            import json
            data = json.loads(payload)
            event_type = data.get("type", "")
            event_data = data.get("data", {})
            await self._on_js_event(event_type, event_data)
        except Exception:
            pass  # Silently ignore malformed binding calls

    # ---- JS DOM Event Handlers ----

    async def _on_js_event(self, event_type: str, data: dict):
        """Receive events from injected JS and dispatch to typed handlers."""
        handler_map = {
            "click": self._on_dom_click,
            "dblclick": self._on_dom_dblclick,
            "context_menu": self._on_dom_contextmenu,
            "input": self._on_dom_input,
            "select": self._on_dom_select,
            "checkbox": self._on_dom_checkbox,
            "file_input": self._on_dom_file,
            "form_submit": self._on_dom_submit,
            "focus": self._on_dom_focus,
            "blur": self._on_dom_blur,
            "keydown": self._on_dom_keydown,
            "wait_visible": self._on_dom_wait_visible,
        }
        handler = handler_map.get(event_type)
        if handler:
            await handler(data)

    async def _on_dom_click(self, d: dict):
        self.log.record("click",
            selector=d.get("selector", ""),
            text=d.get("text", ""),
            tag=d.get("tag", ""),
            attrs=d.get("attrs", ""),
            x=d.get("x"),
            y=d.get("y"),
            in_popup=d.get("in_popup", False),
            popup_selector=d.get("popup_selector", ""),
            popup_type=d.get("popup_type", ""),
        )

    async def _on_dom_dblclick(self, d: dict):
        self.log.record("dblclick",
            selector=d.get("selector", ""),
            text=d.get("text", ""),
        )

    async def _on_dom_contextmenu(self, d: dict):
        self.log.record("context_menu",
            selector=d.get("selector", ""),
        )

    async def _on_dom_input(self, d: dict):
        self.log.record("input",
            selector=d.get("selector", ""),
            old_value=d.get("old_value", ""),
            value=d.get("value", ""),
            type=d.get("type", "text"),
        )

    async def _on_dom_select(self, d: dict):
        self.log.record("select",
            selector=d.get("selector", ""),
            value=d.get("value", ""),
            selected_text=d.get("selected_text", ""),
        )

    async def _on_dom_checkbox(self, d: dict):
        self.log.record("checkbox",
            selector=d.get("selector", ""),
            state=d.get("state", ""),
            value=d.get("value", ""),
        )

    async def _on_dom_file(self, d: dict):
        self.log.record("file_input",
            selector=d.get("selector", ""),
            files=d.get("files", ""),
        )

    async def _on_dom_submit(self, d: dict):
        self.log.record("form_submit",
            selector=d.get("selector", ""),
            attrs=d.get("attrs", ""),
        )

    async def _on_dom_focus(self, d: dict):
        self.log.record("focus", selector=d.get("selector", ""))

    async def _on_dom_blur(self, d: dict):
        self.log.record("blur", selector=d.get("selector", ""))

    async def _on_dom_keydown(self, d: dict):
        self.log.record("keydown",
            key=d.get("key", ""),
            selector=d.get("selector", ""),
        )

    async def _on_dom_wait_visible(self, d: dict):
        self.log.record("wait_visible",
            selector=d.get("selector", ""),
            tag=d.get("tag", ""),
        )


# ── Chrome Connection ─────────────────────────────────────────────────────

def _find_chrome_path():
    """Detect the installed Chrome executable path."""
    import shutil

    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return shutil.which("chrome") or shutil.which("google-chrome")


async def _launch_chrome_debug():
    """Launch a new Chrome instance with remote debugging enabled.

    Returns
    -------
    subprocess.Popen or None
    """
    import subprocess
    import tempfile

    chrome_path = _find_chrome_path()
    if not chrome_path:
        return None

    user_data_dir = os.path.join(tempfile.gettempdir(), "recorder_chrome_profile")
    os.makedirs(user_data_dir, exist_ok=True)

    try:
        proc = subprocess.Popen(
            [
                chrome_path,
                f"--remote-debugging-port={CDP_PORT}",
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return proc
    except Exception:
        return None


async def find_chrome_tab(playwright):
    """Connect to Chrome via CDP (auto-launch if needed) and pick a tab."""
    chrome_proc = None

    for attempt in range(2):
        try:
            browser = await playwright.chromium.connect_over_cdp(
                f"http://localhost:{CDP_PORT}"
            )
            break
        except Exception:
            if attempt == 0:
                _safe_print(
                    _Colors.colorize(
                        "Chrome not in debug mode. Auto-launching...",
                        _Colors.YELLOW,
                    )
                )
                chrome_proc = await _launch_chrome_debug()
                if chrome_proc is None:
                    _safe_print(
                        _Colors.colorize(
                            "\u274c Could not find or launch Chrome.",
                            _Colors.RED,
                            bold=True,
                        )
                    )
                    return None, None
                await asyncio.sleep(3)
            else:
                _safe_print(
                    _Colors.colorize(
                        "\u274c Cannot connect to Chrome. "
                        "Please close all Chrome windows and try again.",
                        _Colors.RED,
                        bold=True,
                    )
                )
                return None, None

    # Gather all pages across all browser contexts
    all_pages = []
    for ctx in browser.contexts:
        all_pages.extend(ctx.pages)

    if not all_pages:
        _safe_print(_Colors.colorize("\u274c No open tabs found.", _Colors.RED))
        await browser.close()
        return None, None

    if len(all_pages) == 1:
        page = all_pages[0]
        title = await page.title()
        _safe_print(
            _Colors.colorize(
                f"\u2705 Connected: {title or '(no title)'}",
                _Colors.GREEN,
            )
        )
        return browser, page

    # Multiple tabs — let user choose
    _safe_print(
        _Colors.colorize(
            f"\n\U0001f4cc Found {len(all_pages)} tabs:\n",
            _Colors.CYAN,
            bold=True,
        )
    )
    for i, p in enumerate(all_pages):
        title = await p.title()
        url = p.url
        _safe_print(f"  [{i}] {title or '(no title)'}")
        _safe_print(f"      URL: {url[:120]}")

    _safe_print()
    while True:
        try:
            choice = input(
                f"Select tab to monitor [0-{len(all_pages) - 1}]: "
            ).strip()
            idx = int(choice)
            if 0 <= idx < len(all_pages):
                page = all_pages[idx]
                title = await page.title()
                _safe_print(
                    _Colors.colorize(
                        f"\u2705 Selected: {title or '(no title)'}",
                        _Colors.GREEN,
                    )
                )
                return browser, page
        except (ValueError, IndexError):
            pass
        _safe_print(_Colors.colorize("  Invalid choice, try again.", _Colors.RED))


# ── Main Entry Point ──────────────────────────────────────────────────────

async def main():
    """Connect to Chrome, start monitoring, and record all user actions."""
    _safe_print("=" * 70)
    _safe_print(_Colors.colorize(
        "  Browser Action Recorder \u2014 \u6d4f\u89c8\u5668\u64cd\u4f5c\u8bb0\u5f55\u5668",
        _Colors.BOLD + _Colors.CYAN,
        bold=True,
    ))
    _safe_print("=" * 70)
    _safe_print()
    _safe_print(f"  Port: localhost:9222")
    _safe_print("  \u64cd\u4f5c: \u5728 Chrome \u4e2d\u6267\u884c\u64cd\u4f5c\uff0c\u672c\u7a0b\u5e8f\u5c06\u81ea\u52a8\u8bb0\u5f55")
    _safe_print("  \u505c\u6b62: Ctrl+C")
    _safe_print()

    log = ActionLogger()
    log.start()

    async with async_playwright() as playwright:
        browser, page = await find_chrome_tab(playwright)
        if not page:
            return

        monitor = PageMonitor(page, log)
        await monitor.start()

        _safe_print()
        _safe_print(_Colors.colorize(
            "\U0001f7e2 Monitoring started \u2014 perform actions in Chrome...\n",
            _Colors.GREEN,
            bold=True,
        ))

        try:
            while True:
                await asyncio.sleep(1)
                # Check if the page is still alive
                try:
                    _ = await page.title()
                except Exception:
                    _safe_print(
                        _Colors.colorize(
                            "\n\u26a0\ufe0f Page closed. Stopping monitor.",
                            _Colors.YELLOW,
                        )
                    )
                    break
        except (KeyboardInterrupt, asyncio.CancelledError):
            _safe_print(
                _Colors.colorize(
                    "\n\n\u23f1 User interrupted.\n",
                    _Colors.YELLOW,
                    bold=True,
                )
            )
        finally:
            await browser.close()

    # Output results
    _safe_print()
    log.summary()

    # Save log
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tag = f"_{SESSION_TAG}" if SESSION_TAG else ""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recorder_log{tag}_{ts}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    log.save(filepath)

    _safe_print(f"\n\U0001f4ca Total events recorded: {len(log.events)}")


if __name__ == "__main__":
    asyncio.run(main())
