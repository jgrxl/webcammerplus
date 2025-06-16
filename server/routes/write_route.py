from dataclasses import asdict, dataclass

from flask import Response, abort, jsonify, request
from flask_restx import Namespace, Resource, fields

from services.write_service import write_text
from utils.auth import check_usage_limits, requires_auth

api = Namespace("write", description="Text generation operations")

write_request_model = api.model(
    "WriteRequest",
    {
        "style": fields.String(
            required=True,
            description="Writing style (e.g., formal, creative, technical)",
        ),
        "text": fields.String(
            required=True, description="Topic or subject to write about"
        ),
        "to_lang": fields.String(
            required=True, description="Target language for the generated content"
        ),
    },
)

write_response_model = api.model(
    "WriteResponse",
    {
        "success": fields.Boolean(description="Success status"),
        "written_text": fields.String(description="Generated text content"),
    },
)

error_model = api.model("Error", {"error": fields.String(description="Error message")})


@dataclass
class WriteRequest:
    style: str
    text: str
    to_lang: str


@dataclass
class WriteResponse:
    success: bool
    written_text: str


@api.route("/")
class Write(Resource):
    @api.expect(write_request_model)
    @api.response(200, "Success", write_response_model)
    @api.response(400, "Bad Request", error_model)
    @api.response(401, "Unauthorized", error_model)
    @api.response(429, "Usage Limit Exceeded", error_model)
    @api.doc("generate_text")
    @requires_auth
    @check_usage_limits("writes")
    def post(self):
        """Generate written content about a given topic with specified style and language"""
        payload = request.get_json(force=True) or {}
        required_fields = ["style", "text", "to_lang"]

        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            abort(
                400, description=f"Missing required fields: {', '.join(missing_fields)}"
            )

        try:
            req = WriteRequest(**payload)
        except TypeError as e:
            abort(400, description=str(e))

        generated_text = write_text(req.style, req.text, req.to_lang)
        out = WriteResponse(success=True, written_text=generated_text)

        resp = jsonify(asdict(out))
        resp.status_code = 200
        return resp
