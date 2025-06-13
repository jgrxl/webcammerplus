from typing import Any
from unittest.mock import MagicMock, patch

import services.translate as st


class DummyMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class DummyResponse:
    def __init__(self, text: str) -> None:
        self.message = DummyMessage(text)


@patch.object(st, "chat")
def test_translate_with_patch_object(mock_chat: MagicMock) -> None:
    mock_chat.return_value = DummyResponse("Bonjour")
    result = st.translate_text("Good morning", to_lang="fr")

    assert result == "Bonjour"  # nosec B101 - Test assertion
    mock_chat.assert_called_once()
