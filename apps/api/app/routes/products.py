from fastapi import APIRouter

from app.schemas.product import (
    ProductDetailResponse,
    ProductIssuesResponse,
    ProductListResponse,
    ProductSummaryResponse,
)
from app.services.catalog_service import catalog_service
from app.services.decision_support_service import decision_support_service
from app.services.issue_service import issue_service
from app.services.review_service import review_service

router = APIRouter(prefix="/products", tags=["products"])

_INTERNAL_KEYS = {"analysis", "analytics"}


@router.get("", response_model=ProductListResponse)
def list_products() -> ProductListResponse:
    items = [
        {key: value for key, value in item.items() if key not in _INTERNAL_KEYS}
        for item in catalog_service.list_products()
    ]
    return ProductListResponse(items=items, total=len(items))


@router.get("/{identifier}", response_model=ProductDetailResponse)
def get_product(identifier: str) -> ProductDetailResponse:
    product = catalog_service.get_product(identifier)
    base_fields = {
        key: value
        for key, value in product.items()
        if key not in _INTERNAL_KEYS
    }
    return ProductDetailResponse(
        **base_fields,
        review_summary=product["analysis"]["review_summary"],
        common_issues=product["analysis"]["common_issues"],
        decision_support=decision_support_service.build_decision_support(product),
        analytics=product["analytics"],
    )


@router.get("/{slug}/summary", response_model=ProductSummaryResponse)
def get_summary(slug: str) -> ProductSummaryResponse:
    return ProductSummaryResponse(**review_service.get_summary(slug))


@router.get("/{slug}/issues", response_model=ProductIssuesResponse)
def get_issues(slug: str) -> ProductIssuesResponse:
    return ProductIssuesResponse(**issue_service.get_issues(slug))
