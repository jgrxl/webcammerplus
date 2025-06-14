from dataclasses import asdict, dataclass
from flask import Response, abort, jsonify, request
from flask_restx import Namespace, Resource, fields
from services.reply_service import reply_text
from utils.auth import requires_auth, check_usage_limits


api = Namespace('reply', description='Reply generation operations')

reply_request_model = api.model('ReplyRequest', {
    'original_text': fields.String(required=True, description='The original message to reply to'),
    'response_idea': fields.String(required=True, description='General idea or direction for the response'),
    'style': fields.String(required=True, description='Writing style (e.g., formal, casual, professional)'),
    'to_lang': fields.String(required=True, description='Target language for the reply')
})

reply_response_model = api.model('ReplyResponse', {
    'success': fields.Boolean(description='Success status'),
    'reply': fields.String(description='Generated reply text')
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})


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


@api.route('/')
class Reply(Resource):
    @api.expect(reply_request_model)
    @api.response(200, 'Success', reply_response_model)
    @api.response(400, 'Bad Request', error_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.response(429, 'Usage Limit Exceeded', error_model)
    @api.doc('generate_reply')
    @requires_auth
    @check_usage_limits('replies')
    def post(self):
        """Generate AI-powered replies to messages with specified style and language"""
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