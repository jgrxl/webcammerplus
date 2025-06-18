import asyncio
import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from server.client.chaturbate_client_event_handler import ChaturbateClientEventHandler
from server.client.chaturbate_client_process import ChaturbateClientProcess


@pytest.fixture
def mock_chaturbate_client():
    """Create a comprehensive mock Chaturbate client."""
    with patch(
        "server.client.chaturbate_client_process.ChaturbateClient"
    ) as mock_class:
        mock_instance = AsyncMock()
        mock_class.return_value = mock_instance

        # Mock async context manager behavior
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)

        # Mock polling method
        mock_instance.poll_events = AsyncMock()

        yield mock_class, mock_instance


@pytest.fixture
def mock_event_handler():
    """Create a mock event handler."""
    handler = Mock(spec=ChaturbateClientEventHandler)
    handler.handle_tip = AsyncMock()
    handler.handle_chat = AsyncMock()
    handler.handle_message = AsyncMock()
    return handler


@pytest.fixture
def clean_env():
    """Clean environment variables for testing."""
    original_env = {}
    env_vars = ["CHATURBATE_USERNAME", "CHATURBATE_TOKEN"]

    # Save original values
    for var in env_vars:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]

    yield

    # Restore original values
    for var, value in original_env.items():
        os.environ[var] = value


class TestChaturbateClientProcessInitialization:
    """Test initialization and configuration of ChaturbateClientProcess."""

    def test_initialization_with_explicit_credentials(self, clean_env):
        """Test initialization with explicitly provided credentials."""
        process = ChaturbateClientProcess(username="test_username", token="test_token")

        assert process.username == "test_username"
        assert process.token == "test_token"
        assert process.client is None
        assert not process.is_running
        assert isinstance(process.event_handler, ChaturbateClientEventHandler)
        assert "tip" in process.handlers
        assert "chatMessage" in process.handlers

    def test_initialization_with_environment_variables(self, clean_env):
        """Test initialization using environment variables."""
        os.environ["CHATURBATE_USERNAME"] = "env_username"
        os.environ["CHATURBATE_TOKEN"] = "env_token"

        process = ChaturbateClientProcess()

        assert process.username == "env_username"
        assert process.token == "env_token"

    def test_initialization_with_custom_event_handler(
        self, mock_event_handler, clean_env
    ):
        """Test initialization with custom event handler."""
        process = ChaturbateClientProcess(
            username="test_username",
            token="test_token",
            event_handler=mock_event_handler,
        )

        assert process.event_handler is mock_event_handler

    def test_initialization_missing_credentials(self, clean_env):
        """Test that initialization fails with missing credentials."""
        with pytest.raises(ValueError, match="Username and token are required"):
            ChaturbateClientProcess()

    def test_initialization_partial_credentials(self, clean_env):
        """Test that initialization fails with partial credentials."""
        with pytest.raises(ValueError, match="Username and token are required"):
            ChaturbateClientProcess(username="test_username")

        with pytest.raises(ValueError, match="Username and token are required"):
            ChaturbateClientProcess(token="test_token")

    def test_repr_representation(self, clean_env):
        """Test string representation of the process."""
        process = ChaturbateClientProcess(username="test_username", token="test_token")

        repr_str = repr(process)
        assert "test_username" in repr_str
        assert "stopped" in repr_str


class TestChaturbateClientProcessLifecycle:
    """Test lifecycle management of ChaturbateClientProcess."""

    @pytest.mark.asyncio
    async def test_start_and_immediate_stop(self, mock_chaturbate_client, clean_env):
        """Test starting the process and stopping it immediately."""
        mock_class, mock_instance = mock_chaturbate_client

        # Make poll_events block until cancelled
        event = asyncio.Event()
        mock_instance.poll_events.side_effect = lambda: event.wait()

        process = ChaturbateClientProcess(username="test_username", token="test_token")

        # Start the process in background
        start_task = asyncio.create_task(process.start())

        # Give it time to initialize
        await asyncio.sleep(0.1)

        assert process.is_running

        # Stop the process
        await process.stop()

        assert not process.is_running

        # Clean up
        start_task.cancel()
        try:
            await start_task
        except asyncio.CancelledError:
            pass

        # Verify client was created with correct parameters
        mock_class.assert_called_with(
            username="test_username",
            token="test_token",
            event_handlers=process.handlers,
        )

    @pytest.mark.asyncio
    async def test_start_already_running(self, clean_env):
        """Test that starting an already running process raises an error."""
        process = ChaturbateClientProcess(username="test_username", token="test_token")

        # Manually set running state
        process.is_running = True

        with pytest.raises(RuntimeError, match="already running"):
            await process.start()

    @pytest.mark.asyncio
    async def test_stop_without_start(self, clean_env):
        """Test that stopping without starting doesn't raise an error."""
        process = ChaturbateClientProcess(username="test_username", token="test_token")

        # Should not raise any errors
        await process.stop()
        assert not process.is_running

    @pytest.mark.asyncio
    async def test_context_manager_usage(self, mock_chaturbate_client, clean_env):
        """Test using the process as a context manager."""
        mock_class, mock_instance = mock_chaturbate_client

        # Make poll_events return quickly
        mock_instance.poll_events = AsyncMock()

        process = ChaturbateClientProcess(username="test_username", token="test_token")

        async with process.run_context() as ctx:
            assert ctx is process
            # Give it time to start
            await asyncio.sleep(0.1)

        # Process should be stopped after context exit
        assert not process.is_running


