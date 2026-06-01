from app.repositories.review_repository import review_repository
from app.repositories.real_review_repository import real_review_repository
from app.services.catalog_service import ProductNotFoundError, catalog_service


class ReviewService:
    def _resolve_real_review_target(self, identifier: str) -> dict:
        try:
            product = catalog_service.get_product(identifier)
            return {"slug": product["slug"], "name": product["name"]}
        except ProductNotFoundError:
            model_name = real_review_repository.resolve_model_identifier(identifier)
            if model_name is None:
                raise
            return {"slug": model_name.lower().replace(" ", "-"), "name": model_name}

    def get_summary(self, identifier: str) -> dict:
        product = catalog_service.get_product(identifier)
        return {
            "slug": product["slug"],
            "name": product["name"],
            "review_summary": product["analysis"]["review_summary"],
        }

    def list_reviews(self, identifier: str) -> dict:
        product = catalog_service.get_product(identifier)
        reviews = review_repository.get_reviews_by_model_name(product["name"])
        return {
            "slug": product["slug"],
            "name": product["name"],
            "total": len(reviews),
            "items": reviews,
        }

    def list_real_reviews(self, identifier: str) -> dict:
        target = self._resolve_real_review_target(identifier)
        reviews = real_review_repository.get_reviews_by_model_name(target["name"])
        return {
            "slug": target["slug"],
            "name": target["name"],
            "total": len(reviews),
            "items": reviews,
        }

    def get_real_review_stats(self, identifier: str) -> dict:
        target = self._resolve_real_review_target(identifier)
        stats = real_review_repository.get_stats_by_model_name(target["name"])
        return {
            "slug": target["slug"],
            "name": target["name"],
            **stats,
        }


review_service = ReviewService()
