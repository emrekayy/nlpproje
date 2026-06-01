from collections import Counter

from app.repositories.review_repository import review_repository


def _clamp(value: float, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, round(value)))


class AnalysisService:
    _aspect_labels: dict[str, str] = {
        "battery": "Pil memnuniyeti",
        "camera": "Kamera deneyimi",
        "performance": "Performans akiciligi",
        "display": "Ekran kalitesi",
        "heat": "Isinma baskisi",
        "software": "Yazilim deneyimi",
        "durability": "Ergonomi ve dayaniklilik",
        "price": "Fiyat algisi",
        "storage": "Depolama siniri",
    }

    def get_reviews_for_product(self, product: dict) -> list[dict]:
        return review_repository.get_reviews_by_model_name(product["name"])

    def _summarize_sources(self, reviews: list[dict]) -> list[str]:
        counts = Counter(r["source"] for r in reviews)
        return [f"{src}: {n}" for src, n in counts.most_common()]

    def _collect_quotes(self, reviews: list[dict]) -> list[str]:
        seen: set[str] = set()
        quotes: list[str] = []
        for review in sorted(reviews, key=lambda r: (-r["rating"], r["timestamp"])):
            if review["aspect"] in seen:
                continue
            quotes.append(review["text"])
            seen.add(review["aspect"])
            if len(quotes) == 3:
                break
        return quotes

    def _community_sentiment(
        self, average_rating: float, positive_pct: float, negative_pct: float
    ) -> str:
        if average_rating >= 4.3 and positive_pct >= 58:
            return "positive"
        if negative_pct >= 30 or average_rating < 3.6:
            return "cautious"
        return "mixed"

    def _top_strengths(self, product: dict, positive_counter: Counter[str]) -> list[str]:
        labels = [
            self._aspect_labels.get(aspect, aspect.title())
            for aspect, _ in positive_counter.most_common(3)
        ]
        return labels or product["analysis"]["review_summary"]["top_positive_aspects"][:3]

    def _top_issues(self, product: dict, negative_counter: Counter[str]) -> list[str]:
        labels = [
            self._aspect_labels.get(aspect, aspect.title())
            for aspect, _ in negative_counter.most_common(3)
        ]
        return labels or [i["title"] for i in product["analysis"]["common_issues"][:3]]

    def _recommendation_score(
        self,
        *,
        product: dict,
        average_rating: float,
        positive_pct: float,
        negative_pct: float,
        negative_counter: Counter[str],
    ) -> int:
        score = 44.0
        score += average_rating * 10
        score += positive_pct * 0.24
        score -= negative_pct * 0.17
        score += max(0, product["release_year"] - 2021) * 2.5

        slug = product["slug"]
        if "pro" in slug:
            score += 3
        if "plus" in slug or "max" in slug:
            score += 2
        if "mini" in slug:
            score -= 6

        score -= min(negative_counter.get("heat", 0) * 1.8, 6)
        score -= min(negative_counter.get("battery", 0) * 1.6, 6)
        score -= min(negative_counter.get("price", 0) * 1.2, 4)

        return _clamp(score, 45, 97)

    def _target_users(self, product: dict) -> list[str]:
        slug = product["slug"]
        users: list[str] = []

        if "mini" in slug:
            users.extend(["Kompakt telefon sevenler", "Tek elle kullanim isteyenler"])
        elif "pro" in slug:
            users.extend(["Mobil foto ve video meraklilari", "Premium deneyim isteyenler"])
        elif "plus" in slug or "max" in slug:
            users.extend(["Buyuk ekran sevenler", "Uzun pil isteyenler"])
        else:
            users.extend(["Genel kullanicilar", "Ogrenciler ve gunluk kullanim odagi olanlar"])

        if "promotion" in product["display_type"].lower():
            users.append("Akici ekran deneyimi onceligi olanlar")
        if "kamera" in product["camera_summary"].lower() or "camera" in product["camera_summary"].lower():
            users.append("Kamera kalitesine oncelik verenler")

        return users[:3]

    def build_analytics(self, product: dict) -> dict:
        reviews = self.get_reviews_for_product(product)
        total = len(reviews)

        if total == 0:
            return {
                "review_count": 0,
                "average_rating": 0.0,
                "positive_percentage": 0.0,
                "neutral_percentage": 0.0,
                "negative_percentage": 0.0,
                "top_issues": [],
                "top_strengths": [],
                "issue_frequency": [],
                "recommendation_score": 45,
                "source_summary": [],
                "community_sentiment": "mixed",
            }

        sentiment_counts = Counter(r["sentiment"] for r in reviews)
        positive_counter = Counter(
            r["aspect"] for r in reviews if r["sentiment"] == "positive"
        )
        negative_counter = Counter(
            r["aspect"] for r in reviews if r["sentiment"] == "negative"
        )

        average_rating = round(sum(r["rating"] for r in reviews) / total, 2)
        positive_pct = round(sentiment_counts["positive"] * 100 / total, 1)
        neutral_pct = round(sentiment_counts["neutral"] * 100 / total, 1)
        negative_pct = round(sentiment_counts["negative"] * 100 / total, 1)

        return {
            "review_count": total,
            "average_rating": average_rating,
            "positive_percentage": positive_pct,
            "neutral_percentage": neutral_pct,
            "negative_percentage": negative_pct,
            "top_issues": self._top_issues(product, negative_counter),
            "top_strengths": self._top_strengths(product, positive_counter),
            "issue_frequency": [
                {"aspect": a, "count": c} for a, c in negative_counter.most_common()
            ],
            "recommendation_score": self._recommendation_score(
                product=product,
                average_rating=average_rating,
                positive_pct=positive_pct,
                negative_pct=negative_pct,
                negative_counter=negative_counter,
            ),
            "source_summary": self._summarize_sources(reviews),
            "community_sentiment": self._community_sentiment(
                average_rating, positive_pct, negative_pct
            ),
        }

    def build_product_intelligence(self, product: dict) -> dict:
        analytics = self.build_analytics(product)
        review_summary = product["analysis"]["review_summary"]
        issues = product["analysis"]["common_issues"]
        reviews = self.get_reviews_for_product(product)

        return {
            "strengths": review_summary["top_positive_aspects"][:3],
            "weaknesses": review_summary["top_negative_aspects"][:3],
            "risk_signals": [issue["title"] for issue in issues[:3]],
            "issue_patterns": analytics["top_issues"],
            "community_sentiment": analytics["community_sentiment"],
            "review_count": analytics["review_count"],
            "average_rating": analytics["average_rating"],
            "recommendation_score": analytics["recommendation_score"],
            "target_users": self._target_users(product),
            "source_summary": analytics["source_summary"],
            "user_quotes": self._collect_quotes(reviews),
            "analytics": analytics,
        }


analysis_service = AnalysisService()
