from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from FlagEmbedding import BGEM3FlagModel, FlagReranker
from app.core.config import EMBEDDING_MODEL, RERANK_MODEL

app = FastAPI(title="Model Server")

embedding_model = None
reranker_model = None


class EmbedRequest(BaseModel):
    texts: List[str]


class RerankRequest(BaseModel):
    query: str
    passages: List[str]
    max_length: int = 512


@app.on_event("startup")
def startup():
    global embedding_model, reranker_model

    embedding_model = BGEM3FlagModel(
        EMBEDDING_MODEL,
        use_fp16=True,
    )
    reranker_model = FlagReranker(
        RERANK_MODEL,
        use_fp16=False,
    )


@app.post("/embed")
def embed(req: EmbedRequest):
    result = embedding_model.encode(req.texts)
    return {
        "dense_vecs": result["dense_vecs"].tolist()
    }


@app.post("/rerank")
def rerank(req: RerankRequest):
    pairs = [[req.query, p] for p in req.passages]
    scores = reranker_model.compute_score(
        pairs,
        max_length=req.max_length,
    )
    return {
        "scores": [float(x) for x in scores]
    }