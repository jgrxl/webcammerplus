import os
import json
import elasticsearch

def load_mappings() -> None:
    """
    Load index mappings from JSON files in ../mappings/,
    creating each index if it doesn't already exist.
    Any error (BadRequest, HTTP, network) is caught and logged.
    """
    # __file__ is server/client/es_client.py, so go up one to server/, then into
    # mappings/
    base_dir = os.path.dirname(__file__)
    mappings_dir = os.path.normpath(os.path.join(base_dir, "..", "mappings"))

    if not os.path.isdir(mappings_dir):
        print(f"[es_client] mappings directory not found: {mappings_dir}")
        return

    for fname in os.listdir(mappings_dir):
        if not fname.endswith(".json"):
            continue

        index_name = fname[:-5]  # strip ".json"
        mapping_path = os.path.join(mappings_dir, fname)

        with open(mapping_path, "r", encoding="utf-8") as f:
            mapping = json.load(f)

        try:
            if not es.indices.exists(index=index_name):
                es.indices.create(index=index_name, body=mapping)
                print(f"[es_client] Created index '{index_name}'.")
            else:
                print(f"[es_client] Index '{index_name}' already exists.")
        except (elasticsearch.ElasticsearchException, OSError, IOError) as err:
            # catches ElasticsearchException, HTTP errors, network issues, etc.
            print(f"[es_client] load_mappings failed for '{index_name}': {err}") 