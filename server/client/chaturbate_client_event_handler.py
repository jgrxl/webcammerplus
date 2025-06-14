from chaturbate_poller.models import Event, Tip, Message, User


class ChaturbateClientHandle:
    """Handle chaturbate client events."""

    def __init__(self) -> None:
        pass

    async def handle_tip(self, event: Tip) -> None:
        """Process tip events with custom logic."""
        username = event.object.user.username
        amount = event.object.tip.tokens
        print(f"Received {amount} tokens from {username}!")

        # Trigger special actions based on tip amount
        if amount >= 100:
            ...

    async def handle_chat(self, event: Message) -> None:
        """Process chat message events."""
        username = event.object.user.username
        message = event.object.message
        print(f"{username}: {message}")

    async def handle_message(self, event: Event) -> None:
        """Process events."""
        if is_chat_message(event):
            await self.handle_chat(event)
        elif is_private_message(event):
            await self.handle_private_message(event)
        return None

    async def handle_private_message(self, event: Message) -> None:
        """Process private message events."""
        username = event.object.user.username
        message = event.object.message
        print(f"{username}: {message}")

    async def handle_media_purchase(self, event: Event) -> None:
        """Process media purchase events."""
        username = event.object.user.username
        media = event.object.media
        print(f"{username} purchased {media.name} for {media.tokens} tokens!")

    async def handle_user(self, user: User) -> None:
        """Process user events."""
        username = user.username
        print(f"User {username} joined the fanclub!")


def is_private_message(message: Message) -> bool:
    """
    Determines if the message is a private message.
    A private message typically has 'from_user' and 'to_user' fields.
    """
    return message.from_user is not None and message.to_user is not None


def is_chat_message(message: Message) -> bool:
    """
    Determines if the message is a public chat message.
    A public chat message typically does NOT have 'from_user' or 'to_user' fields
    (or at least not both, as 'to_user' would be irrelevant in a public chat).
    """
    return message.from_user is None and message.to_user is None
