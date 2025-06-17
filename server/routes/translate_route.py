from dataclasses import asdict, dataclass
from typing import Optional

from flask import request
from flask_restx import Namespace, Resource, fields

from common.error_handlers import ExternalServiceError, ValidationError
from common.response_models import create_error_model
from core.dependencies import get_translate_service
from utils.auth import check_usage_limits, requires_auth

api = Namespace("translate", description="Translation operations")

translate_request_model = api.model(
    "TranslateRequest",
    {
        "text": fields.String(required=True, description="Text to translate"),
        "to_lang": fields.String(required=True, description="Target language code"),
        "from_lang": fields.String(
            required=False,
            description="Source language code (auto-detect if not provided)",
        ),
    },
)

translate_response_model = api.model(
    "TranslateResponse",
    {
        "success": fields.Boolean(description="Success status"),
        "translation": fields.String(description="Translated text"),
    },
)

error_model = create_error_model(api)


@dataclass
class TranslateRequest:
    text: str
    to_lang: str
    from_lang: Optional[str] = None


@dataclass
class TranslateResponse:
    success: bool
    translation: str


@api.route("/")
class Translate(Resource):
    @api.expect(translate_request_model)
    @api.response(200, "Success", translate_response_model)
    @api.response(400, "Bad Request", error_model)
    @api.response(401, "Unauthorized", error_model)
    @api.response(429, "Usage Limit Exceeded", error_model)
    @api.doc("translate_text")
    @requires_auth
    @check_usage_limits("translations")
    def post(self):
        """Translate text from one language to another"""
        payload = request.get_json(force=True) or {}
        if "text" not in payload or "to_lang" not in payload:
            raise ValidationError("Both 'text' and 'to_lang' fields are required.")

        try:
            req = TranslateRequest(**payload)
        except TypeError as e:
            raise ValidationError(f"Invalid request data: {str(e)}")

        try:
            service = get_translate_service()
            translated = service.translate_text(req.text, req.to_lang, req.from_lang)
            out = TranslateResponse(success=True, translation=translated)

            return asdict(out), 200
        except ValueError as e:
            raise ExternalServiceError("Novita AI", str(e))
        except Exception as e:
            raise ExternalServiceError("Translation", f"Translation failed: {str(e)}")
