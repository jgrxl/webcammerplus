import html

import pytest
from flask import Flask

from routes.write_route import bp as write_bp


@pytest.fixture(name="app")
def flask_app_fixture() -> Flask:
    """
    Creates a Flask test app with the write blueprint.
    """
    flask_app = Flask(__name__)
    flask_app.register_blueprint(write_bp)
    return flask_app


def test_write_success(app: Flask) -> None:
    client = app.test_client()
    resp = client.post(
        "/write/",
        json={"style": "formal", "text": "artificial intelligence", "to_lang": "en"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["written_text"] is not None
    assert data["written_text"] != ""


def test_write_missing_fields(app: Flask) -> None:
    """
    Test that the write route returns a 400 error
    when required fields are missing.
    """
    client = app.test_client()
    resp = client.post("/write/", json={"style": "formal", "text": "AI"})
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    assert "Missing required fields:" in html.unescape(body)
    assert "to_lang" in html.unescape(body)


def test_write_type_error(app: Flask) -> None:
    """
    Test that the write route returns a 400 error
    when an unexpected field is passed.
    """
    client = app.test_client()
    resp = client.post(
        "/write/", json={"style": "formal", "text": "AI", "to_lang": "en", "extra": 123}
    )
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    assert "unexpected keyword argument 'extra'" in html.unescape(body)


def test_write_all_fields_missing(app: Flask) -> None:
    """
    Test that the write route returns a 400 error
    when all required fields are missing.
    """
    client = app.test_client()
    resp = client.post("/write/", json={})
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    assert "Missing required fields:" in html.unescape(body)


def test_write_partial_fields_missing(app: Flask) -> None:
    """
    Test that the write route returns a 400 error
    when some required fields are missing.
    """
    client = app.test_client()
    resp = client.post("/write/", json={"style": "creative"})
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    assert "Missing required fields:" in html.unescape(body)
    assert "text" in html.unescape(body)
    assert "to_lang" in html.unescape(body)
