from fastapi import APIRouter, HTTPException

from app.opensearch.opensearch_client import get_opensearch_client
from app.opensearch.schema import ( 
    CreateIndexRequest, 
    CreateIndexResponse, 
    DeleteIndexRequest, 
    DeleteIndexResponse,
    ListIndicesResponse,
    ListIndicesResponseItem,
    UpdateIndexMappingRequest,
    UpdateIndexResponse,
    GetIndexPropertiesRequest,
    GetIndexPropertiesResponse,
    IndexErrorResponse,
    IndexErrorRequest,
    SearchErrorResponse,
    SearchErrorRequest
    )

from app.application.opensearch_service import (
    create_index_raw,
    delete_index,
    list_indices,
    update_index_mapping,
    get_index_properties,
    index_errors_service,
    search_errors_service
    
)

router = APIRouter(prefix="/opensearch", tags=["opensearch"])

@router.post("/index/create", response_model=CreateIndexResponse)
def create_index_raw_api(req: CreateIndexRequest):
    client = get_opensearch_client()

    result = create_index_raw(
        client=client,
        index_name=req.index_name,
        body=req.body,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return CreateIndexResponse(**result)


@router.post("/index/delete", response_model=DeleteIndexResponse)
def delete_index_api(req: DeleteIndexRequest):
    client = get_opensearch_client()

    result = delete_index(
        client=client,
        index_name=req.index_name,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return DeleteIndexResponse(**result)


@router.get("/index/list", response_model=ListIndicesResponse)
def list_indices_api():
    client = get_opensearch_client()

    result = list_indices(client=client)

    items = [ListIndicesResponseItem(**x) for x in result["indices"]]

    return ListIndicesResponse(
        success=result["success"],
        count=result["count"],
        indices=items,
    )


@router.post("/index/update", response_model=UpdateIndexResponse)
def update_index_mapping_api(req: UpdateIndexMappingRequest):
    client = get_opensearch_client()

    result = update_index_mapping(
        client=client,
        index_name=req.index_name,
        properties=req.properties,
    )

    if result is None:
        raise HTTPException(status_code=500, detail="update_index_mapping returned None")

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return UpdateIndexResponse(**result)


@router.post("/index/properties", response_model=GetIndexPropertiesResponse)
def get_index_properties_api(req: GetIndexPropertiesRequest):
    client = get_opensearch_client()

    result = get_index_properties(
        client=client,
        index_name=req.index_name,
    )

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("message", "Index not found"))

    return GetIndexPropertiesResponse(**result)


@router.post("/preprocess/errors", response_model=IndexErrorResponse)
async def index_errors_api(req: IndexErrorRequest):
    client = get_opensearch_client()

    result = await index_errors_service(
        client=client,
        index_name=req.index_name,
        date=req.date,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result.get("message", "Indexing failed"),
        )

    return IndexErrorResponse(**result)

@router.post("/search", response_model=SearchErrorResponse)
async def search_errors_api(req: SearchErrorRequest):
    client = get_opensearch_client()

    result = await search_errors_service(
        client=client,
        index_name=req.index_name,
        query=req.query,
        top_k=req.top_k,
        rerank_top_n=req.rerank_top_n,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result.get("message", "Search failed"),
        )

    return SearchErrorResponse(**result)