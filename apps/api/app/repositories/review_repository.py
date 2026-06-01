import json
from functools import cached_property

from app.core.config import settings
from app.repositories.real_review_repository import real_review_repository


class ReviewRepository:
    def _to_legacy_review(self, review: dict) -> dict:
        if "text" in review and "timestamp" in review:
            return review

        rating = review.get("rating")
        return {
            "id": review["id"],
            "model": review["model"],
            "rating": max(1, min(5, int(round(rating)))) if rating is not None else 3,
            "text": review["review_text"],
            "aspect": review.get("aspect") or "general",
            "sentiment": review.get("sentiment") or "neutral",
            "source": review.get("source") or "Real Review Dataset",
            "timestamp": review.get("date") or "1970-01-01T00:00:00Z",
            "review_title": review.get("review_title"),
            "verified_purchase": review.get("verified_purchase"),
            "source_url": review.get("source_url"),
            "source_type": "Real User Review",
            "source_platform": review.get("source") or "Real Review Dataset",
            "metadata": review.get("metadata", {}),
        }

    @cached_property
    def _mock_reviews(self) -> list[dict]:
        with settings.reviews_seed_file.open("r", encoding="utf-8") as seed_file:
            return json.load(seed_file)["reviews"]

    @cached_property
    def _reviews(self) -> list[dict]:
        real_reviews = real_review_repository.list_reviews()
        if not real_reviews:
            return self._mock_reviews

        real_models = {review["model"] for review in real_reviews}
        merged_reviews = [self._to_legacy_review(review) for review in real_reviews]
        merged_reviews.extend(
            review for review in self._mock_reviews if review["model"] not in real_models
        )
        return merged_reviews

    def list_reviews(self) -> list[dict]:
        return self._reviews

    def get_reviews_by_model_name(self, model_name: str) -> list[dict]:
        real_reviews = real_review_repository.get_reviews_by_model_name(model_name)
        if real_reviews:
            return [self._to_legacy_review(review) for review in real_reviews]
        return [review for review in self._mock_reviews if review["model"] == model_name]


review_repository = ReviewRepository()
