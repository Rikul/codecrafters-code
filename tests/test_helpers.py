import pathlib
from unittest.mock import patch

from app.helpers import load_system_context


def test_load_system_context_returns_string():
    result = load_system_context()
    assert isinstance(result, str)


def test_load_system_context_includes_file_content():
    # The real system.md directory ships with the app and should contain content
    result = load_system_context()
    assert len(result) > 0


def test_load_system_context_skips_missing_files(tmp_path):
    system_md_dir = tmp_path / "system.md"
    system_md_dir.mkdir()

    with patch("app.helpers.Path") as MockPath:
        instance = MockPath.return_value
        instance.parent.__truediv__ = lambda self, key: system_md_dir
        MockPath.side_effect = lambda *args, **kwargs: pathlib.Path(*args, **kwargs)

        # Only one file present; should not raise
        (system_md_dir / "self.md").write_text("hello", encoding="utf-8")
        result = load_system_context()

    assert isinstance(result, str)

