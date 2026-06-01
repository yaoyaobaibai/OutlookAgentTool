import pytest
import ast
import inspect
import os
import re


def test_both_copies_have_identical_css_logic():
    """Verify both _html_body_to_pdf copies process CSS identically (strip then inject)"""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    msg_to_pdf_path = os.path.join(
        base, "pdf_merge_tool", "converters", "msg_to_pdf.py"
    )
    attach_handler_path = os.path.join(
        base, "outlook_agent", "attachment_handler.py"
    )

    with open(msg_to_pdf_path, "r", encoding="utf-8") as f:
        msg_source = f.read()
    with open(attach_handler_path, "r", encoding="utf-8") as f:
        attach_source = f.read()

    # Check CSS strip pattern exists in both
    assert "re.sub" in msg_source and "<style" in msg_source, (
        "msg_to_pdf.py must strip <style> blocks"
    )
    assert "re.sub" in attach_source and "<style" in attach_source, (
        "attachment_handler.py must strip <style> blocks"
    )

    # Check @page CSS uses mm (not pt)
    assert "mm" in msg_source and "@page" in msg_source, (
        "msg_to_pdf.py must use mm in @page"
    )
    assert "mm" in attach_source and "@page" in attach_source, (
        "attachment_handler.py must use mm in @page"
    )

    # Check strip happens BEFORE inject (the 're.sub' for style must come before 'page_css')
    # This is a structural check - we verify the order of operations
    msg_strip_pos = msg_source.find("re.sub(r'<style")
    msg_inject_pos = msg_source.find("page_css")
    attach_strip_pos = attach_source.find("re.sub(r'<style")
    attach_inject_pos = attach_source.find("page_css")

    if msg_strip_pos > 0 and msg_inject_pos > 0:
        assert msg_strip_pos < msg_inject_pos, (
            "msg_to_pdf.py: strip must come BEFORE inject (先清后注)"
        )
    if attach_strip_pos > 0 and attach_inject_pos > 0:
        assert attach_strip_pos < attach_inject_pos, (
            "attachment_handler.py: strip must come BEFORE inject (先清后注)"
        )


def test_both_copies_have_diagnostic_log_before_disable():
    """Verify both copies call logger.info BEFORE _logging.disable()"""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    msg_to_pdf_path = os.path.join(
        base, "pdf_merge_tool", "converters", "msg_to_pdf.py"
    )
    attach_handler_path = os.path.join(
        base, "outlook_agent", "attachment_handler.py"
    )

    with open(msg_to_pdf_path, "r", encoding="utf-8") as f:
        msg_source = f.read()
    with open(attach_handler_path, "r", encoding="utf-8") as f:
        attach_source = f.read()

    # Find logger.info position and _logging.disable position
    msg_log_pos = msg_source.find('logger.info("PATH: _html_body_to_pdf')
    msg_disable_pos = msg_source.find("_logging.disable")
    attach_log_pos = attach_source.find("logger.info(")
    attach_disable_pos = attach_source.find("_logging.disable")

    if msg_log_pos > 0 and msg_disable_pos > 0:
        assert msg_log_pos < msg_disable_pos, (
            "msg_to_pdf.py: diagnostic log must be BEFORE _logging.disable"
        )
    if attach_log_pos > 0 and attach_disable_pos > 0:
        assert attach_log_pos < attach_disable_pos, (
            "attachment_handler.py: diagnostic log must be BEFORE _logging.disable"
        )
