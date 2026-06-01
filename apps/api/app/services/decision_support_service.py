from app.repositories.product_repository import product_repository


class DecisionSupportService:
    def get_recommendation_score(self, product: dict, review_summary: dict, issues: list[dict]) -> int:
        score = 72
        release_year = product["release_year"]
        slug = product["slug"]

        score += max(0, release_year - 2021) * 4
        score += min(len(review_summary["top_positive_aspects"]), 3) * 3
        score -= min(len(review_summary["top_negative_aspects"]), 3) * 2

        if "pro" in slug:
            score += 5
        if "mini" in slug:
            score -= 6
        if "plus" in slug or "max" in slug:
            score += 2

        if "promotion" in product["display_type"].lower():
            score += 3

        if issues:
            score -= round(sum(issue["confidence_score"] for issue in issues[:2]) * 6)

        return max(45, min(96, score))

    def _get_recommendation_verdict(self, product: dict) -> str:
        slug = product["slug"]
        release_year = product["release_year"]

        if release_year >= 2024 or ("pro" in slug and release_year >= 2023):
            return "strong_buy"

        if "mini" in slug or release_year <= 2020:
            return "niche_pick"

        return "buy_with_caveats"

    def _build_best_for(self, product: dict, review_summary: dict) -> list[str]:
        slug = product["slug"]
        positive_aspects = review_summary["top_positive_aspects"]

        if "mini" in slug:
            return [
                "Kompakt telefon sevenler",
                "Tek elle kullanim onceligi olanlar",
                positive_aspects[0],
            ]

        if "pro" in slug:
            return [
                "Mobil foto ve video meraklilari",
                "Premium malzeme ve ekran isteyenler",
                positive_aspects[0],
            ]

        if "plus" in slug or "max" in slug or "6.7" in product["display_size"] or "6.9" in product["display_size"]:
            return [
                "Buyuk ekran sevenler",
                "Uzun pil omru onceligi olanlar",
                "Medya ve video tuketimi agir kullananlar",
            ]

        return [
            "Gunluk kullanimda dengeli cihaz arayanlar",
            "Ogrenciler ve genel kullanicilar",
            positive_aspects[0],
        ]

    def _build_not_ideal_for(self, product: dict, review_summary: dict) -> list[str]:
        slug = product["slug"]
        items: list[str] = []

        if "mini" in slug:
            items.append("Yogun ekran suresiyle tum gun pil isteyenler")

        if "plus" in slug or "max" in slug or "6.7" in product["display_size"] or "6.9" in product["display_size"]:
            items.append("Tek elle kullanim ve maksimum tasinabilirlik isteyenler")

        if "promotion" not in product["display_type"].lower():
            items.append("120 Hz ekran bekleyenler")

        if product["release_year"] <= 2021:
            items.append("En yeni nesil kamera ve uzun yazilim omru isteyenler")

        items.append(review_summary["top_negative_aspects"][0])
        return items[:3]

    def build_decision_support(self, product: dict) -> dict:
        review_summary = product["analysis"]["review_summary"]
        issues = product["analysis"]["common_issues"]
        verdict = self._get_recommendation_verdict(product)
        top_positive = review_summary["top_positive_aspects"][0]
        top_negative = review_summary["top_negative_aspects"][0]
        issue_title = issues[0]["title"] if issues else "belirgin issue baskisi yok"

        quick_verdict = (
            f"{product['name']}, 2026 perspektifinde {top_positive.lower()} sayesinde hala anlamli bir aday. "
            f"Ancak {top_negative.lower()} ve {issue_title.lower()} gibi sinyaller satin alma kararinda dikkatle tartilmali."
        )

        return {
            "recommendation_verdict": verdict,
            "quick_verdict": quick_verdict,
            "best_for": self._build_best_for(product, review_summary),
            "not_ideal_for": self._build_not_ideal_for(product, review_summary),
        }

    def get_previous_model(self, product: dict) -> dict | None:
        slug = product["slug"]
        parts = slug.split("-")

        if len(parts) < 2 or not parts[1].isdigit():
            return None

        previous_generation = int(parts[1]) - 1
        if previous_generation < 11:
            return None

        suffix = ""
        if len(parts) > 2:
            suffix = "-" + "-".join(parts[2:])

        candidate_slugs = [f"iphone-{previous_generation}{suffix}"]
        if suffix:
            candidate_slugs.append(f"iphone-{previous_generation}")

        for candidate_slug in candidate_slugs:
            if candidate_slug == slug:
                continue

            for candidate in product_repository.list_products():
                if candidate["slug"] == candidate_slug:
                    return candidate

        return None


decision_support_service = DecisionSupportService()
