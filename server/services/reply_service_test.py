from services.reply_service import reply_text


def test_reply() -> None:
    original_text = "Hello, world!"
    response_idea = "Hello, world!"
    style = "formal"
    to_lang = "ES"

    response = reply_text(original_text, response_idea, style, to_lang)
    assert response is not None
    assert response != ""
