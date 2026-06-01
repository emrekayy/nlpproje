from fastapi import APIRouter, Query

from app.schemas.product import SemanticSearchResponse
from app.services.retrieval_service import retrieval_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/semantic", response_model=SemanticSearchResponse)
def semantic_search(
    q: str = Query(..., min_length=2, description="Natural language search query"),
    limit: int = Query(8, ge=1, le=20),
) -> SemanticSearchResponse:
    return SemanticSearchResponse(**retrieval_service.semantic_search(q, limit=limit))
