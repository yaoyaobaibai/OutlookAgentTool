"""
TDD-RED: Tests for dual-path HTML extraction (COM first, extract_msg fallback).

All tests should FAIL initially because convert_msg_to_pdf does not exist yet.
"""

import pytest
from unittest.mock import patch, MagicMock, call


def test_extraction_tries_com_first():
    """Verify COM path is tried BEFORE extract_msg"""
    with patch('pdf_merge_tool.converters.msg_to_pdf._read_msg_html_via_outlook') as mock_com:
        mock_com.return_value = '<html>COM HTML</html>'
        with patch('pdf_merge_tool.converters.msg_to_pdf.extract_msg') as mock_extract:
            # Call the function that should try COM first
            from pdf_merge_tool.converters.msg_to_pdf import convert_msg_to_pdf
            import tempfile, os
            d = tempfile.mkdtemp()
            # This import will fail — RED state
            ok, err = convert_msg_to_pdf('test.msg', d)
            # COM should be called
            mock_com.assert_called_once()


def test_extraction_falls_back_on_com_failure():
    """When COM returns None, extract_msg fallback is used"""
    with patch('pdf_merge_tool.converters.msg_to_pdf._read_msg_html_via_outlook') as mock_com:
        mock_com.return_value = None  # COM fails
        with patch('pdf_merge_tool.converters.msg_to_pdf.extract_msg') as mock_extract:
            mock_msg = MagicMock()
            mock_msg.htmlBody = '<html>Fallback HTML</html>'
            mock_msg.attachments = []
            mock_extract.Message.return_value = mock_msg

            from pdf_merge_tool.converters.msg_to_pdf import convert_msg_to_pdf
            import tempfile
            d = tempfile.mkdtemp()
            ok, err = convert_msg_to_pdf('test.msg', d)
            # extract_msg should be called as fallback
            mock_extract.Message.assert_called()


def test_extraction_returns_html_on_com_success():
    """When COM succeeds, returns that HTML without calling extract_msg"""
    with patch('pdf_merge_tool.converters.msg_to_pdf._read_msg_html_via_outlook') as mock_com:
        mock_com.return_value = '<html>COM Success</html>'
        with patch('pdf_merge_tool.converters.msg_to_pdf.extract_msg') as mock_extract:
            from pdf_merge_tool.converters.msg_to_pdf import convert_msg_to_pdf
            import tempfile
            d = tempfile.mkdtemp()
            ok, err = convert_msg_to_pdf('test.msg', d)
            # extract_msg should NOT be called
            mock_extract.Message.assert_not_called()
