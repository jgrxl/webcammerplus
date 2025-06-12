import services.translate as st
from unittest.mock import patch

class DummyMessage:
    def __init__(self, content: str):
        self.content = content

class DummyResponse:
    def __init__(self, text: str):
        self.message = DummyMessage(text)

@patch.object(st, "chat")
def test_translate_with_patch_object(mock_chat):
    mock_chat.return_value = DummyResponse("Bonjour")
    result = st.translate_text("Good morning", to_lang="fr")
    
    assert result == "Bonjour"
    mock_chat.assert_called_once()
