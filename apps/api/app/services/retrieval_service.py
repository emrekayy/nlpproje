from functools import cached_property

import numpy as np
import truststore
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.repositories.review_repository import review_repository
from app.services.catalog_service import catalog_service

truststore.inject_into_ssl()


class SemanticSearchUnavailableError(Exception):
    pass


class RetrievalService:
    # TODO: Move semantic chunk embeddings from in-memory numpy arrays to a vector database.
    # TODO: Replace full corpus re-embedding with incremental chunk upserts when ingestion becomes dynamic.
    _query_priority_profiles = {
        "daily-use": {
            "boost": ["babam icin", "annem icin", "gunluk kullanim", "whatsapp", "spotify", "universite"],
            "targets": {"general", "battery", "software", "durability"},
            "chunk_types": {"review", "real_review", "community_opinion", "user_evidence", "product_description"},
            "score": 0.18,
        },
        "gaming": {
            "boost": ["pubg", "fps", "genshin"],
            "targets": {"performance", "heat"},
            "chunk_types": {"review", "real_review", "risk_signal", "strength", "product_description"},
            "score": 0.2,
        },
        "camera": {
            "boost": ["tiktok", "instagram", "story", "fotograf", "foto"],
            "targets": {"camera"},
            "chunk_types": {"review", "real_review", "strength", "product_description", "user_evidence"},
            "score": 0.2,
        },
    }
    _query_suppressions = {
        "camera": {
            "phrases": ["kamera onemli degil", "kamera bos", "kamera gereksiz", "kamera bos ama"],
            "targets": {"camera"},
            "chunk_types": {"review", "real_review", "strength", "product_description", "user_evidence"},
            "score": 0.65,
        },
        "gaming": {
            "phrases": ["oyun onemli degil", "oyun oynamiyorum", "gaming onemli degil"],
            "targets": {"performance", "heat"},
            "chunk_types": {"review", "real_review", "risk_signal", "strength", "product_description"},
            "score": 0.65,
        },
    }
    _intent_profiles = {
        "heating": {
            "boost": [
                "heating",
                "thermal",
                "temperature",
                "overheat",
                "hot",
                "gaming",
                "performance load",
            ],
            "penalty": ["battery health", "camera", "display", "software update"],
        },
        "battery": {
            "boost": ["battery", "screen time", "battery life", "charging", "usage time"],
            "penalty": ["camera", "thermal", "gaming"],
        },
        "camera": {
            "boost": ["camera", "photo", "night mode", "video", "zoom"],
            "penalty": ["battery", "thermal"],
        },
        "gaming": {
            "boost": ["gaming", "fps", "performance", "pubg", "genshin"],
            "penalty": ["camera", "battery aging"],
        },
        "negative": {
            "boost": ["risk", "issue", "problem", "weakness", "complaint"],
            "penalty": ["camera quality", "battery life"],
        },
        "recommendation": {
            "boost": ["recommendation", "worth", "value", "buy", "overall"],
            "penalty": [],
        },
        "daily-use": {
            "boost": ["daily use", "whatsapp", "spotify", "reliability", "simplicity", "battery", "overall"],
            "penalty": ["camera", "gaming", "thermal", "overheat"],
        },
        "comparison": {
            "boost": ["compare", "difference", "versus", "overall", "camera", "battery", "performance"],
            "penalty": [],
        },
        "general": {"boost": ["review", "opinion", "overall", "experience"], "penalty": []},
    }
    _aspect_hints = {
        "heat": ["heat", "heating", "thermal", "hot", "isinma", "sicak", "termal"],
        "battery": ["battery", "endurance", "reliable", "degradation", "pil", "sarj", "dayaniklilik"],
        "camera": ["camera", "photo", "video", "zoom", "kamera", "fotograf", "cekim"],
        "performance": ["performance", "gaming", "speed", "chip", "performans", "oyun", "hiz"],
        "display": ["display", "screen", "oled", "brightness", "ekran", "panel"],
        "software": ["software", "ios", "update", "bug", "yazilim", "guncelleme"],
        "durability": ["durability", "weight", "build", "ergonomi", "dayaniklilik", "agirlik"],
        "price": ["price", "value", "cost", "fiyat", "deger"],
        "storage": ["storage", "capacity", "space", "depolama", "kapasite"],
        "general": ["overall", "general", "yorum", "deneyim", "topluluk"],
    }

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

    def describe_capability(self) -> str:
        return "Semantic retrieval pipeline backed by local sentence-transformers embeddings."

    @cached_property
    def _products(self) -> list[dict]:
        return catalog_service.list_products()

    @cached_property
    def _products_by_name(self) -> dict[str, dict]:
        return {product["name"]: product for product in self._products}

    @cached_property
    def _products_by_slug(self) -> dict[str, dict]:
        return {product["slug"]: product for product in self._products}

    def _normalize_text(self, text: str) -> str:
        return text.lower().translate(self._char_map)

    def _aspect_tokens(self, aspect: str | None, text: str) -> list[str]:
        normalized_text = self._normalize_text(text)
        tokens: set[str] = set()

        if aspect and aspect in self._aspect_hints:
            tokens.update(self._aspect_hints[aspect])

        for aspect_name, hints in self._aspect_hints.items():
            if any(hint in normalized_text for hint in hints):
                tokens.add(aspect_name)
                tokens.update(hints)

        return sorted(tokens)

    def _build_embedding_text(
        self,
        *,
        model: str,
        chunk_type: str,
        chunk_label: str,
        text: str,
        aspect: str | None = None,
        sentiment: str | None = None,
    ) -> str:
        normalized_text = self._normalize_text(text)
        hint_tokens = self._aspect_tokens(aspect, text)
        fields = [
            model,
            self._normalize_text(model),
            chunk_type,
            chunk_label,
            aspect or "general",
            sentiment or "neutral",
            normalized_text,
            " ".join(hint_tokens),
        ]
        return " | ".join(field for field in fields if field)

    def _product_chunks(self, product: dict) -> list[dict]:
        review_summary = product["analysis"]["review_summary"]
        chunks: list[dict] = []

        def add_chunk(
            *,
            chunk_id: str,
            chunk_type: str,
            chunk_label: str,
            text: str,
            source: str,
            aspect: str | None = None,
            sentiment: str | None = None,
            rating: int | None = None,
            timestamp: str | None = None,
        ) -> None:
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "slug": product["slug"],
                    "model": product["name"],
                    "chunk_type": chunk_type,
                    "chunk_label": chunk_label,
                    "text": text,
                    "source": source,
                    "aspect": aspect or "general",
                    "sentiment": sentiment or "neutral",
                    "rating": rating,
                    "timestamp": timestamp,
                    "embedding_text": self._build_embedding_text(
                        model=product["name"],
                        chunk_type=chunk_type,
                        chunk_label=chunk_label,
                        text=text,
                        aspect=aspect,
                        sentiment=sentiment,
                    ),
                }
            )

        add_chunk(
            chunk_id=f"{product['slug']}-description-short",
            chunk_type="product_description",
            chunk_label="Product description",
            text=product["short_description"],
            source="Product summary",
            aspect="general",
            sentiment="neutral",
        )
        add_chunk(
            chunk_id=f"{product['slug']}-description-battery",
            chunk_type="product_description",
            chunk_label="Battery description",
            text=product["battery_summary"],
            source="Battery summary",
            aspect="battery",
            sentiment="neutral",
        )
        add_chunk(
            chunk_id=f"{product['slug']}-description-camera",
            chunk_type="product_description",
            chunk_label="Camera description",
            text=product["camera_summary"],
            source="Camera summary",
            aspect="camera",
            sentiment="neutral",
        )

        for index, strength in enumerate(product["strengths"]):
            add_chunk(
                chunk_id=f"{product['slug']}-strength-{index}",
                chunk_type="strength",
                chunk_label="Strength",
                text=strength,
                source="Strength synthesis",
                sentiment="positive",
            )

        for index, weakness in enumerate(product["weaknesses"]):
            add_chunk(
                chunk_id=f"{product['slug']}-weakness-{index}",
                chunk_type="weakness",
                chunk_label="Weakness",
                text=weakness,
                source="Weakness synthesis",
                sentiment="negative",
            )

        for index, issue in enumerate(product["analysis"]["common_issues"]):
            add_chunk(
                chunk_id=f"{product['slug']}-risk-{index}",
                chunk_type="risk_signal",
                chunk_label=issue["title"],
                text=f"{issue['title']}. {issue['description']}",
                source="Risk signal",
                aspect="heat" if "isinma" in self._normalize_text(issue["title"]) else "general",
                sentiment="negative",
            )

        for index, snippet in enumerate(review_summary["evidence_snippets"]):
            add_chunk(
                chunk_id=f"{product['slug']}-evidence-{index}",
                chunk_type="user_evidence",
                chunk_label="User evidence",
                text=snippet["text"],
                source=snippet["source"],
                sentiment="neutral",
            )

        add_chunk(
            chunk_id=f"{product['slug']}-community-summary",
            chunk_type="community_opinion",
            chunk_label="Community summary",
            text=review_summary["overall_sentiment_summary"],
            source="Community summary",
            sentiment="neutral",
        )
        add_chunk(
            chunk_id=f"{product['slug']}-community-chat-summary",
            chunk_type="community_opinion",
            chunk_label="Community opinion",
            text=review_summary["chatbot_ready_summary"],
            source="Community opinion",
            sentiment="neutral",
        )

        for index, quote in enumerate(product["user_quotes"]):
            add_chunk(
                chunk_id=f"{product['slug']}-quote-{index}",
                chunk_type="community_opinion",
                chunk_label="Community quote",
                text=quote,
                source="Community quote",
                sentiment="neutral",
            )

        return chunks

    def _review_chunks(self) -> list[dict]:
        chunks: list[dict] = []
        for review in review_repository.list_reviews():
            product = self._products_by_name.get(review["model"])
            source_type = review.get("source_type") or "Mock Community Review"
            source_platform = review.get("source_platform") or review["source"]
            review_title = review.get("review_title")
            chunk_text = (
                f"{review_title}. {review['text']}"
                if review_title and review_title.lower() not in review["text"].lower()
                else review["text"]
            )
            chunks.append(
                {
                    "chunk_id": review["id"],
                    "slug": product["slug"] if product else None,
                    "model": review["model"],
                    "chunk_type": "real_review" if source_type == "Real User Review" else "review",
                    "chunk_label": "Real user review" if source_type == "Real User Review" else "Community review",
                    "text": review["text"],
                    "content": chunk_text,
                    "source": source_platform,
                    "source_type": source_type,
                    "source_platform": source_platform,
                    "aspect": review["aspect"],
                    "sentiment": review["sentiment"],
                    "rating": review["rating"],
                    "timestamp": review["timestamp"],
                    "verified_purchase": review.get("verified_purchase"),
                    "review_title": review_title,
                    "source_url": review.get("source_url"),
                    "metadata": review.get("metadata", {}),
                    "embedding_text": self._build_embedding_text(
                        model=review["model"],
                        chunk_type="real_review" if source_type == "Real User Review" else "review",
                        chunk_label="Real user review" if source_type == "Real User Review" else "Community review",
                        text=chunk_text,
                        aspect=review["aspect"],
                        sentiment=review["sentiment"],
                    ),
                }
            )
        return chunks

    @cached_property
    def _chunks(self) -> list[dict]:
        chunks: list[dict] = []
        for product in self._products:
            chunks.extend(self._product_chunks(product))
        chunks.extend(self._review_chunks())
        return chunks

    @cached_property
    def _model(self) -> SentenceTransformer:
        try:
            return SentenceTransformer(settings.embedding_model_name)
        except Exception as exc:  # pragma: no cover - depends on local model/runtime state
            raise SemanticSearchUnavailableError(
                "Semantic model could not be loaded locally. Download the model or fix network/SSL access "
                f"for '{settings.embedding_model_name}'."
            ) from exc

    @cached_property
    def _embedding_matrix(self) -> np.ndarray:
        texts = [chunk["embedding_text"] for chunk in self._chunks]
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        return self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def _extract_model_hint(self, query: str) -> str | None:
        normalized = self._normalize_text(query.strip())
        for product in self._products:
            if self._normalize_text(product["name"]) in normalized or product["slug"] in normalized:
                return product["slug"]
        return None

    def _score_boost(self, chunk: dict, *, query: str, slug: str | None) -> float:
        boost = 0.0
        normalized_query = self._normalize_text(query)
        query_hints = self._aspect_tokens(None, query)

        if slug is not None and chunk["slug"] == slug:
            boost += 0.12
        elif slug is None:
            hinted_slug = self._extract_model_hint(query)
            if hinted_slug is not None and chunk["slug"] == hinted_slug:
                boost += 0.08

        chunk_aspect = chunk.get("aspect", "general")
        if chunk_aspect in query_hints:
            boost += 0.08

        if chunk["chunk_type"] == "risk_signal" and any(
            token in normalized_query for token in ["isinma", "heat", "thermal", "sicak"]
        ):
            boost += 0.05
        if chunk["chunk_type"] == "product_description" and any(
            token in normalized_query for token in ["kamera", "camera", "pil", "battery"]
        ):
            boost += 0.03

        if chunk.get("source_type") == "Real User Review":
            boost += 0.12
        elif chunk["chunk_type"] == "product_description":
            boost += 0.06
        elif chunk["chunk_type"] in {"community_opinion", "user_evidence"}:
            boost += 0.03
        elif chunk["chunk_type"] == "review":
            boost += 0.02

        return round(min(boost, 0.35), 2)

    def _chunk_profile_text(self, chunk: dict) -> str:
        aspect_aliases = {
            "heat": "heating thermal temperature hot overheat performance load",
            "battery": "battery charging battery life screen time usage time battery health",
            "camera": "camera photo video zoom night mode lens camera quality",
            "performance": "gaming fps performance pubg genshin lag kasma performance load",
            "display": "display screen panel brightness",
            "software": "software update ios bug software update",
            "general": "overall product summary community opinion review experience",
        }
        parts = [
            chunk.get("content", chunk.get("text", "")),
            chunk.get("source", ""),
            chunk.get("source_type", ""),
            chunk.get("source_platform", ""),
            chunk.get("chunk_label", ""),
            chunk.get("chunk_type", ""),
            chunk.get("aspect", ""),
            aspect_aliases.get(chunk.get("aspect", "general"), ""),
        ]
        return self._normalize_text(" ".join(parts))

    def _profile_term_score(self, text: str, terms: list[str], *, weight: float) -> tuple[float, list[str]]:
        matched_terms: list[str] = []
        for term in terms:
            if self._normalize_text(term) in text:
                matched_terms.append(term)
        score = min(len(matched_terms) * weight, 1.0)
        return round(score, 2), matched_terms

    def _query_profile_adjustment(
        self, *, query: str, chunk: dict
    ) -> tuple[float, float, list[str], list[str]]:
        normalized_query = self._normalize_text(query)
        chunk_aspect = chunk.get("aspect", "general")
        chunk_type = chunk.get("chunk_type", "community_opinion")

        boost = 0.0
        penalty = 0.0
        boost_hits: list[str] = []
        penalty_hits: list[str] = []

        for profile in self._query_priority_profiles.values():
            matched = [term for term in profile["boost"] if self._normalize_text(term) in normalized_query]
            if not matched:
                continue
            if chunk_aspect in profile["targets"] or chunk_type in profile["chunk_types"]:
                boost += profile["score"]
                boost_hits.extend(matched)

        for profile in self._query_suppressions.values():
            matched = [term for term in profile["phrases"] if self._normalize_text(term) in normalized_query]
            if not matched:
                continue
            if chunk_aspect in profile["targets"] or chunk_type in profile["chunk_types"]:
                penalty += profile["score"]
                penalty_hits.extend(matched)

        return (
            round(min(boost, 1.0), 2),
            round(min(penalty, 1.0), 2),
            boost_hits,
            penalty_hits,
        )

    def _is_comparison_query(self, query: str) -> bool:
        normalized = self._normalize_text(query)
        return any(token in normalized for token in ["compare", "karsilastir", "onceki", "previous"])

    def retrieve_chunks(
        self,
        query: str,
        *,
        slug: str | None = None,
        allowed_slugs: list[str] | None = None,
        category: str = "general",
        limit: int = 8,
    ) -> list[dict]:
        normalized_query = query.strip()
        if not normalized_query or self._embedding_matrix.size == 0:
            return []

        resolved_allowed_slugs = allowed_slugs or ([slug] if slug is not None else None)
        restrict_to_slug = resolved_allowed_slugs is not None and category != "comparison"

        query_vector = self._model.encode(
            self._build_embedding_text(
                model=self._products_by_slug[slug]["name"] if slug and slug in self._products_by_slug else "global",
                chunk_type="query",
                chunk_label="user question",
                text=normalized_query,
            ),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        similarities = np.matmul(self._embedding_matrix, query_vector)

        ranked_items: list[dict] = []
        for index, chunk in enumerate(self._chunks):
            if restrict_to_slug and chunk["slug"] not in resolved_allowed_slugs:
                continue

            cosine_similarity = float(similarities[index])
            profile = self._intent_profiles.get(category, self._intent_profiles["general"])
            profile_text = self._chunk_profile_text(chunk)
            boost_score, matched_boost_terms = self._profile_term_score(
                profile_text, profile["boost"], weight=0.2
            )
            penalty_score, matched_penalty_terms = self._profile_term_score(
                profile_text, profile["penalty"], weight=0.3
            )
            source_priority_boost = self._score_boost(chunk, query=normalized_query, slug=slug)
            query_boost, query_penalty, query_boost_hits, query_penalty_hits = self._query_profile_adjustment(
                query=normalized_query,
                chunk=chunk,
            )
            boost_score = round(min(boost_score + query_boost + source_priority_boost, 1.0), 2)
            penalty_score = round(min(penalty_score + query_penalty, 1.0), 2)
            matched_boost_terms = list(dict.fromkeys([*matched_boost_terms, *query_boost_hits]))
            matched_penalty_terms = list(dict.fromkeys([*matched_penalty_terms, *query_penalty_hits]))

            ranking_score = (
                cosine_similarity * 0.7
                + boost_score * 0.3
                - penalty_score * 0.2
            )
            if (
                resolved_allowed_slugs is not None
                and not restrict_to_slug
                and chunk["slug"] not in resolved_allowed_slugs
            ):
                ranking_score -= 0.08

            ranked_items.append(
                {
                    **chunk,
                    "similarity_score": round(cosine_similarity, 4),
                    "boost_score": boost_score,
                    "penalty_score": penalty_score,
                    "matched_boost_terms": matched_boost_terms,
                    "matched_penalty_terms": matched_penalty_terms,
                    "intent_category": category.upper(),
                    "final_score": round(ranking_score, 4),
                    "ranking_score": round(ranking_score, 4),
                }
            )

        ranked_items.sort(key=lambda item: item["ranking_score"], reverse=True)
        return ranked_items[:limit]

    def semantic_search(self, query: str, limit: int = 8) -> dict:
        items = self.retrieve_chunks(query, limit=limit)
        return {
            "query": query.strip(),
            "total": len(items),
            "items": [
                {
                    "review_id": item["chunk_id"],
                    "slug": item["slug"],
                    "model": item["model"],
                    "rating": item["rating"],
                    "text": item["text"],
                    "aspect": item["aspect"],
                    "sentiment": item["sentiment"],
                    "source": item["source"],
                    "timestamp": item["timestamp"],
                    "similarity_score": item["similarity_score"],
                    "chunk_type": item["chunk_type"],
                    "chunk_label": item["chunk_label"],
                }
                for item in items
            ],
        }


retrieval_service = RetrievalService()
