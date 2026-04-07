import os
import pytest
import tempfile

from app.tools.read_file import ReadFileTool
read_file = ReadFileTool.call


def test_read_file_returns_contents(tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("hello world", encoding="utf-8")
    assert read_file(str(f)) == "hello world"


def test_read_file_nonexistent_returns_error():
    result = read_file("/nonexistent/path/file.txt")
    assert result.startswith("Error:")


def test_read_file_empty_file(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("", encoding="utf-8")
    assert read_file(str(f)) == ""


def test_read_file_multiline(tmp_path):
    content = "line1\nline2\nline3"
    f = tmp_path / "multi.txt"
    f.write_text(content, encoding="utf-8")
    assert read_file(str(f)) == content
