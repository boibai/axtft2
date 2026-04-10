import httpx
from app.core.config import RERANK_URL

def make_rerank_text(doc: dict) -> str:
    return "\n".join([
        str(doc.get("keywords", "") or ""),
        str(doc.get("vector_text", "") or ""),
        str(doc.get("content", "") or ""),
    ]).strip()

def dedupe_by_filename(hits: list[dict]) -> list[dict]:
    seen = set()
    deduped = []

    for hit in hits:
        source = hit.get("_source", {})
        filename = source.get("filename")

        if not filename:
            continue

        if filename in seen:
            continue

        seen.add(filename)
        deduped.append(hit)

    return deduped

def search_similar(client, index_name: str, query: str, query_vector: list[float], k: int = 10) -> list[dict]:
    body = {
        "size": k * 3,
        "query": {
            "hybrid": {
                "queries": [
                    {
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["error_message^3", "keywords^2"]
                        }
                    }
                    },
                    {
                        "knn": {
                            "vector": {
                                "vector": query_vector,
                                "k": k * 3
                            }
                        }
                    }
                ]
            }
        }
    }

    resp = client.search(index=index_name, body=body)
    hits = resp["hits"]["hits"]

    deduped_hits = dedupe_by_filename(hits)
    return deduped_hits[:k]


async def rerank_documents(query: str, docs: list[dict], top_n: int = 5) -> list[dict]:
    if not docs:
        return []

    passages = [make_rerank_text(doc) for doc in docs]

    async with httpx.AsyncClient(timeout=30.0) as client_http:
        resp = await client_http.post(
            RERANK_URL,
            json={
                "query": str(query),
                "passages": passages,
                "max_length": 512,
            },
        )
        resp.raise_for_status()
        scores = resp.json()["scores"]

    scored_docs = []
    for doc, score in zip(docs, scores):
        item = dict(doc)
        item["rerank_score"] = float(score)
        scored_docs.append(item)

    scored_docs.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored_docs[:top_n]