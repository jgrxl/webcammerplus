from flask import Blueprint, request, jsonify
from client.es_client import es     # ← this now exists
bp = Blueprint("api", __name__)

@bp.route("/<index_name>/document", methods=["POST"])
def add_document(index_name):
    doc = request.get_json(force=True)
    res = es.index(index=index_name, body=doc)
    return jsonify(res)

@bp.route("/<index_name>/search")
def search(index_name):
    q = request.args.get("q","")
    body = {"query": {"multi_match": {"query": q, "fields": ["*"]}}}
    res = es.search(index=index_name, body=body)
    return jsonify(res["hits"])
