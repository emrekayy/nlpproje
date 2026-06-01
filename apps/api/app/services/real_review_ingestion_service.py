import csv
import json
import re
from collections import Counter
from datetime import datetime
from functools import cached_property
from pathlib import Path

from app.core.config import settings
from app.repositories.product_repository import product_repository


class RealReviewIngestionService:
    _encoding_fallbacks = ["utf-8-sig", "utf-8", "latin1", "cp1252"]
    _char_map = str.maketrans(
        {
            "ç": "c",
            "ğ": "g",
            "ı": "i",
            "ö": "o",
            "ş": "s",
            "ü": "u",
            "Ç": "C",
            "Ğ": "G",
            "İ": "I",
            "Ö": "O",
            "Ş": "S",
            "Ü": "U",
        }
    )
    _column_aliases = {
        "review_text": ["review_text", "reviewDescription", "Review", "Comment", "Reviews"],
        "rating": ["review_rating", "ratingScore", "Rating", "Ratings"],
        "title": ["review_title", "reviewTitle"],
        "date": ["reviewed_at", "date", "Date"],
        "country": ["review_country", "country"],
        "model": ["product", "model", "variant"],
        "verified_purchase": ["isVerified"],
        "source_url": ["reviewUrl", "url"],
        "helpful_count": ["helpful_count"],
    }
    _platform_by_filename = {
        "datadna_cleaned.csv": "Apple Review Dataset",
        "iphone.csv": "Amazon Reviews",
        "apple_iphone_11_reviews.csv": "Apple Review Dataset",
        "apple-iphone-16-128-gb_reviews (1).csv": "Amazon Reviews",
        "apple_iphone_se.csv": "Flipkart Reviews",
        "iphonereview.csv": "Legacy Review Dataset",
    }
    _model_fallback_by_filename = {
        "iphone.csv": "iPhone 13",
        "apple_iphone_11_reviews.csv": "iPhone 11",
        "apple-iphone-16-128-gb_reviews (1).csv": "iPhone 16",
        "apple_iphone_se.csv": "iPhone SE",
    }
    _aspect_keywords = {
        "camera": [
            "camera",
            "photo",
            "video",
            "zoom",
            "lens",
            "selfie",
            "story",
            "instagram",
            "tiktok",
            "reels",
            "night",
            "low light",
            "portrait",
        ],
        "battery": ["battery", "screen time", "charge", "charging", "backup", "sot"],
        "heat": ["heat", "heating", "thermal", "overheat", "hot", "warm"],
        "performance": ["performance", "gaming", "game", "pubg", "genshin", "fps", "lag", "smooth", "speed"],
        "display": ["display", "screen", "brightness", "oled", "panel", "color"],
        "software": ["software", "ios", "update", "bug", "app", "interface", "ui"],
        "durability": ["build", "weight", "durable", "slippery", "hand", "compact"],
        "price": ["price", "value", "cost", "expensive"],
        "storage": ["storage", "gb", "capacity", "space"],
    }
    _positive_keywords = {
        "good",
        "great",
        "excellent",
        "smooth",
        "fast",
        "strong",
        "reliable",
        "amazing",
        "love",
        "awesome",
        "impressed",
        "happy",
    }
    _negative_keywords = {
        "bad",
        "poor",
        "worse",
        "worst",
        "terrible",
        "issue",
        "problem",
        "defective",
        "disappointed",
        "lag",
        "drain",
        "hot",
        "overheat",
        "awkward",
        "careless",
    }

    def _normalize_text(self, value: str | None) -> str:
        text = str(value or "")
        text = (
            text.replace("\ufeff", " ")
            .replace("\u200b", " ")
            .replace("\xa0", " ")
            .replace("Â", " ")
            .replace("�", " ")
        )
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _normalize_key(self, value: str | None) -> str:
        lowered = self._normalize_text(value).lower().translate(self._char_map)
        return re.sub(r"[^a-z0-9]+", "", lowered)

    @cached_property
    def _known_model_aliases(self) -> dict[str, str]:
        aliases: dict[str, str] = {}
        extra_models = ["iPhone SE"]
        for product in product_repository.list_products():
            canonical = product["name"]
            raw_aliases = {
                canonical,
                canonical.lower(),
                canonical.replace("iPhone", "Apple iPhone"),
                canonical.replace(" ", ""),
                product["slug"],
                product["slug"].replace("-", ""),
            }
            for alias in raw_aliases:
                aliases[self._normalize_key(alias)] = canonical
        for model in extra_models:
            aliases[self._normalize_key(model)] = model
            aliases[self._normalize_key(model.replace("iPhone", "Apple iPhone"))] = model
            aliases[self._normalize_key(model.replace(" ", ""))] = model
        return aliases

    def _extract_value(self, row: dict, aliases: list[str]) -> str | None:
        for alias in aliases:
            if alias in row and self._normalize_text(row[alias]):
                return self._normalize_text(row[alias])
        return None

    def _parse_rating(self, value: str | None) -> float | None:
        raw = self._normalize_text(value)
        if not raw:
            return None
        match = re.search(r"(\d+(?:\.\d+)?)", raw)
        if not match:
            return None
        rating = float(match.group(1))
        if rating > 5:
            rating = 5.0
        if rating < 1:
            return None
        return round(rating, 1)

    def _parse_bool(self, value: str | None) -> bool | None:
        raw = self._normalize_text(value).lower()
        if not raw:
            return None
        if raw in {"true", "yes", "y", "verified"}:
            return True
        if raw in {"false", "no", "n", "unverified"}:
            return False
        return None

    def _parse_date(self, value: str | None) -> str | None:
        raw = self._normalize_text(value)
        if not raw:
            return None
        formats = (
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d-%b-%y",
            "%d %b %Y",
            "%d %B %Y",
            "%Y/%m/%d",
            "%d.%m.%Y",
            "%Y-%m-%d %H:%M:%S",
        )
        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt).strftime("%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                continue
        if "Reviewed in" in raw:
            tail = raw.split(" on ", 1)[-1]
            return self._parse_date(tail)
        if "T" in raw:
            return raw
        return raw

    def _infer_model_from_text(self, value: str) -> str | None:
        normalized = self._normalize_key(value)
        # Sort by descending alias length so "iphone11pro" beats "iphone11"
        for alias, canonical in sorted(
            self._known_model_aliases.items(), key=lambda kv: -len(kv[0])
        ):
            if alias and alias in normalized:
                return canonical
        return None

    def _normalize_model_name(self, raw_model: str | None, csv_path: Path, row: dict) -> str | None:
        direct_candidates = [
            self._normalize_text(raw_model),
            self._extract_value(row, self._column_aliases["model"]),
            self._extract_value(row, ["product"]),
            self._extract_value(row, ["variant"]),
        ]
        for candidate in direct_candidates:
            if not candidate:
                continue
            inferred = self._infer_model_from_text(candidate)
            if inferred:
                return inferred

        filename_key = csv_path.name.lower()
        if filename_key in self._model_fallback_by_filename:
            return self._model_fallback_by_filename[filename_key]

        combined = " ".join(self._normalize_text(value) for value in row.values())
        return self._infer_model_from_text(combined)

    def _infer_aspect(self, content: str) -> str | None:
        normalized = self._normalize_text(content).lower().translate(self._char_map)
        scored = {
            aspect: sum(1 for keyword in keywords if keyword in normalized)
            for aspect, keywords in self._aspect_keywords.items()
        }
        aspect, score = max(scored.items(), key=lambda item: item[1])
        return aspect if score > 0 else "general"

    def _infer_sentiment(self, content: str, rating: float | None) -> str | None:
        normalized = self._normalize_text(content).lower().translate(self._char_map)
        positive_hits = sum(1 for token in self._positive_keywords if token in normalized)
        negative_hits = sum(1 for token in self._negative_keywords if token in normalized)
        if rating is not None:
            if rating >= 4 and positive_hits >= negative_hits:
                return "positive"
            if rating <= 2 or negative_hits > positive_hits:
                return "negative"
            return "neutral"
        if positive_hits > negative_hits:
            return "positive"
        if negative_hits > positive_hits:
            return "negative"
        return None

    def _read_csv_rows(self, csv_path: Path) -> tuple[list[dict], str]:
        for encoding in self._encoding_fallbacks:
            try:
                with csv_path.open("r", encoding=encoding, newline="") as csv_file:
                    reader = csv.DictReader(csv_file)
                    if reader.fieldnames is None:
                        continue
                    rows = [{(key or "").strip(): value for key, value in row.items()} for row in reader]
                    return rows, encoding
            except UnicodeDecodeError:
                continue
        return [], "unknown"

    def _platform_label(self, csv_path: Path) -> str:
        return self._platform_by_filename.get(csv_path.name.lower(), "Real Review Dataset")

    def _review_id(self, csv_path: Path, row_index: int, explicit_id: str | None) -> str:
        normalized = self._normalize_text(explicit_id)
        if normalized:
            return normalized
        stem = re.sub(r"[^a-z0-9]+", "-", csv_path.stem.lower()).strip("-")
        return f"{stem}-{row_index}"

    def _write_processed_artifact(self, reviews: list[dict]) -> None:
        settings.processed_reviews_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "total": len(reviews),
            "reviews": reviews,
        }
        settings.processed_real_reviews_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _ingest_all_files(self) -> list[dict]:
        reviews: list[dict] = []
        seen_texts: set[str] = set()

        if not settings.raw_reviews_dir.exists():
            return reviews

        for csv_path in sorted(settings.raw_reviews_dir.glob("*.csv")):
            valid_count = 0
            skipped_count = 0
            detected_models: set[str] = set()
            rows, encoding = self._read_csv_rows(csv_path)
            if not rows:
                print(f"[real-review-ingestion] file={csv_path.name} skipped (unreadable or empty)")
                continue
            platform = self._platform_label(csv_path)

            for row_index, row in enumerate(rows, start=1):
                review_text = self._extract_value(row, self._column_aliases["review_text"])
                review_title = self._extract_value(row, self._column_aliases["title"])
                review_text = self._normalize_text(review_text)
                review_title = self._normalize_text(review_title)
                if not review_text:
                    skipped_count += 1
                    continue

                normalized_dedupe = self._normalize_key(review_text)
                if not normalized_dedupe or normalized_dedupe in seen_texts:
                    skipped_count += 1
                    continue

                model_name = self._normalize_model_name(
                    self._extract_value(row, self._column_aliases["model"]), csv_path, row
                )
                if model_name is None:
                    skipped_count += 1
                    continue

                rating = self._parse_rating(self._extract_value(row, self._column_aliases["rating"]))
                country = self._extract_value(row, self._column_aliases["country"])
                verified_purchase = self._parse_bool(
                    self._extract_value(row, self._column_aliases["verified_purchase"])
                )
                source_url = self._extract_value(row, self._column_aliases["source_url"])
                date = self._parse_date(self._extract_value(row, self._column_aliases["date"]))
                helpful_count = self._extract_value(row, self._column_aliases["helpful_count"])
                content = f"{review_title}. {review_text}" if review_title and review_title.lower() not in review_text.lower() else review_text
                aspect = self._infer_aspect(content)
                sentiment = self._infer_sentiment(content, rating)

                review = {
                    "id": self._review_id(csv_path, row_index, row.get("id")),
                    "model": model_name,
                    "source": platform,
                    "rating": rating,
                    "review_text": review_text,
                    "review_title": review_title or None,
                    "date": date,
                    "country": country or None,
                    "verified_purchase": verified_purchase,
                    "sentiment": sentiment,
                    "aspect": aspect,
                    "source_url": source_url or None,
                    "metadata": {
                        "file_name": csv_path.name,
                        "encoding": encoding,
                        "helpful_count": helpful_count,
                    },
                }
                reviews.append(review)
                seen_texts.add(normalized_dedupe)
                valid_count += 1
                detected_models.add(model_name)

            print(
                f"[real-review-ingestion] file={csv_path.name} valid_reviews={valid_count} "
                f"skipped_rows={skipped_count} detected_models={sorted(detected_models)}"
            )

        reviews.sort(key=lambda item: (item["model"], item.get("date") or "", item["id"]))
        self._write_processed_artifact(reviews)
        return reviews

    @cached_property
    def _reviews(self) -> list[dict]:
        return self._ingest_all_files()

    def list_reviews(self) -> list[dict]:
        return self._reviews

    def resolve_model_identifier(self, identifier: str) -> str | None:
        normalized = self._normalize_text(identifier)
        if not normalized:
            return None
        inferred = self._infer_model_from_text(normalized)
        if inferred is not None:
            return inferred
        for review in self._reviews:
            if self._normalize_text(review["model"]).lower() == normalized.lower():
                return review["model"]
        return None

    def get_reviews_by_model_name(self, model_name: str) -> list[dict]:
        return [review for review in self._reviews if review["model"] == model_name]

    def get_stats_by_model_name(self, model_name: str) -> dict:
        reviews = self.get_reviews_by_model_name(model_name)
        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0.0,
                "positive_count": 0,
                "neutral_count": 0,
                "negative_count": 0,
                "source_distribution": [],
                "rating_distribution": [],
                "verified_review_count": 0,
                "top_aspects": [],
            }

        rating_values = [review["rating"] for review in reviews if review["rating"] is not None]
        sentiments = Counter((review["sentiment"] or "unknown") for review in reviews)
        sources = Counter(review["source"] for review in reviews)
        rating_distribution = Counter(str(review["rating"]) for review in reviews if review["rating"] is not None)
        aspects = Counter((review["aspect"] or "general") for review in reviews)
        verified_count = sum(1 for review in reviews if review["verified_purchase"] is True)

        return {
            "total_reviews": len(reviews),
            "average_rating": round(sum(rating_values) / len(rating_values), 2) if rating_values else 0.0,
            "positive_count": sentiments.get("positive", 0),
            "neutral_count": sentiments.get("neutral", 0),
            "negative_count": sentiments.get("negative", 0),
            "source_distribution": [{"label": label, "count": count} for label, count in sources.most_common()],
            "rating_distribution": [{"label": label, "count": count} for label, count in rating_distribution.most_common()],
            "verified_review_count": verified_count,
            "top_aspects": [{"aspect": label, "count": count} for label, count in aspects.most_common(5)],
        }


real_review_ingestion_service = RealReviewIngestionService()