class TestChaturbateClientProcessErrorHandling:
    """Test error handling and resilience of ChaturbateClientProcess."""

    @pytest.mark.asyncio
    async def test_connection_failure_retry(self, mock_chaturbate_client, clean_env):
        """Test that connection failures trigger retry logic."""
        mock_class, mock_instance = mock_chaturbate_client

        # Simulate connection failure then success
        call_count = 0

        async def failing_poll():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Connection failed")
            else:
                # Block on second call to simulate continuous running
                await asyncio.Event().wait()

        mock_instance.poll_events.side_effect = failing_poll

        process = ChaturbateClientProcess(username="test_username", token="test_token")

        # Start process in background
        start_task = asyncio.create_task(process.start())

        # Wait for retry logic to execute
        await asyncio.sleep(6)  # Should be enough for retry delay

        # Verify multiple attempts were made
        assert mock_class.call_count >= 2

        # Stop the process
        await process.stop()

        # Clean up
        start_task.cancel()
        try:
            await start_task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_graceful_shutdown_timeout(self, mock_chaturbate_client, clean_env):
        """Test that shutdown handles timeouts gracefully."""
        mock_class, mock_instance = mock_chaturbate_client

        # Make poll_events block indefinitely
        mock_instance.poll_events.side_effect = lambda: asyncio.Event().wait()

        process = ChaturbateClientProcess(username="test_username", token="test_token")

        # Start process
        start_task = asyncio.create_task(process.start())
        await asyncio.sleep(0.1)  # Let it start

        # Stop should complete even if cleanup times out
        await process.stop()

        assert not process.is_running

        # Clean up
        start_task.cancel()
        try:
            await start_task
        except asyncio.CancelledError:
            pass


class TestChaturbateClientProcessEventHandling:
    """Test event handling configuration and behavior."""

    def test_event_handlers_registration(self, mock_event_handler, clean_env):
        """Test that event handlers are properly registered."""
        process = ChaturbateClientProcess(
            username="test_username",
            token="test_token",
            event_handler=mock_event_handler,
        )

        # Verify handlers are registered
        assert "tip" in process.handlers
        assert "chatMessage" in process.handlers
        assert process.handlers["tip"] == mock_event_handler.handle_tip
        assert process.handlers["chatMessage"] == mock_event_handler.handle_chat

    def test_default_event_handler_creation(self, clean_env):
        """Test that default event handler is created when none provided."""
        process = ChaturbateClientProcess(username="test_username", token="test_token")

        assert isinstance(process.event_handler, ChaturbateClientEventHandler)
        assert callable(process.handlers["tip"])
        assert callable(process.handlers["chatMessage"])


# Integration-style tests
class TestChaturbateClientProcessIntegration:
    """Integration tests for complete workflows."""

    @pytest.mark.asyncio
    async def test_full_lifecycle_with_events(
        self, mock_chaturbate_client, mock_event_handler, clean_env
    ):
        """Test complete lifecycle with event processing."""
        mock_class, mock_instance = mock_chaturbate_client

        # Track if poll_events was called
        poll_events_called = asyncio.Event()

        async def mock_poll():
            poll_events_called.set()
            await asyncio.sleep(0.1)  # Simulate some processing

        mock_instance.poll_events.side_effect = mock_poll

        process = ChaturbateClientProcess(
            username="test_username",
            token="test_token",
            event_handler=mock_event_handler,
        )

        # Use context manager for automatic cleanup
        async with process.run_context():
            # Wait for poll_events to be called
            await asyncio.wait_for(poll_events_called.wait(), timeout=1.0)

            # Verify the process is running
            assert process.is_running

            # Verify client was created correctly
            mock_class.assert_called_with(
                username="test_username",
                token="test_token",
                event_handlers=process.handlers,
            )

        # After context exit, process should be stopped
        assert not process.is_running
