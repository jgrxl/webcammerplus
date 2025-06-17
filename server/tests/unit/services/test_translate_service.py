# from unittest.mock import MagicMock, patch

import server.services.translate_service as st


def test_translate_text() -> None:
    text = "Hello, world!"
    from_lang = "en"
    to_lang = "fr"

    response = st.translate_text(text, to_lang, from_lang)
    assert response is not None
    assert response != ""
