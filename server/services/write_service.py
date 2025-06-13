from server.services.write_service import write_text


def test_write() -> None:
    style = "formal"
    text = "Hello, world!"
    to_lang = "ES"

    response = write_text(style, text, to_lang)
    assert response is not None
    assert response != ""
