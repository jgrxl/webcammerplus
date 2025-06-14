import asyncio
from server.client.chaturbate_client_event_handler import (
    ChaturbateClientHandle,
)
from chaturbate_poller.chaturbate_client import (  # type: ignore
    ChaturbateClient,
)


class ChaturbateClientProcess:
    """Process for managing the Chaturbate client."""

    def __init__(self, username: str, token: str) -> None:
        self.username = username
        self.token = token
        self.client: ChaturbateClient | None = None
        self.handlers = {
            "tip": ChaturbateClientHandle.handle_tip,
            "chatMessage": ChaturbateClientHandle.handle_chat,
        }

    async def start(self) -> None:
        """Start the client process."""
        self.client = ChaturbateClient(
            username=self.username,
            token=self.token,
            event_handlers=self.handlers,
        )
        async with self.client as client:
            await client.poll_events()

    async def stop(self) -> None:
        """Stop the client process."""
        if self.client is not None:
            await self.client.__aexit__(None, None, None)


async def main() -> None:
    """Run the client process."""
    process = ChaturbateClientProcess(
        username="your_username",
        token="your_token",
    )
    await process.start()


if __name__ == "__main__":
    asyncio.run(main())
