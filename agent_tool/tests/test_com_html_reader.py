"""
TDD-RED tests for _read_msg_html_via_outlook().

These tests MUST FAIL initially — the function doesn't exist yet (RED state).
"""
import pytest
from unittest.mock import patch, MagicMock


def test_read_html_via_outlook_returns_html_string():
    """_read_msg_html_via_outlook returns non-empty string for valid .msg file"""
    from pdf_merge_tool.converters.msg_to_pdf import _read_msg_html_via_outlook

    with patch('pdf_merge_tool.converters.msg_to_pdf.win32com') as mock_com:
        mock_app = MagicMock()
        mock_mail = MagicMock()
        mock_mail.HTMLBody = '<html><body><p>Test email</p></body></html>'
        mock_app.Session.OpenSharedItem.return_value = mock_mail
        mock_com.client.Dispatch.return_value = mock_app

        # Since the function doesn't exist yet, this import will FAIL (RED)
        result = _read_msg_html_via_outlook('dummy_path.msg')
        assert isinstance(result, str)
        assert len(result) > 0


def test_read_html_via_outlook_handles_missing_file():
    """_read_msg_html_via_outlook returns None for nonexistent file"""
    from pdf_merge_tool.converters.msg_to_pdf import _read_msg_html_via_outlook

    result = _read_msg_html_via_outlook('nonexistent_file.msg')
    assert result is None


def test_read_html_via_outlook_handles_com_unavailable():
    """_read_msg_html_via_outlook returns None when COM fails"""
    from pdf_merge_tool.converters.msg_to_pdf import _read_msg_html_via_outlook

    with patch('pdf_merge_tool.converters.msg_to_pdf.win32com') as mock_com:
        mock_com.client.Dispatch.side_effect = Exception("COM not available")
        result = _read_msg_html_via_outlook('test.msg')
        assert result is None
