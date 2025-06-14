from dataclasses import asdict, dataclass
from flask import Blueprint, Response, abort, jsonify, request
from services.reply_service import reply_text


bp = Blueprint("reply", __name__, url_prefix="/reply")


@dataclass
class ReplyRequest:
    original_text: str
    response_idea: str
    style: str
    to_lang: str


@dataclass
class ReplyResponse:
    success: bool
    reply: str


@bp.route("/", methods=["POST"])
def reply() -> Response:
    payload = request.get_json(force=True) or {}
    required_fields = ["original_text", "response_idea", "style", "to_lang"]
    
    missing_fields = [field for field in required_fields if field not in payload]
    if missing_fields:
        abort(400, description=f"Missing required fields: {', '.join(missing_fields)}")

    try:
        req = ReplyRequest(**payload)
    except TypeError as e:
        abort(400, description=str(e))

    generated_reply = reply_text(req.original_text, req.response_idea, req.style, req.to_lang)
    out = ReplyResponse(success=True, reply=generated_reply)

    resp = jsonify(asdict(out))
    resp.status_code = 200
    return resp