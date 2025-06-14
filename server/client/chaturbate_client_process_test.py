import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from server.client.chaturbate_client_process import ChaturbateClientProcess


@pytest.fixture
def mock_chaturbate_client():
    """Create a mock Chaturbate client."""
    with patch("chaturbate_poller.chaturbate_client.ChaturbateClient") as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        yield client


@pytest.mark.asyncio
async def test_client_process_initialization():
    """Test that the client process initializes correctly."""
    process = ChaturbateClientProcess(username="test_username", token="test_token")
    assert process.username == "test_username"
    assert process.token == "test_token"
    assert process.client is None
    assert "tip" in process.handlers
    assert "chatMessage" in process.handlers


@pytest.mark.asyncio
async def test_client_process_start(mock_chaturbate_client):
    """Test that the client process starts correctly."""
    process = ChaturbateClientProcess(username="test_username", token="test_token")
    await process.start()

    # Verify client was initialized with correct parameters
    mock_chaturbate_client.assert_called_once_with(
        username="test_username", token="test_token", event_handlers=process.handlers
    )
    # Verify poll_events was called
    mock_chaturbate_client.poll_events.assert_called_once()


@pytest.mark.asyncio
async def test_client_process_stop(mock_chaturbate_client):
    """Test that the client process stops correctly."""
    process = ChaturbateClientProcess(username="test_username", token="test_token")
    await process.start()
    await process.stop()

    # Verify client was stopped
    mock_chaturbate_client.__aexit__.assert_called_once_with(None, None, None)


@pytest.mark.asyncio
async def test_client_process_stop_without_start():
    """Test that stopping without starting doesn't raise an error."""
    process = ChaturbateClientProcess(username="test_username", token="test_token")
    await process.stop()  # Should not raise any errors


@pytest.mark.asyncio
async def test_client_process_event_handling(mock_chaturbate_client):
    """Test that event handlers are properly registered."""
    process = ChaturbateClientProcess(username="test_username", token="test_token")
    await process.start()

    # Verify handlers are registered
    assert process.handlers["tip"] is not None
    assert process.handlers["chatMessage"] is not None
    # Verify client was initialized with handlers
    mock_chaturbate_client.assert_called_once_with(
        username="test_username", token="test_token", event_handlers=process.handlers
    )
