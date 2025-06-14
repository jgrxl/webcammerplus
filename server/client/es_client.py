import json
import os
from typing import Optional

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import BadRequestError


class ESClient:
    def __init__(self, hosts: Optional[str] = None):
        """Initialize Elasticsearch client.

        Args:
            hosts: Comma-separated list of ES hosts. Defaults to ES_HOSTS env var or localhost.
        """
        self._hosts = hosts or os.getenv("ES_HOSTS", "http://localhost:9200")
        self.client = Elasticsearch(hosts=self._hosts)

    def load_mappings(self) -> None:
        """Load index mappings from JSON files in ../mappings/.

        Creates each index if it doesn't exist. Catches and logs any errors.
        """
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
                mapping_doc = json.load(f)

            settings = mapping_doc.get("settings")
            mappings = mapping_doc.get("mappings")

            try:
                if not self.client.indices.exists(index=index_name):
                    if settings or mappings:
                        self.client.indices.create(
                            index=index_name, settings=settings, mappings=mappings
                        )
                    else:
                        self.client.indices.create(index=index_name)
                    print(f"[es_client] Created index '{index_name}'.")
                else:
                    print(f"[es_client] Index '{index_name}' already exists.")
            except BadRequestError as err:
                print(f"[es_client] load_mappings failed for '{index_name}': {err}")

    def close(self) -> None:
        """Close the Elasticsearch client connection."""
        self.client.close()
