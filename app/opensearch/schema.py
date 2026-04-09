from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class CreateIndexRequest(BaseModel):
    index_name: str
    body: Dict[str, Any]


class CreateIndexResponse(BaseModel):
    success: bool
    created: bool
    message: str
    index_name: str


class DeleteIndexRequest(BaseModel):
    index_name: str


class DeleteIndexResponse(BaseModel):
    success: bool
    deleted: bool
    message: str
    index_name: str


class ListIndicesResponseItem(BaseModel):
    index_name: str
    health: Optional[str] = None
    status: Optional[str] = None
    docs_count: Optional[str] = None
    store_size: Optional[str] = None


class ListIndicesResponse(BaseModel):
    success: bool
    count: int
    indices: List[ListIndicesResponseItem]


class UpdateIndexMappingRequest(BaseModel):
    index_name: str
    properties: Dict[str, Any]


class UpdateIndexResponse(BaseModel):
    success: bool
    updated: bool
    message: str
    index_name: str
    result: Optional[Dict[str, Any]] = None


class GetIndexPropertiesRequest(BaseModel):
    index_name: str

class GetIndexPropertiesResponse(BaseModel):
    success: bool
    index_name: str
    properties: Dict[str, Any]


class IndexErrorRequest(BaseModel):
    index_name: str
    date: str

class IndexErrorResponse(BaseModel):
    success: bool
    index_name: str
    date: str
    file_count: int
    indexed_count: int
    failed_count: int
    message: str | None = None
    
class SearchErrorRequest(BaseModel):
    index_name: str
    query: str
    top_k: int = 10
    rerank_top_n: int = 5


class SearchErrorItem(BaseModel):
    date: str
    filename: str
    request_id: str | None = None
    rerank_score: float | None = None
    raw_data: dict[str, Any]


class SearchErrorResponse(BaseModel):
    success: bool
    query: str
    index_name: str
    hybrid_count: int
    rerank_count: int
    results: list[SearchErrorItem]
    message: str | None = None