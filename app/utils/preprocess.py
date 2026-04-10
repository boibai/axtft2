from opensearchpy.helpers import bulk
import requests
import httpx
from app.core.config import EMBEDDING_URL, ERROR_LIST_URL, ERROR_FILE_URL


async def embed_texts(texts: list[str]) -> list[list[float]]:
    async with httpx.AsyncClient(timeout=30.0) as client_http:
        resp = await client_http.post(
            EMBEDDING_URL,
            json={"texts": texts},
        )
        resp.raise_for_status()
        return resp.json()["dense_vecs"]


def format_action_plan(action_plan: list[str]) -> str:
    return "\n".join(f"{i+1}. {item}" for i, item in enumerate(action_plan))


def build_search_doc(file: dict, date: str, filename: str) -> dict:
    cause_list = file.get("output_json", {}).get("causeList", [])

    sections = []
    keyword_parts = []
    error_message = file.get("input_text")
    
    for i, cause in enumerate(cause_list, start=1):
        title = cause.get("title", "")
        cause_text = cause.get("cause", "")
        evidence = cause.get("evidence", "")
        action_plan = cause.get("actionPlan", [])

        sections.append(
            f"""[CAUSE {i}]
title: {title}
cause: {cause_text}
evidence : {evidence}
actionPlan:
{format_action_plan(action_plan)}"""
        )

        keyword_parts.append(title)
        keyword_parts.append(evidence)

    vector_text = f"[ERROR MESSAGE]\n{error_message["message"]}\n\n"+"\n\n".join(sections).strip()
    keywords = " ".join(x for x in keyword_parts if x).strip()

    return {
        "date": date,
        "filename": filename,
        "request_id": file.get("request_id"),
        "timestamp": file.get("timestamp"),
        "model_name": file.get("model_name"),
        "error_message": error_message["message"],
        "vector_text": vector_text,
        "keywords": keywords,
    }


def get_error_list(date: str):
    resp = requests.post(ERROR_LIST_URL, json={"date": date}, timeout=30)
    resp.raise_for_status()
    return resp.json().get("files", [])


def get_error_file(date: str, file_list: list):
    result = []
    for file in file_list:
        resp = requests.post(
            ERROR_FILE_URL,
            json={"date": date, "filename": file},
            timeout=60,
        )
        resp.raise_for_status()
        result.append(resp.json())
    return result


def bulk_insert(client, docs: list[dict]) -> tuple[int, int]:
    success, failed = bulk(
        client,
        docs,
        stats_only=True,
        raise_on_error=False,
        refresh=True,
    )
    return success, failed