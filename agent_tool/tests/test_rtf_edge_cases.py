"""
TDD-RED: Tests for RTF encoding edge cases in msg_to_pdf conversion.
These tests FAIL initially because the edge cases are not yet handled.
"""
import pytest
from unittest.mock import patch, MagicMock


def test_byte_0x90_in_rtf_body_handled():
    """Mock extract_msg.Message to raise encoding error with byte 0x90"""
    with patch('pdf_merge_tool.converters.msg_to_pdf.extract_msg') as mock_extract:
        mock_extract.Message.side_effect = UnicodeDecodeError('utf-8', b'\x90', 0, 1, 'invalid start byte')
        with patch('pdf_merge_tool.converters.msg_to_pdf._read_msg_html_via_outlook') as mock_com:
            mock_com.return_value = None  # COM also fails

            from pdf_merge_tool.converters.msg_to_pdf import convert_msg_to_pdf
            import tempfile
            d = tempfile.mkdtemp()
            ok, err = convert_msg_to_pdf('test.msg', d)
            # Should handle gracefully (ok=False or fallback to plain text)
            # Should not crash


def test_empty_html_body_returns_none():
    """When htmlBody is empty or None, verify graceful handling"""
    with patch('pdf_merge_tool.converters.msg_to_pdf._read_msg_html_via_outlook') as mock_com:
        mock_com.return_value = None
        with patch('pdf_merge_tool.converters.msg_to_pdf.extract_msg') as mock_extract:
            mock_msg = MagicMock()
            mock_msg.htmlBody = None  # Empty HTML
            mock_msg.body = 'Plain text body'
            mock_msg.attachments = []
            mock_extract.Message.return_value = mock_msg

            from pdf_merge_tool.converters.msg_to_pdf import convert_msg_to_pdf
            import tempfile
            d = tempfile.mkdtemp()
            ok, err = convert_msg_to_pdf('test.msg', d)
            # Should fall back to plain text, not crash


def test_mixed_encoding_message_handled():
    """When htmlBody is bytes with mixed encoding, verify proper decode"""
    with patch('pdf_merge_tool.converters.msg_to_pdf._read_msg_html_via_outlook') as mock_com:
        mock_com.return_value = None
        with patch('pdf_merge_tool.converters.msg_to_pdf.extract_msg') as mock_extract:
            mock_msg = MagicMock()
            # Mixed encoding bytes
            mock_msg.htmlBody = b'<html><body>\x90\xfe Test</body></html>'
            mock_msg.attachments = []
            mock_extract.Message.return_value = mock_msg

            from pdf_merge_tool.converters.msg_to_pdf import convert_msg_to_pdf
            import tempfile
            d = tempfile.mkdtemp()
            ok, err = convert_msg_to_pdf('test.msg', d)
            # Should decode with errors='replace', not crash
