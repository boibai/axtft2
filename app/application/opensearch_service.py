from opensearchpy import OpenSearch
from opensearchpy.exceptions import NotFoundError, RequestError


def create_index_raw(client: OpenSearch, index_name: str, body: dict) -> dict:
    if client.indices.exists(index=index_name):
        return {
            "success": True,
            "created": False,
            "message": f"Index already exists: {index_name}",
            "index_name": index_name,
        }

    try:
        client.indices.create(index=index_name, body=body)
        return {
            "success": True,
            "created": True,
            "message": f"Created index: {index_name}",
            "index_name": index_name,
        }
    except RequestError as e:
        return {
            "success": False,
            "created": False,
            "message": str(e),
            "index_name": index_name,
        }


def delete_index(client: OpenSearch, index_name: str) -> dict:
    if not client.indices.exists(index=index_name):
        return {
            "success": True,
            "deleted": False,
            "message": f"Index not found: {index_name}",
            "index_name": index_name,
        }

    try:
        client.indices.delete(index=index_name)
        return {
            "success": True,
            "deleted": True,
            "message": f"Deleted index: {index_name}",
            "index_name": index_name,
        }
    except RequestError as e:
        return {
            "success": False,
            "deleted": False,
            "message": str(e),
            "index_name": index_name,
        }


def list_indices(client: OpenSearch) -> dict:
    rows = client.cat.indices(format="json")

    indices = []
    for row in rows:
        if not row.get("index").startswith("."):
            indices.append({
                "index_name": row.get("index"),
                "health": row.get("health"),
                "status": row.get("status"),
                "docs_count": row.get("docs.count"),
                "store_size": row.get("store.size"),
            })

    return {
        "success": True,
        "count": len(indices),
        "indices": indices,
    }


def update_index_mapping(client, index_name: str, properties: dict) -> dict:

    if not client.indices.exists(index=index_name):
        return {
            "success": False,
            "updated": False,
            "message": f"Index not found: {index_name}",
            "index_name": index_name,
            "result": None,
        }

    try:
        res = client.indices.put_mapping(
            index=index_name,
            body={"properties": properties},
        )

        return {
            "success": True,
            "updated": True,
            "message": f"Updated mapping for index: {index_name}",
            "index_name": index_name,
            "result": res,
        }

    except Exception as e:
        return {
            "success": False,
            "updated": False,
            "message": str(e),
            "index_name": index_name,
            "result": None,
        }


def get_index_properties(client: OpenSearch, index_name: str) -> dict:
    if not client.indices.exists(index=index_name):
        return {
            "success": False,
            "index_name": index_name,
            "properties": {},
            "message": f"Index not found: {index_name}",
        }

    try:
        mapping = client.indices.get_mapping(index=index_name)
        properties = (
            mapping.get(index_name, {})
            .get("mappings", {})
            .get("properties", {})
        )

        return {
            "success": True,
            "index_name": index_name,
            "properties": properties,
        }
    except (RequestError, NotFoundError) as e:
        return {
            "success": False,
            "index_name": index_name,
            "properties": {},
            "message": str(e),
        }