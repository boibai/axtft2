from opensearchpy import OpenSearch
from opensearchpy.exceptions import NotFoundError, RequestError
from app.utils.preprocess import (
        bulk_insert,
        embed_texts,
        build_search_doc,
        get_error_file,
        get_error_list)
from app.utils.search import (
    search_similar,
    rerank_documents
)

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
        if not row.get("index").startswith(".") and not row.get("index").startswith("top_"):
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
        

async def index_errors_service(client, index_name: str, date: str, filename: str):
    try:
        # file_list = get_error_list(date)
        
        if not filename:
            return {
                "success": True,
                "index_name": index_name,
                "date": date,
                "file_count": 0,
                "indexed_count": 0,
                "failed_count": 0,
                "message": "No files found",
            }

        files = get_error_file(date, [filename])

        search_docs = []

        for i, f in enumerate(files):
            output_json = f.get("output_json") or {}
            cause_list = output_json.get("causeList") or []

            if not cause_list:
                continue

            search_docs.append(
                build_search_doc(file=f, date=date, filename=[filename][i])
            )


        vector_text_list = [doc["vector_text"] for doc in search_docs]
        embeddings = await embed_texts(vector_text_list)

        final_docs = []
        for doc, emb in zip(search_docs, embeddings):
            doc["vector"] = emb

            final_docs.append({
                "_op_type": "index",
                "_index": index_name,
                "_id": doc['filename'],
                "_source": doc,
            })

        success, failed = bulk_insert(client, final_docs)

        return {
            "success": True,
            "index_name": index_name,
            "date": date,
            "file_count": len([filename]),
            "indexed_count": success,
            "failed_count": failed,
            "message": None,
        }

    except Exception as e:
        return {
            "success": False,
            "index_name": index_name,
            "date": date,
            "file_count": 0,
            "indexed_count": 0,
            "failed_count": 0,
            "message": str(e),
        }
        
        
async def search_errors_service(
    client,
    index_name: str,
    query: str,
    top_k: int,
    rerank_top_n: int,
):
    try:
        query_vector = (await embed_texts([query]))[0]

        hybrid_hits = search_similar(
            client=client,
            index_name=index_name,
            query=query,
            query_vector=query_vector,
            k=top_k,
        )

        source_docs = [hit["_source"] for hit in hybrid_hits]

        reranked_docs = await rerank_documents(
            query=query,
            docs=source_docs,
            top_n=rerank_top_n,
        )

        final_results = []
        for doc in reranked_docs:
            raw_doc = get_error_file(doc["date"], [doc["filename"]])[0]
            final_results.append({
                "date": doc["date"],
                "filename": doc["filename"],
                "request_id": doc.get("request_id"),
                "rerank_score": doc.get("rerank_score"),
                "raw_data": raw_doc,
            })

        return {
            "success": True,
            "query": query,
            "index_name": index_name,
            "hybrid_count": len(hybrid_hits),
            "rerank_count": len(final_results),
            "results": final_results,
            "message": None,
        }

    except Exception as e:
        return {
            "success": False,
            "query": query,
            "index_name": index_name,
            "hybrid_count": 0,
            "rerank_count": 0,
            "results": [],
            "message": str(e),
        }
        
        
def get_document_by_id(client, index_name: str, doc_id: str):
    try:
        resp = client.get(index=index_name, id=doc_id)

        return {
            "success": True,
            "index_name": index_name,
            "doc_id": doc_id,
            "found": True,
            "document": resp["_source"],
            "message": None,
        }

    except Exception as e:
        if hasattr(e, "status_code") and e.status_code == 404:
            return {
                "success": True,
                "index_name": index_name,
                "doc_id": doc_id,
                "found": False,
                "document": None,
                "message": "Document not found",
            }

        return {
            "success": False,
            "index_name": index_name,
            "doc_id": doc_id,
            "found": False,
            "document": None,
            "message": str(e),
        }