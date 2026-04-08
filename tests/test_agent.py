import pytest
from unittest.mock import patch, MagicMock, AsyncMock

import app.config as config
from app.cli_agent import CliAgent as Agent


def make_mock_client(tool_calls=None, content="Hello!", finish_reason="stop"):
    """Build a mock AsyncOpenAI client that returns a canned response."""
    mock_message = MagicMock()
    mock_message.tool_calls = tool_calls
    mock_message.content = content

    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_choice.finish_reason = finish_reason

    mock_chat = MagicMock()
    mock_chat.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_chat)
    return mock_client


def make_agent(auto_approve=True, silent=True, max_iterations=10):
    with patch("app.agent.Client") as MockClient:
        mock_openai = make_mock_client()
        MockClient.return_value.get_client.return_value = mock_openai
        with patch("app.agent.load_system_context", return_value=""):
            with patch("app.cli_agent.MessageHistory") as MockHistory:
                MockHistory.return_value.get_history.return_value = []
                agent = Agent(
                    auto_approve=auto_approve, silent=silent, max_iterations=max_iterations
                )
    # Attach the mock client so callers can reconfigure it after construction
    agent.client = mock_openai
    return agent, mock_openai


@pytest.fixture(autouse=True)
def patch_config():
    with patch.object(config, "_config", {"agent": {"model": "test-model"}}):
        yield


def test_agent_initializes_with_empty_messages():
    agent, _ = make_agent()
    # Only system message if system context is non-empty; here it's empty so no messages
    assert agent.messages == []


def test_agent_initializes_with_system_context():
    with patch("app.agent.Client") as MockClient:
        MockClient.return_value.get_client.return_value = MagicMock()
        with patch("app.agent.load_system_context", return_value="system prompt"):
            with patch("app.cli_agent.MessageHistory") as MockHistory:
                MockHistory.return_value.get_history.return_value = []
                agent = Agent(auto_approve=True, silent=True, max_iterations=10)
    assert len(agent.messages) == 1
    assert agent.messages[0]["role"] == "system"
    assert agent.messages[0]["content"] == "system prompt"


@pytest.mark.asyncio
async def test_agent_loop_adds_user_message():
    agent, mock_client = make_agent()
    await agent.agent_loop("What is 2+2?")
    assert any(
        m.get("role") == "user" and m.get("content") == "What is 2+2?"
        for m in agent.messages
    )


@pytest.mark.asyncio
async def test_agent_loop_appends_assistant_message():
    agent, mock_client = make_agent()
    await agent.agent_loop("Hello")
    assistant_messages = [m for m in agent.messages if not isinstance(m, dict)]
    assert any(
        msg.content == "Hello!" and msg.tool_calls is None for msg in assistant_messages
    )


@pytest.mark.asyncio
async def test_agent_loop_raises_on_empty_choices():
    agent, mock_client = make_agent()
    mock_response = MagicMock()
    mock_response.choices = []
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with pytest.raises(RuntimeError, match="no choices in response"):
        await agent.agent_loop("Hello")


@pytest.mark.asyncio
async def test_agent_loop_respects_max_iterations():
    with patch("app.agent.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value.get_client.return_value = mock_client
        with patch("app.agent.load_system_context", return_value=""):
            agent = Agent(auto_approve=True, silent=True, max_iterations=3)
    agent.client = mock_client

    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "bash"
    mock_tool_call.function.arguments = '{"command": "echo hi"}'
    mock_tool_call.id = "tc1"

    mock_message = MagicMock()
    mock_message.tool_calls = [mock_tool_call]
    mock_message.content = None

    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_choice.finish_reason = "tool_calls"

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("app.cli_agent.run_tool", return_value="hi\n"):
        await agent.agent_loop("run forever")

    # Should have stopped after max_iterations=3 LLM calls
    assert mock_client.chat.completions.create.call_count == 3


@pytest.mark.asyncio
async def test_agent_loop_runs_tool_when_auto_approve():
    with patch("app.agent.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value.get_client.return_value = mock_client
        with patch("app.agent.load_system_context", return_value=""):
            agent = Agent(auto_approve=True, silent=True, max_iterations=10)
    agent.client = mock_client

    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "bash"
    mock_tool_call.function.arguments = '{"command": "echo hi"}'
    mock_tool_call.id = "tc1"

    # First response: has a tool call
    msg_with_tool = MagicMock()
    msg_with_tool.tool_calls = [mock_tool_call]
    msg_with_tool.content = None
    choice_with_tool = MagicMock()
    choice_with_tool.message = msg_with_tool
    choice_with_tool.finish_reason = "tool_calls"
    response_with_tool = MagicMock()
    response_with_tool.choices = [choice_with_tool]

    # Second response: plain text, ends the loop
    msg_plain = MagicMock()
    msg_plain.tool_calls = None
    msg_plain.content = "done"
    choice_plain = MagicMock()
    choice_plain.message = msg_plain
    choice_plain.finish_reason = "stop"
    response_plain = MagicMock()
    response_plain.choices = [choice_plain]

    mock_client.chat.completions.create = AsyncMock(
        side_effect=[response_with_tool, response_plain]
    )

    with patch("app.cli_agent.run_tool", return_value="hi\n") as mock_run_tool:
        await agent.agent_loop("say hi")

    mock_run_tool.assert_called_once_with(
        tool_name="bash", tool_args={"command": "echo hi"}
    )


@pytest.mark.asyncio
async def test_agent_loop_continues_when_finish_reason_not_stop():
    with patch("app.agent.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value.get_client.return_value = mock_client
        with patch("app.agent.load_system_context", return_value=""):
            agent = Agent(auto_approve=True, silent=True, max_iterations=10)
    agent.client = mock_client

    msg_partial = MagicMock()
    msg_partial.tool_calls = None
    msg_partial.content = "partial"
    choice_partial = MagicMock()
    choice_partial.message = msg_partial
    choice_partial.finish_reason = "length"
    response_partial = MagicMock()
    response_partial.choices = [choice_partial]

    msg_final = MagicMock()
    msg_final.tool_calls = None
    msg_final.content = "final"
    choice_final = MagicMock()
    choice_final.message = msg_final
    choice_final.finish_reason = "stop"
    response_final = MagicMock()
    response_final.choices = [choice_final]

    mock_client.chat.completions.create = AsyncMock(
        side_effect=[response_partial, response_final]
    )

    await agent.agent_loop("continue")

    assert mock_client.chat.completions.create.call_count == 2
