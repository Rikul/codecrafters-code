import os
import pytest
from unittest.mock import patch

from app.config import Config


def test_get_model_returns_env_value():
    with patch.dict(os.environ, {"LLM_MODEL": "gpt-4o"}):
        assert Config.get_model() == "gpt-4o"


def test_get_model_raises_when_not_set():
    env = {k: v for k, v in os.environ.items() if k != "LLM_MODEL"}
    with patch.dict(os.environ, env, clear=True):
        with pytest.raises(RuntimeError, match="LLM_MODEL is not set"):
            Config.get_model()


def test_get_model_returns_different_model_names():
    for model in ["claude-3-opus", "mistral-7b", "llama-3"]:
        with patch.dict(os.environ, {"LLM_MODEL": model}):
            assert Config.get_model() == model
