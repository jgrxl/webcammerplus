from dataclasses import asdict, dataclass
from typing import Optional
from flask import Response, abort, jsonify, request
from flask_restx import Namespace, Resource, fields
from services.translate_service import translate_text
from utils.auth import requires_auth, check_usage_limits


api = Namespace('translate', description='Translation operations')

translate_request_model = api.model('TranslateRequest', {
    'text': fields.String(required=True, description='Text to translate'),
    'to_lang': fields.String(required=True, description='Target language code'),
    'from_lang': fields.String(required=False, description='Source language code (auto-detect if not provided)')
})

translate_response_model = api.model('TranslateResponse', {
    'success': fields.Boolean(description='Success status'),
    'translation': fields.String(description='Translated text')
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})


@dataclass
class TranslateRequest:
    text: str
    to_lang: str
    from_lang: Optional[str] = None


@dataclass
class TranslateResponse:
    success: bool
    translation: str


@api.route('/')
class Translate(Resource):
    @api.expect(translate_request_model)
    @api.response(200, 'Success', translate_response_model)
    @api.response(400, 'Bad Request', error_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.response(429, 'Usage Limit Exceeded', error_model)
    @api.doc('translate_text')
    @requires_auth
    @check_usage_limits('translations')
    def post(self):
        """Translate text from one language to another"""
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