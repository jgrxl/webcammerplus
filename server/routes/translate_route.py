from dataclasses import asdict, dataclass
from typing import Optional
from flask import Blueprint, Response, abort, jsonify, request
from server.services.translate_service import translate_text


bp = Blueprint("translate", __name__, url_prefix="/translate")


@dataclass
class TranslateRequest:
    text: str
    to_lang: str
    from_lang: Optional[str] = None


@dataclass
class TranslateResponse:
    success: bool
    translation: str


@bp.route("/", methods=["POST"])
def translate() -> Response:
    payload = request.get_json(force=True) or {}
    if "text" not in payload or "to_lang" not in payload:
        abort(400, description="Both 'text' and 'to_lang' fields are required.")

    try:
        req = TranslateRequest(**payload)
    except TypeError as e:
        abort(400, description=str(e))

    translated = translate_text(req.text, req.to_lang, req.from_lang)
    out = TranslateResponse(success=True, translation=translated)

    resp = jsonify(asdict(out))
    resp.status_code = 200
    return resp
