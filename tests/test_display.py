import logging
from unittest.mock import patch, MagicMock

from app.display import log


def test_log_is_configured():
    """Test that log is a properly configured logger instance"""
    assert isinstance(log, logging.Logger)
    assert log.name == "app.display"


def test_log_level_is_info_by_default():
    """Test that log level is INFO by default"""
    assert log.level <= logging.INFO


def test_library_loggers_silenced():
    """Test that noisy library loggers are set to WARNING level"""
    for name in ("httpx", "httpcore", "openai", "urllib3"):
        assert logging.getLogger(name).level == logging.WARNING


# Note: ask_permission tests have been removed because the function
# has been moved to app.cli and completely rewritten with a different
# async interface that uses message queues.