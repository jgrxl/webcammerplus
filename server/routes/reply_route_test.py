import html

import pytest
from flask import Flask

from routes.reply_route import bp as reply_bp


@pytest.fixture(name="app")
def flask_app_fixture() -> Flask:
    """
    Creates a Flask test app with the reply blueprint.
    """
    flask_app = Flask(__name__)
    flask_app.register_blueprint(reply_bp)
    return flask_app


def test_reply_success(app: Flask) -> None:
    client = app.test_client()
    resp = client.post("/reply/", json={
        "original_text": "Hello, how are you?",
        "response_idea": "I'm doing well",
        "style": "casual",
        "to_lang": "en"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["reply"] is not None
    assert data["reply"] != ""


def test_reply_missing_fields(app: Flask) -> None:
    """
    Test that the reply route returns a 400 error
    when required fields are missing.
    """
    client = app.test_client()
    resp = client.post("/reply/", json={
        "original_text": "Hello",
        "style": "casual"
    })
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    assert "Missing required fields:" in html.unescape(body)
    assert "response_idea" in html.unescape(body)
    assert "to_lang" in html.unescape(body)


def test_reply_type_error(app: Flask) -> None:
    """
    Test that the reply route returns a 400 error
    when an unexpected field is passed.
    """
    client = app.test_client()
    resp = client.post("/reply/", json={
        "original_text": "Hello",
        "response_idea": "I'm good",
        "style": "casual",
        "to_lang": "en",
        "extra": 123
    })
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    assert "unexpected keyword argument 'extra'" in html.unescape(body)


def test_reply_all_fields_missing(app: Flask) -> None:
    """
    Test that the reply route returns a 400 error
    when all required fields are missing.
    """
    client = app.test_client()
    resp = client.post("/reply/", json={})
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    assert "Missing required fields:" in html.unescape(body)