import pytest
from unittest.mock import patch, MagicMock

from app.tools.bash import bash


def test_bash_runs_simple_command():
    result = bash("echo hello")
    assert "hello" in result


def test_bash_returns_stderr_on_failure():
    result = bash("ls /nonexistent_path_xyz")
    assert result  # should contain some output (error in stderr)
    assert "No such file" in result or "cannot access" in result or "stderr" in result


def test_bash_captures_stdout():
    result = bash("printf 'abc'")
    assert "abc" in result


def test_bash_timeout_error():
    with patch("subprocess.run", side_effect=Exception("timed out")) as mock_run:
        result = bash("sleep 100")
    assert "Error" in result


def test_bash_multiline_output():
    result = bash("printf 'a\nb\nc'")
    assert "a" in result
    assert "b" in result
    assert "c" in result


def test_bash_returns_combined_stderr():
    result = bash("echo out && echo err >&2")
    assert "out" in result
    assert "err" in result
