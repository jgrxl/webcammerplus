from dataclasses import asdict, dataclass
from flask import Blueprint, Response, abort, jsonify, request
from services.write_service import write_text


bp = Blueprint("write", __name__, url_prefix="/write")


@dataclass
class WriteRequest:
    style: str
    text: str
    to_lang: str


@dataclass
class WriteResponse:
    success: bool
    written_text: str


@bp.route("/", methods=["POST"])
def write() -> Response:
    payload = request.get_json(force=True) or {}
    required_fields = ["style", "text", "to_lang"]
    
    missing_fields = [field for field in required_fields if field not in payload]
    if missing_fields:
        abort(400, description=f"Missing required fields: {', '.join(missing_fields)}")

    try:
        req = WriteRequest(**payload)
    except TypeError as e:
        abort(400, description=str(e))

    generated_text = write_text(req.style, req.text, req.to_lang)
    out = WriteResponse(success=True, written_text=generated_text)

    resp = jsonify(asdict(out))
    resp.status_code = 200
    return resp