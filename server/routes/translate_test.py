import html

import pytest
from flask import Flask

from server.routes.translate import bp as translate_bp


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
    assert resp.status_code == 200  # nosec B101 - Test assertion
    data = resp.get_json()
    assert data["success"] is True  # nosec B101 - Test assertion
    assert data["translation"] == "hello world"  # nosec B101 - Test assertion


def test_translate_missing_fields(app: Flask) -> None:
    client = app.test_client()
    # Missing 'to_lang'
    resp = client.post("/translate/", json={"text": "hola"})
    assert resp.status_code == 400  # nosec B101 - Test assertion
    # HTML-escaped apostrophes: unescape before checking
    body = resp.get_data(as_text=True)
    assert "Both 'text' and 'to_lang' fields are required." in html.unescape(
        body
    )  # nosec B101 - Test assertion


def test_translate_type_error(app: Flask) -> None:
    client = app.test_client()
    # Pass an extra unexpected field
    resp = client.post(
        "/translate/", json={"text": "hola", "to_lang": "en", "extra": 123}
    )
    assert resp.status_code == 400  # nosec B101 - Test assertion
    body = resp.get_data(as_text=True)
    assert "__init__() got an unexpected keyword argument 'extra'" in html.unescape(
        body
    )  # nosec B101 - Test assertion
