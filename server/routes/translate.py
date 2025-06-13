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


def _translate(text: str) -> str:
    """Stub translation function: always returns the same text."""
    return text


@bp.route("/", methods=["POST"])
def translate_text() -> Response:
    payload = request.get_json(force=True) or {}
    if "text" not in payload or "to_lang" not in payload:
        abort(400, description="Both 'text' and 'to_lang' fields are required.")

    try:
        req = TranslateRequest(**payload)
    except TypeError as e:
        abort(400, description=str(e))

    translated = _translate(req.text)
    out = TranslateResponse(success=True, translation=translated)

    resp = jsonify(asdict(out))
    resp.status_code = 200
    return resp
