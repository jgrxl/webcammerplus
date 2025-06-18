import server.services.write_service as ws


def test_write() -> None:
    style = "formal"
    text = "Hello, world!"
    to_lang = "ES"

    response = ws.write_text(style, text, to_lang)
    assert response is not None
    assert response != ""
