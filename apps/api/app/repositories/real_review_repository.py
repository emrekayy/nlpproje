from app.services.real_review_ingestion_service import real_review_ingestion_service


class RealReviewRepository:
    def list_reviews(self) -> list[dict]:
        return real_review_ingestion_service.list_reviews()

    def get_reviews_by_model_name(self, model_name: str) -> list[dict]:
        return real_review_ingestion_service.get_reviews_by_model_name(model_name)

    def get_stats_by_model_name(self, model_name: str) -> dict:
        return real_review_ingestion_service.get_stats_by_model_name(model_name)

    def resolve_model_identifier(self, identifier: str) -> str | None:
        return real_review_ingestion_service.resolve_model_identifier(identifier)


real_review_repository = RealReviewRepository()
