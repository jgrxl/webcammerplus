from dataclasses import dataclass
from flask import Blueprint, request, jsonify, abort, Response
from typing import Any

bp = Blueprint("translate", __name__, url_prefix="/translate")


@dataclass
class TranslateRequest:
    text: str
    to_lang: str


@dataclass
class TranslateResponse:
    success: bool
    translation: str


# private translator stub
def _translate(text: str, _to_lang: str) -> str:
    """
    Stub translation function: always returns the same text.
    """
    return text  # or replace with any static string


@bp.route("/", methods=["POST"])  # type: ignore[misc]
def translate_text() -> Response:
    payload = request.get_json(force=True) or {}
    # Validate required fields
    if not payload.get("text") or not payload.get("to_lang"):
        abort(400, description="Both 'text' and 'to_lang' fields are required.")

    # Create request object
    try:
        req = TranslateRequest(**payload)
    except TypeError as e:
        abort(400, description=str(e))

    # Translate the text
    translated = _translate(req.text, req.to_lang)

    # Return response
    return jsonify(
        TranslateResponse(success=True, translation=translated).__dict__
    ) 