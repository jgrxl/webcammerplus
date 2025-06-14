import asyncio
import logging
import os
import signal
from contextlib import asynccontextmanager
from typing import Optional, Dict, Callable, Any

from server.client.chaturbate_client_event_handler import (
    ChaturbateClientEventHandler,
)
from chaturbate_poller.chaturbate_client import (  # type: ignore
    ChaturbateClient,
)


logger = logging.getLogger(__name__)


class ChaturbateClientProcess:
    """High-level process manager for Chaturbate client connections.
    
    This class manages the lifecycle of a Chaturbate client connection,
    including automatic reconnection, graceful shutdown, and comprehensive
    error handling.
    
    Attributes:
        username: Chaturbate account username
        token: Authentication token
        client: The underlying Chaturbate client instance
        event_handler: Handler for processing events
        is_running: Whether the process is currently running
    """

    def __init__(self, 
                 username: Optional[str] = None, 
                 token: Optional[str] = None,
                 event_handler: Optional[ChaturbateClientEventHandler] = None) -> None:
        """Initialize the Chaturbate client process.
        
        Args:
            username: Chaturbate username (or uses CHATURBATE_USERNAME env var)
            token: Authentication token (or uses CHATURBATE_TOKEN env var)
            event_handler: Custom event handler (creates default if None)
            
        Raises:
            ValueError: If required credentials are missing
        """
        self.username = username or os.getenv("CHATURBATE_USERNAME")
        self.token = token or os.getenv("CHATURBATE_TOKEN")
        
        if not self.username or not self.token:
            raise ValueError(
                "Username and token are required. Provide them directly or set "
                "CHATURBATE_USERNAME and CHATURBATE_TOKEN environment variables."
            )
        
        self.client: Optional[ChaturbateClient] = None
        self.event_handler = event_handler or ChaturbateClientEventHandler()
        self.is_running = False
        self._shutdown_event = asyncio.Event()
        
        # Build event handler mapping
        self.handlers: Dict[str, Callable] = {
            "tip": self.event_handler.handle_tip,
            "chatMessage": self.event_handler.handle_chat,
            "chatMessage": self.event_handler.handle_message,
        }
        
        logger.info(f"Initialized Chaturbate client process for user '{self.username}'")

    async def start(self) -> None:
        """Start the client process with automatic reconnection.
        
        This method will run indefinitely until stop() is called or an
        unrecoverable error occurs.
        
        Raises:
            RuntimeError: If the process is already running
        """
        if self.is_running:
            raise RuntimeError("Client process is already running")
            
        self.is_running = True
        logger.info("Starting Chaturbate client process")
        
        try:
            while self.is_running and not self._shutdown_event.is_set():
                try:
                    await self._run_client_session()
                except Exception as e:
                    logger.error(f"Client session failed: {e}")
                    if self.is_running:
                        logger.info("Attempting to reconnect in 5 seconds...")
                        await asyncio.sleep(5)
                    else:
                        break
        finally:
            self.is_running = False
            logger.info("Chaturbate client process stopped")
    
    async def _run_client_session(self) -> None:
        """Run a single client session.
        
        Raises:
            Exception: Any error that occurs during the session
        """
        logger.debug("Starting new client session")
        
        self.client = ChaturbateClient(
            username=self.username,
            token=self.token,
            event_handlers=self.handlers,
        )
        
        try:
            async with self.client as client:
                # Run until shutdown is requested
                poll_task = asyncio.create_task(client.poll_events())
                shutdown_task = asyncio.create_task(self._shutdown_event.wait())
                
                done, pending = await asyncio.wait(
                    [poll_task, shutdown_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Cancel any remaining tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                        
                # Check if polling failed
                if poll_task in done:
                    try:
                        await poll_task
                    except Exception as e:
                        logger.error(f"Event polling failed: {e}")
                        raise
                        
        except Exception as e:
            logger.error(f"Client session error: {e}")
            raise
        finally:
            self.client = None
            logger.debug("Client session ended")

    async def stop(self) -> None:
        """Gracefully stop the client process.
        
        This method signals the client to stop and waits for cleanup to complete.
        """
        if not self.is_running:
            logger.warning("Client process is not running")
            return
            
        logger.info("Stopping Chaturbate client process")
        self.is_running = False
        self._shutdown_event.set()
        
        # Give the client time to clean up
        try:
            await asyncio.wait_for(self._wait_for_shutdown(), timeout=10.0)
        except asyncio.TimeoutError:
            logger.warning("Client shutdown timed out")
            
        logger.info("Chaturbate client process stopped successfully")
    
    async def _wait_for_shutdown(self) -> None:
        """Wait for the client to fully shut down."""
        while self.client is not None:
            await asyncio.sleep(0.1)
    
    @asynccontextmanager
    async def run_context(self):
        """Context manager for running the client process.
        
        Usage:
            async with process.run_context():
                # Client runs in background
                await asyncio.sleep(60)  # Run for 60 seconds
        """
        task = asyncio.create_task(self.start())
        try:
            # Give the client time to start
            await asyncio.sleep(0.1)
            yield self
        finally:
            await self.stop()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    def __repr__(self) -> str:
        """String representation of the process."""
        status = "running" if self.is_running else "stopped"
        return f"ChaturbateClientProcess(username='{self.username}', status='{status}')"


async def main() -> None:
    """Run the client process with graceful shutdown handling.
    
    This function demonstrates proper usage of the ChaturbateClientProcess
    with signal handling for clean shutdown.
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create process instance
    try:
        process = ChaturbateClientProcess()
    except ValueError as e:
        logger.error(f"Failed to initialize client: {e}")
        return
    
    # Setup signal handlers for graceful shutdown
    def signal_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(process.stop())
    
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler())
    if hasattr(signal, 'SIGINT'):
        signal.signal(signal.SIGINT, lambda s, f: signal_handler())
    
    # Run the client
    try:
        await process.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if process.is_running:
            await process.stop()


if __name__ == "__main__":
    asyncio.run(main())