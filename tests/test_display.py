import logging
from unittest.mock import patch, MagicMock

from rich.console import Console

from app.display import ask_permission, console, log


def test_console_is_console_instance():
    assert isinstance(console, Console)


def test_log_is_named_rich():
    assert log.name == "rich"


def test_log_level_is_info_by_default():
    assert log.level <= logging.INFO


def test_library_loggers_silenced():
    for name in ("httpx", "httpcore", "openai", "urllib3"):
        assert logging.getLogger(name).level == logging.WARNING


def test_ask_permission_returns_true_when_confirmed():
    with patch("app.display.console") as mock_console:
        with patch("app.display.Confirm.ask", return_value=True):
            result = ask_permission("bash", {"command": "echo hi"})
    assert result is True


def test_ask_permission_returns_false_when_denied():
    with patch("app.display.console") as mock_console:
        with patch("app.display.Confirm.ask", return_value=False):
            result = ask_permission("read_file", {"file_path": "/tmp/x"})
    assert result is False


def test_ask_permission_prints_tool_name_and_args():
    with patch("app.display.console") as mock_console:
        with patch("app.display.Confirm.ask", return_value=True):
            ask_permission("write_file", {"file_path": "/tmp/out.txt", "content": "hello"})
    mock_console.print.assert_called_once()
    printed = mock_console.print.call_args[0][0]
    assert "write_file" in printed
