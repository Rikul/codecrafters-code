import os
import pytest
from unittest.mock import patch, MagicMock

from app.client import Client


def test_client_raises_when_no_api_key():
    env = {k: v for k, v in os.environ.items() if k not in ("LLM_API_KEY",)}
    with patch.dict(os.environ, env, clear=True):
        with patch("app.client.API_KEY", None):
            with pytest.raises(RuntimeError, match="API_KEY is not set"):
                Client(api_key=None)


def test_client_get_client_returns_openai_instance():
    with patch("app.client.AsyncOpenAI") as MockOpenAI:
        mock_instance = MagicMock()
        MockOpenAI.return_value = mock_instance
        client = Client(api_key="test-key", base_url="https://example.com")
        assert client.get_client() is mock_instance


def test_client_uses_provided_base_url():
    with patch("app.client.AsyncOpenAI") as MockOpenAI:
        Client(api_key="test-key", base_url="https://custom.api.com")
        MockOpenAI.assert_called_once_with(api_key="test-key", base_url="https://custom.api.com")


def test_client_uses_default_base_url_when_not_set():
    with patch.dict(os.environ, {"LLM_BASE_URL": ""}, clear=False):
        with patch("app.client.AsyncOpenAI") as MockOpenAI:
            with patch("app.client.BASE_URL", "https://openrouter.ai/api/v1"):
                Client(api_key="test-key")
                MockOpenAI.assert_called_once()
