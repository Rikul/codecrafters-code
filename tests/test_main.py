import sys
import logging
import pytest
from unittest.mock import patch, MagicMock, AsyncMock, call
from prompt_toolkit import PromptSession

from app.main import input_loop, main


# ---------------------------------------------------------------------------
# input_loop
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_input_loop_yields_user_input():
    session = MagicMock(spec=PromptSession)
    session.prompt_async = AsyncMock(side_effect=["hello", "world", EOFError()])

    results = []
    async for value in input_loop(session):
        results.append(value)

    assert results == ["hello", "world"]


@pytest.mark.asyncio
async def test_input_loop_stops_on_eof():
    session = MagicMock(spec=PromptSession)
    session.prompt_async = AsyncMock(side_effect=[EOFError()])

    results = []
    async for value in input_loop(session):
        results.append(value)

    assert results == []


@pytest.mark.asyncio
async def test_input_loop_stops_on_keyboard_interrupt():
    session = MagicMock(spec=PromptSession)
    session.prompt_async = AsyncMock(side_effect=[KeyboardInterrupt()])

    results = []
    async for value in input_loop(session):
        results.append(value)

    assert results == []


# ---------------------------------------------------------------------------
# Helpers to patch the heavy dependencies used by main()
# ---------------------------------------------------------------------------

def _patch_main(argv, agent_mock=None):
    """Context-manager stack that patches sys.argv and the Agent class.

    argv should contain only the arguments (without a leading program name);
    the helper prepends a dummy program name automatically.
    """
    if agent_mock is None:
        agent_mock = MagicMock()
        agent_mock.agent_loop = AsyncMock()

    patches = [
        patch("sys.argv", ["prog"] + argv),
        patch("app.main.Agent", return_value=agent_mock),
        patch("app.main.PromptSession"),
    ]
    return patches, agent_mock


# ---------------------------------------------------------------------------
# main() – argument parsing & validation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_main_calls_agent_loop_with_prompt():
    agent_mock = MagicMock()
    agent_mock.agent_loop = AsyncMock()
    patches, _ = _patch_main(["-p", "say hello", "--no-repl"], agent_mock=agent_mock)

    for p in patches:
        p.start()
    try:
        await main()
    finally:
        for p in patches:
            p.stop()

    agent_mock.agent_loop.assert_called_once_with("say hello")


@pytest.mark.asyncio
async def test_main_no_repl_exits_after_first_agent_loop():
    agent_mock = MagicMock()
    agent_mock.agent_loop = AsyncMock()
    patches, _ = _patch_main(["-p", "hi", "--no-repl"], agent_mock=agent_mock)

    for p in patches:
        p.start()
    try:
        await main()
    finally:
        for p in patches:
            p.stop()

    assert agent_mock.agent_loop.call_count == 1


@pytest.mark.asyncio
async def test_main_silent_exits_after_first_agent_loop():
    agent_mock = MagicMock()
    agent_mock.agent_loop = AsyncMock()
    patches, _ = _patch_main(["-p", "hi", "--silent"], agent_mock=agent_mock)

    for p in patches:
        p.start()
    try:
        await main()
    finally:
        for p in patches:
            p.stop()

    assert agent_mock.agent_loop.call_count == 1


@pytest.mark.asyncio
async def test_main_silent_sets_log_level_to_warning():
    agent_mock = MagicMock()
    agent_mock.agent_loop = AsyncMock()
    patches, _ = _patch_main(["-p", "hi", "--silent"], agent_mock=agent_mock)

    for p in patches:
        p.start()
    try:
        await main()
    finally:
        for p in patches:
            p.stop()

    from app.display import log
    assert log.level == logging.WARNING


@pytest.mark.asyncio
async def test_main_silent_implies_auto_approve():
    MockAgent = MagicMock()
    MockAgent.return_value.agent_loop = AsyncMock()

    with patch("sys.argv", ["prog", "-p", "hi", "--silent"]), patch("app.main.Agent", MockAgent), patch("app.main.PromptSession"):
        await main()

    _, kwargs = MockAgent.call_args
    assert kwargs["auto_approve"] is True


@pytest.mark.asyncio
async def test_main_returns_early_when_max_iterations_is_zero():
    agent_mock = MagicMock()
    agent_mock.agent_loop = AsyncMock()
    patches, _ = _patch_main(["-p", "hi", "--no-repl", "--max-iterations", "0"], agent_mock=agent_mock)

    for p in patches:
        p.start()
    try:
        await main()
    finally:
        for p in patches:
            p.stop()

    agent_mock.agent_loop.assert_not_called()


@pytest.mark.asyncio
async def test_main_returns_early_when_max_iterations_is_negative():
    agent_mock = MagicMock()
    agent_mock.agent_loop = AsyncMock()
    patches, _ = _patch_main(["-p", "hi", "--no-repl", "--max-iterations", "-5"], agent_mock=agent_mock)

    for p in patches:
        p.start()
    try:
        await main()
    finally:
        for p in patches:
            p.stop()

    agent_mock.agent_loop.assert_not_called()


@pytest.mark.asyncio
async def test_main_repl_calls_agent_loop_for_each_input():
    agent_mock = MagicMock()
    agent_mock.agent_loop = AsyncMock()

    async def fake_input_loop(session):
        for msg in ["second", "third"]:
            yield msg

    with patch("sys.argv", ["prog", "-p", "first"]), \
         patch("app.main.Agent", return_value=agent_mock), \
         patch("app.main.PromptSession"), \
         patch("app.main.input_loop", fake_input_loop):
        await main()

    assert agent_mock.agent_loop.call_count == 3
    agent_mock.agent_loop.assert_any_call("first")
    agent_mock.agent_loop.assert_any_call("second")
    agent_mock.agent_loop.assert_any_call("third")
