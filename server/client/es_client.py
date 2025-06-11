# server/client/es_client.py

import os
import json
from elasticsearch import Elasticsearch, exceptions as es_exceptions

# ─── Configuration ───────────────────────────────────────────────────────────────
ES_HOSTS    = ["http://localhost:9200"]
MAPPING_DIR = os.path.join(os.path.dirname(__file__), "..", "mapping")  
#                                                          ^---- singular

# ─── Exported client instance ────────────────────────────────────────────────────
es = Elasticsearch(ES_HOSTS)   # ← this name must match your import

def load_mappings():
    """
    For each JSON file under `server/mapping/`, create or update the index.
    """
    for fname in os.listdir(MAPPING_DIR):
        if not fname.lower().endswith(".json"):
            continue

        index_name = os.path.splitext(fname)[0]
        path       = os.path.join(MAPPING_DIR, fname)

        with open(path, "r", encoding="utf-8") as f:
            body = json.load(f)

        try:
            if not es.indices.exists(index=index_name):
                es.indices.create(index=index_name, body=body)
                print(f"[es_client] Created index {index_name}")
            else:
                es.indices.put_mapping(index=index_name,
                                       body=body.get("mappings", {}))
                print(f"[es_client] Updated mapping for {index_name}")
        except es_exceptions.ElasticsearchException as err:
            print(f"[es_client] ERROR for {index_name}: {err}")
