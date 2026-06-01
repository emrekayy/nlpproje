from fastapi import APIRouter

from app.schemas.product import ProductReviewsResponse, RealProductReviewsResponse, RealReviewStatsResponse
from app.services.review_service import review_service

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/real/{identifier}/stats", response_model=RealReviewStatsResponse)
def get_real_review_stats(identifier: str) -> RealReviewStatsResponse:
    return RealReviewStatsResponse(**review_service.get_real_review_stats(identifier))


@router.get("/real/{identifier}", response_model=RealProductReviewsResponse)
def get_real_reviews(identifier: str) -> RealProductReviewsResponse:
    return RealProductReviewsResponse(**review_service.list_real_reviews(identifier))


@router.get("/{identifier}", response_model=ProductReviewsResponse)
def get_reviews(identifier: str) -> ProductReviewsResponse:
    return ProductReviewsResponse(**review_service.list_reviews(identifier))
