# from unittest.mock import MagicMock, patch

# import server.services.translate as st


class DummyMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class DummyResponse:
    def __init__(self, text: str) -> None:
        self.message = DummyMessage(text)
