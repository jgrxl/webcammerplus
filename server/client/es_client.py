# server/client/es_client.py

import json
import os

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import TransportError


# -----------------------------------------------------------------------------
# Configure your ES client however makes sense for your environment:
#   - via environment variable ES_HOSTS (e.g. "http://localhost:9200")
#   - defaulting to localhost
# -----------------------------------------------------------------------------
_ES_HOSTS = os.getenv("ES_HOSTS", "http://localhost:9200").split(",")
es = Elasticsearch(_ES_HOSTS)


def load_mappings() -> None:
    """
    Load index mappings from JSON files in ../mappings/,
    creating each index if it doesn't already exist.
    Any error (BadRequest, HTTP, network) is caught and logged.
    """
    base_dir = os.path.dirname(__file__)
    mappings_dir = os.path.normpath(os.path.join(base_dir, "..", "mappings"))

    if not os.path.isdir(mappings_dir):
        print(f"[es_client] mappings directory not found: {mappings_dir}")
        return

    for fname in os.listdir(mappings_dir):
        if not fname.endswith(".json"):
            continue

        index_name = fname[:-5]  # strip “.json”
        mapping_path = os.path.join(mappings_dir, fname)

        with open(mapping_path, "r", encoding="utf-8") as f:
            mapping = json.load(f)

        try:
            if not es.indices.exists(index=index_name):
                es.indices.create(index=index_name, body=mapping)
                print(f"[es_client] Created index '{index_name}'.")
            else:
                print(f"[es_client] Index '{index_name}' already exists.")
        except TransportError as err:  #
            print(f"[es_client] load_mappings failed for '{index_name}': {err}")
