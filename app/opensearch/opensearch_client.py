import os
from functools import lru_cache
from opensearchpy import OpenSearch
from app.core.config import OPENSEARCH_HOST, OPENSEARCH_PORT, OPENSEARCH_USER, OPENSEARCH_PASSWORD, OPENSEARCH_USE_SSL, OPENSEARCH_VERIFY_CERTS, OPENSEARCH_HTTP_COMPRESS

@lru_cache
def get_opensearch_client() -> OpenSearch:
    kwargs = {
        "hosts": [{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
        "http_compress": OPENSEARCH_HTTP_COMPRESS,
        "use_ssl": OPENSEARCH_USE_SSL,
        "verify_certs": OPENSEARCH_VERIFY_CERTS,
    }

    if OPENSEARCH_PASSWORD:
        kwargs["http_auth"] = (OPENSEARCH_USER, OPENSEARCH_PASSWORD)

    return OpenSearch(**kwargs)