import pytest
import app.config as config


def test_load_raises_when_file_not_found(tmp_path):
    with pytest.raises(RuntimeError, match="does not exist"):
        config.load(tmp_path / "missing.toml")


def test_load_reads_toml_file(tmp_path):
    toml_file = tmp_path / "test.toml"
    toml_file.write_bytes(b'[agent]\nmodel = "gpt-4o"\n')
    config.load(toml_file)
    assert config.get("agent") == {"model": "gpt-4o"}


def test_get_returns_value_for_existing_key(tmp_path):
    toml_file = tmp_path / "test.toml"
    toml_file.write_bytes(b'[agent]\nmodel = "gpt-4o"\n')
    config.load(toml_file)
    assert config.get("agent") == {"model": "gpt-4o"}


def test_get_returns_default_for_missing_key(tmp_path):
    toml_file = tmp_path / "test.toml"
    toml_file.write_bytes(b'[agent]\nmodel = "gpt-4o"\n')
    config.load(toml_file)
    assert config.get("nonexistent", "fallback") == "fallback"


def test_get_returns_none_by_default_for_missing_key(tmp_path):
    toml_file = tmp_path / "test.toml"
    toml_file.write_bytes(b'[agent]\nmodel = "gpt-4o"\n')
    config.load(toml_file)
    assert config.get("nonexistent") is None


def test_getattr_returns_config_section(tmp_path):
    toml_file = tmp_path / "test.toml"
    toml_file.write_bytes(b'[agent]\nmodel = "gpt-4o"\n')
    config.load(toml_file)
    assert config.agent == {"model": "gpt-4o"}


def test_getattr_raises_for_missing_key(tmp_path):
    toml_file = tmp_path / "test.toml"
    toml_file.write_bytes(b'[agent]\nmodel = "gpt-4o"\n')
    config.load(toml_file)
    with pytest.raises(AttributeError, match="Config has no attribute"):
        _ = config.nonexistent_key


def test_load_defaults_to_config_toml():
    config.load()
    assert isinstance(config.get("agent"), dict)
    assert "model" in config.get("agent")
