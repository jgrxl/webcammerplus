import html

import pytest
from flask import Flask

from routes.translate_route import bp as translate_bp


@pytest.fixture(name="app")
def flask_app_fixture() -> Flask:
    """
    Creates a Flask test app with the translate blueprint.
    """
    flask_app = Flask(__name__)
    flask_app.register_blueprint(translate_bp)
    return flask_app


def test_translate_success(app: Flask) -> None:
    client = app.test_client()
    resp = client.post("/translate/", json={"text": "hello world", "to_lang": "es"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["translation"] is not None
    assert data["translation"] != ""


def test_translate_missing_fields(app: Flask) -> None:
    """
    Test that the translate route returns a 400 error
    when the 'to_lang' field is missing.
    """
    client = app.test_client()
    resp = client.post("/translate/", json={"text": "hola"})
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    assert "Both 'text' and 'to_lang' fields are required." in html.unescape(body)


def test_translate_type_error(app: Flask) -> None:
    """
    Test that the translate route returns a 400 error
    when an unexpected field is passed.
    """
    client = app.test_client()
    resp = client.post(
        "/translate/", json={"text": "hola", "to_lang": "en", "extra": 123}
    )
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    assert "unexpected keyword argument 'extra'" in html.unescape(body)
