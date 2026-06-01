from fastapi import APIRouter

from app.schemas.product import ProductAnalytics
from app.services.catalog_service import catalog_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/{identifier}", response_model=ProductAnalytics)
def get_analytics(identifier: str) -> ProductAnalytics:
    # Reuse cached enriched product instead of recomputing analytics
    product = catalog_service.get_product(identifier)
    return ProductAnalytics(**product["analytics"])
