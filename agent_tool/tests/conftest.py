import pytest
from pathlib import Path


@pytest.fixture
def test_msg_path() -> Path:
    """Return path to a test .msg file from project root."""
    return Path(__file__).parent.parent / "测试" / "RE PDF文件合并-0529.msg"


@pytest.fixture
def sample_html_body() -> str:
    """Return a minimal valid HTML string with CJK content."""
    return "<html><body><p>测试邮件</p></body></html>"


@pytest.fixture
def page_size_a4() -> tuple[float, float]:
    """Return A4 page size in points (595.28 x 841.89)."""
    return (595.28, 841.89)
