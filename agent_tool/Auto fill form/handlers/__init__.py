"""
Handlers Package - Built-in field type handlers for FormFiller workflow engine.

Each handler implements the BaseHandler interface and handles one field type.
"""

__version__ = "1.0"

from .base_handler import BaseHandler

# Handler registry
_handler_registry = {}

def register_handler(handler_type: str, handler_class):
    """Register a handler for a given field type."""
    _handler_registry[handler_type] = handler_class

def get_handler(handler_type: str):
    """Get handler class by type name."""
    if handler_type not in _handler_registry:
        raise KeyError(f"Unknown handler type: '{handler_type}'. Available: {list(_handler_registry.keys())}")
    return _handler_registry[handler_type]

def get_handler_for_field(field_config: dict):
    """Get handler class from field config's 'type' field."""
    field_type = field_config.get("type", "input")
    return get_handler(field_type)

def list_handler_types():
    """List all registered handler type names."""
    return list(_handler_registry.keys())

# Import and register all built-in handlers
from .input_handler import InputHandler
from .select_handler import SelectHandler
from .checkbox_handler import CheckboxHandler
from .autocomplete_handler import AutoCompleteHandler
from .datepicker_handler import DatePickerHandler
from .popup_search_handler import PopupSearchHandler
from .file_upload_handler import FileUploadHandler

register_handler("input", InputHandler)
register_handler("select", SelectHandler)
register_handler("checkbox", CheckboxHandler)
register_handler("autocomplete", AutoCompleteHandler)
register_handler("datepicker", DatePickerHandler)
register_handler("popup_search", PopupSearchHandler)
register_handler("file_upload", FileUploadHandler)
