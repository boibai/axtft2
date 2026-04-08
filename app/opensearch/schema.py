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