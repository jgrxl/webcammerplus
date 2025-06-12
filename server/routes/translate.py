# server/routes/translate.py
from dataclasses import asdict, dataclass

from flask import Blueprint, Response, abort, jsonify, request

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
def _translate(text: str, to_lang: str) -> str:
    """
    Stub translation function: always returns the same text.
    """
    return text  # or replace with any static string


@bp.route("/", methods=["POST"])  # type: ignore[misc]
def translate_text() -> Response:
    payload = request.get_json(force=True) or {}
    # Validate required fields
    if "text" not in payload or "to_lang" not in payload:
        abort(400, description="Both 'text' and 'to_lang' fields are required.")

    # Build request object
    try:
        req = TranslateRequest(**payload)
    except TypeError as e:
        abort(400, description=str(e))

    # Perform translation via private stub
    translated = _translate(req.text, req.to_lang)

    out = TranslateResponse(success=True, translation=translated)
    return jsonify(asdict(out)), 200
