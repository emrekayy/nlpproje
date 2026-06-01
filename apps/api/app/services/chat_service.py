import re

from app.services.catalog_service import catalog_service
from app.services.decision_support_service import decision_support_service
from app.services.retrieval_service import retrieval_service


class ChatService:
    _purchase_question_phrases = [
        "alinir mi",
        "alinir",
        "mantikli mi",
        "satin almali miyim",
        "satin almam gerekir mi",
        "onerir misin",
        "almaya deger mi",
        "deger mi",
        "buy",
        "worth",
        "recommend",
    ]
    _product_keywords = [
        "iphone",
        "telefon",
        "phone",
        "model",
        "cihaz",
        "kamera",
        "camera",
        "story",
        "instagram",
        "tiktok",
        "reels",
        "sosyal medya",
        "selfie",
        "gece cekimi",
        "low light",
        "pil",
        "battery",
        "oyun",
        "gaming",
        "isinma",
        "sicak",
        "sicaklik",
        "elde yanma",
        "elimi yakmasin",
        "heat",
        "termal",
        "overheating",
        "performans",
        "performance",
        "fiyat",
        "deger",
        "sikayet",
        "sorun",
        "review",
        "yorum",
        "alinir",
        "onerir",
        "recommend",
        "worth",
        "compare",
        "karsilastir",
        "onceki",
        "previous",
    ]
    _out_of_scope_keywords = [
        "hava",
        "weather",
        "yagmur",
        "rain",
        "siir",
        "poem",
        "tarif",
        "recipe",
        "futbol",
        "football",
        "borsa",
        "stock",
        "siyaset",
        "politics",
        "film",
        "movie",
        "muzik",
        "song",
        "burc",
        "horoscope",
        "kod yaz",
        "write code",
    ]
    _intent_expansions = {
        "battery": "battery endurance iphone",
        "camera": "camera quality iphone",
        "gaming": "gaming performance thermal heating iphone",
        "heating": "heating thermal issue iphone",
        "recommendation": "purchase recommendation iphone",
        "daily-use": "daily use reliability simplicity iphone",
        "long-term": "long term longevity durability battery health iphone",
        "negative": "negative weakness risk issue iphone",
        "comparison": "product comparison iphone",
        "general": "iphone product review community opinion",
    }
    _semantic_phrase_groups = {
        "battery": [
            "bir gun rahat cikar",
            "aksama kadar gidiyor",
            "sarji yetiyor",
            "gunluk kullanimda pili nasil",
            "gunluk kullanimda pil nasil",
            "tek sarjla ne kadar gidiyor",
            "ekran suresi nasil",
            "gun boyu gider mi",
            "aksami cikariyor mu",
            "sarji cabuk bitiyor mu",
        ],
        "camera": [
            "gece cekimleri nasil",
            "karanlikta fotograf iyi mi",
            "instagram icin iyi mi",
            "tiktok icin iyi mi",
            "tik tok icin iyi mi",
            "reels icin iyi mi",
            "story kalitesi nasil",
            "sosyal medya icin iyi mi",
            "gece cekiminde iyi mi",
            "gece story atarken uzmesin",
            "low light iyi mi",
            "selfie nasil",
            "kamerasi iyi mi",
            "video kalitesi nasil",
            "low light performansi nasil",
        ],
        "heating": [
            "pubg de elde yaniyor mu",
            "pubg elde yaniyor mu",
            "uzun kullanimda isiniyor mu",
            "oyun oynarken ates gibi oluyor mu",
            "oyunda cok isinıyor mu",
            "uzun sure kullanimda isiniyor mu",
            "telefon sicakliyor mu",
            "elde ates gibi oluyor mu",
            "elde yaniyor mu",
            "elde yanma",
            "elimi yakmasin",
            "sicaklik artiyor mu",
        ],
        "gaming": [
            "oyunda kasiyor mu",
            "pubg performansi nasil",
            "genshin performansi nasil",
            "fps dusuyor mu",
            "oyunda lag oluyor mu",
            "uzun oyunda performans dusuyor mu",
            "oyun performansi nasil",
        ],
        "recommendation": [
            "alinir mi",
            "mantikli mi",
            "deger mi",
            "almaya deger mi",
            "2026 da alinirmi",
            "hala alinirmi",
        ],
        "long-term": [
            "uzun kullanimda nasil",
            "uzun vadede nasil",
            "2 yil sonra nasil",
            "omurlu mu",
            "uzun donemde nasil",
            "dayanir mi",
        ],
        "daily-use": [
            "babam icin",
            "annem icin",
            "gunluk kullanim",
            "gundelik kullanim",
            "sadece gunluk kullanim",
            "kolay kullanim",
            "whatsapp ve arama",
        ],
        "comparison": [
            "arasinda ne fark var",
            "hangisi daha iyi",
            "karsilastir",
            "vs",
            "farki ne",
            "onceki modele gore",
        ],
    }

    def _normalize_text(self, text: str) -> str:
        normalized = (
            text.lower()
            .replace("ç", "c")
            .replace("ğ", "g")
            .replace("ı", "i")
            .replace("ö", "o")
            .replace("ş", "s")
            .replace("ü", "u")
        )
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _clean_evidence_fragment(self, text: str) -> str:
        cleaned = (text or "").replace("\n", " ").replace("\r", " ").replace("READ MORE", " ")
        cleaned = re.sub(r"https?://\S+", " ", cleaned)
        cleaned = re.sub(r"\bReviewed in [^.]+ on [^.]+\b", " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\b\d[\d,]* people found this helpful\b", " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\b(Anonymous|Amazon Customer|Mr No|UserName)\b", " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\b(India|Germany|UK|USA)\b", " ", cleaned)
        cleaned = re.sub(r"^[A-Za-z][A-Za-z0-9_. -]{0,24},\s*\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}", " ", cleaned)
        cleaned = re.sub(r"\b(Colour|Color|Size):\s*[^.]+", " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"[\"“”]+", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,-:")
        return cleaned

    def _evidence_priority_score(self, sentence: str, *, aspect: str | None) -> int:
        normalized = self._normalize_text(sentence)
        priority_terms = [
            "battery",
            "pil",
            "camera",
            "kamera",
            "performance",
            "performans",
            "heating",
            "isinma",
            "thermal",
            "gaming",
            "oyun",
            "display",
            "ekran",
        ]
        score = sum(1 for term in priority_terms if term in normalized)
        if aspect and aspect != "general":
            score += 2 if aspect in normalized else 0
        word_count = len(sentence.split())
        if 10 <= word_count <= 20:
            score += 2
        elif 8 <= word_count <= 25:
            score += 1
        return score

    def _build_evidence_summary_sentence(self, chunk: dict) -> str:
        aspect_label = {
            "battery": "pil",
            "camera": "kamera",
            "performance": "performans",
            "heat": "isinma",
            "display": "ekran",
            "software": "yazilim",
            "general": "genel kullanim",
        }.get(chunk.get("aspect", "general"), "genel kullanim")
        sentiment = chunk.get("sentiment")
        if sentiment == "positive":
            return f"Kullanici yorumu {aspect_label} tarafinda olumlu bir deneyim anlatiyor."
        if sentiment == "negative":
            return f"Kullanici yorumu {aspect_label} tarafinda daha temkinli bir deneyim aktariyor."
        return f"Kullanici yorumu {aspect_label} tarafinda dengeli bir deneyimden bahsediyor."

    def _quality_evidence_text(self, chunk: dict) -> str:
        raw_text = chunk.get("content") or chunk.get("text") or ""
        cleaned = self._clean_evidence_fragment(raw_text)
        sentences = [
            part.strip(" .,-:")
            for part in re.split(r"(?<=[.!?])\s+|\s{2,}", cleaned)
            if part and part.strip(" .,-:")
        ]

        candidates: list[tuple[int, str]] = []
        for sentence in sentences:
            normalized = self._normalize_text(sentence)
            word_count = len(normalized.split())
            if word_count < 8:
                continue
            if word_count > 25:
                continue
            metadata_noise = [
                "reviewed in",
                "people found this helpful",
                "amazon customer",
                "anonymous",
                "colour",
                "size",
                "username",
                "star crowd",
                "crowd attention",
            ]
            if any(token in normalized for token in metadata_noise):
                continue
            low_quality_signals = [
                "looks like apple",
                "very worst",
                "hanging always",
                "do not purchase",
                "my father s first iphone",
                "battery 3 starcamera",
                "performance 4",
                "5 starcrowd attention",
            ]
            if any(token in normalized for token in low_quality_signals):
                continue
            if re.search(r"\b\d+\s*star\w*", normalized):
                continue
            if re.search(r"[a-z]+-\d", normalized):
                continue
            if re.search(r"\b[a-z]+\d+[a-z]*\b", normalized):
                continue
            if re.search(r"\b(?:camera|battery|performance|display|gaming)-\d+\b", normalized):
                continue
            candidates.append(
                (self._evidence_priority_score(sentence, aspect=chunk.get("aspect")), sentence)
            )

        if candidates:
            best_sentence = max(candidates, key=lambda item: item[0])[1]
            words = best_sentence.split()
            if len(words) > 25:
                best_sentence = " ".join(words[:25]).rstrip(" ,.-") + "."
            return best_sentence

        return self._build_evidence_summary_sentence(chunk)

    def _matches_semantic_group(self, normalized_text: str, category: str) -> bool:
        return any(
            phrase in normalized_text
            for phrase in self._semantic_phrase_groups.get(category, [])
        )

    def _semantic_category(self, normalized_text: str) -> str | None:
        priority = ["comparison", "heating", "gaming", "battery", "camera", "recommendation", "long-term", "daily-use"]
        for category in priority:
            if self._matches_semantic_group(normalized_text, category):
                return category
        return None

    def _is_purchase_question(self, normalized_text: str) -> bool:
        return any(phrase in normalized_text for phrase in self._purchase_question_phrases)

    def _mentioned_products(self, question: str) -> list[str]:
        normalized = self._normalize_text(question)
        mentioned: list[str] = []
        for product in catalog_service.list_products():
            if (
                self._normalize_text(product["name"]) in normalized
                or product["slug"] in normalized
            ):
                if product["slug"] not in mentioned:
                    mentioned.append(product["slug"])
        return mentioned

    def _suppressed_intents(self, normalized: str) -> set[str]:
        suppressions = {
            "camera": [
                "kamera onemli degil",
                "kamera cok onemli degil",
                "kamera gerekmiyor",
                "kamera bos",
                "kamera bos ama",
            ],
            "gaming": ["oyun onemli degil", "oyun oynamiyorum", "oyun gerekmiyor"],
            "battery": ["pil onemli degil", "sarj cok onemli degil"],
        }
        suppressed: set[str] = set()
        for intent_name, phrases in suppressions.items():
            if any(phrase in normalized for phrase in phrases):
                suppressed.add(intent_name)
        return suppressed

    def _expanded_query(self, *, category: str, question: str) -> str:
        normalized = self._normalize_text(question)
        has_gaming = any(
            token in normalized
            for token in ["pubg", "genshin", "fps", "gaming", "oyun", "lag", "kasma"]
        )
        has_heating = any(
            token in normalized
            for token in [
                "isiniyor",
                "isinma",
                "sicakliyor",
                "sicak",
                "sicaklik",
                "termal",
                "elde yaniyor",
                "elde yanma",
                "elimi yakmasin",
                "elde ates gibi",
                "ates gibi",
                "cok sicak",
                "overheating",
                "heat",
                "thermal",
                "hot",
            ]
        )
        has_low_light_camera = any(
            token in normalized
            for token in [
                "story",
                "instagram",
                "tiktok",
                "tik tok",
                "reels",
                "sosyal medya",
                "gece cekimi",
                "low light",
                "selfie",
            ]
        )

        if has_gaming and has_heating:
            expansion = "gaming performance thermal heating iphone"
        elif category == "gaming":
            expansion = "gaming performance thermal heating iphone"
        elif category == "heating":
            expansion = "heating thermal issue iphone"
        elif category == "camera" and has_low_light_camera:
            expansion = "camera quality iphone low light night selfie social media"
        else:
            expansion = self._intent_expansions.get(category, self._intent_expansions["general"])

        return f"{question.strip()} | {expansion}"

    def _classify_intent(self, question: str, current_product: dict) -> dict:
        normalized = self._normalize_text(question.strip())
        mentioned = self._mentioned_products(normalized)
        suppressed_intents = self._suppressed_intents(normalized)
        domain_signal = any(keyword in normalized for keyword in self._product_keywords)
        out_of_scope_signal = any(keyword in normalized for keyword in self._out_of_scope_keywords)
        semantic_category = self._semantic_category(normalized)
        has_gaming = any(
            keyword in normalized
            for keyword in ["oyun", "gaming", "fps", "performans", "performance", "pubg", "genshin", "lag", "kasma"]
        )
        has_heating = any(
            keyword in normalized
            for keyword in [
                "isiniyor",
                "isinma",
                "sicakliyor",
                "sicak",
                "termal",
                "elde yaniyor",
                "elde ates gibi",
                "ates gibi",
                "cok sicak",
                "overheating",
                "heat",
                "thermal",
                "hot",
                "koz",
                "kor",
                "yaniyor",
            ]
        )
        has_recommendation = self._is_purchase_question(normalized)
        has_long_term = any(
            keyword in normalized
            for keyword in [
                "uzun kullanim",
                "uzun vadede",
                "2 yil",
                "3 yil",
                "omurlu",
                "dayanir mi",
                "long term",
                "longevity",
            ]
        )
        has_daily_use = any(
            keyword in normalized
            for keyword in [
                "babam icin",
                "annem icin",
                "gunluk kullanim",
                "gundelik kullanim",
                "kolay kullanim",
                "whatsapp",
                "spotify",
                "universite",
                "arama",
            ]
        )

        comparison_keywords = ["compare", "karsilastir", "fark", "vs", "onceki", "previous"]
        if (
            any(keyword in normalized for keyword in comparison_keywords)
            or semantic_category == "comparison"
            or len(mentioned) >= 2
        ):
            targets = [current_product["slug"]]
            for slug in mentioned:
                if slug not in targets:
                    targets.append(slug)
            if len(targets) == 1:
                previous_model = decision_support_service.get_previous_model(current_product)
                if previous_model is not None:
                    targets.append(previous_model["slug"])
            return {
                "category": "comparison",
                "target_slugs": targets[:2],
                "is_unrelated": False,
                "retrieval_query": f"{question.strip()} | {self._intent_expansions['comparison']}",
                "active_intents": ["comparison"],
            }

        active_intents: list[str] = []
        if has_gaming:
            active_intents.append("gaming")
        if has_heating:
            active_intents.append("heating")
        if semantic_category == "battery" or any(
            keyword in normalized
            for keyword in ["pil", "sarj", "batarya", "battery", "ekran suresi", "dayaniklilik"]
        ):
            active_intents.append("battery")
        if semantic_category == "camera" or any(
            keyword in normalized
            for keyword in [
                "kamera",
                "fotograf",
                "video",
                "camera",
                "zoom",
                "gece cekimi",
                "lens",
                "instagram",
                "story",
                "tiktok",
                "tik tok",
                "reels",
                "sosyal medya",
                "low light",
                "selfie",
            ]
        ):
            active_intents.append("camera")
        if semantic_category == "recommendation" or has_recommendation:
            active_intents.append("recommendation")
        if semantic_category == "long-term" or has_long_term:
            active_intents.append("long-term")
        if semantic_category == "daily-use" or has_daily_use:
            active_intents.append("daily-use")
        active_intents = list(dict.fromkeys(active_intents))
        active_intents = [intent_name for intent_name in active_intents if intent_name not in suppressed_intents]

        if has_gaming and has_heating:
            category = "gaming"
        elif semantic_category == "comparison":
            category = "comparison"
        elif semantic_category == "battery":
            category = "battery"
        elif semantic_category == "camera":
            category = "camera"
        elif semantic_category == "heating":
            category = "heating"
        elif semantic_category == "gaming":
            category = "gaming"
        elif semantic_category == "recommendation":
            category = "recommendation"
        elif semantic_category == "long-term":
            category = "long-term"
        elif semantic_category == "daily-use":
            category = "daily-use"
        elif has_heating:
            category = "heating"
        elif any(
            keyword in normalized
            for keyword in ["pil", "sarj", "batarya", "battery", "ekran suresi", "dayaniklilik"]
        ):
            category = "battery"
        elif any(
            keyword in normalized
            for keyword in [
                "kamera",
                "fotograf",
                "video",
                "camera",
                "zoom",
                "gece cekimi",
                "lens",
                "instagram",
                "story",
                "tiktok",
                "tik tok",
                "reels",
                "sosyal medya",
                "low light",
                "selfie",
            ]
        ):
            category = "camera"
        elif has_gaming:
            category = "gaming"
        elif any(keyword in normalized for keyword in ["sikayet", "sorun", "problem", "risk", "eksi", "negatif"]):
            category = "negative"
        elif has_recommendation:
            category = "recommendation"
        elif has_long_term:
            category = "long-term"
        elif has_daily_use:
            category = "daily-use"
        elif out_of_scope_signal or (not domain_signal and len(normalized.split()) <= 2 and len(normalized) < 10):
            category = "nonsense/unrelated"
        elif not domain_signal and all(token not in normalized for token in ["bu", "this", "telefon", "model", "cihaz"]):
            category = "nonsense/unrelated"
        else:
            category = "general"

        if not active_intents and category not in {"nonsense/unrelated", "general"}:
            active_intents = [category]
        if not active_intents and category == "general":
            active_intents = ["general"]

        _casual_tokens = {
            "😅", "😄", "😂", "🤣", "😁", "🙃", "😬", "haha", "lol",
            "koz", "kor", "bez", "mq", "ya la", "vallah",
            "yandim", "oldu mu", "canim",
        }
        is_casual = (
            any(token in question for token in _casual_tokens)
            or any(token in normalized for token in _casual_tokens)
            or bool(re.search(
                r"\b(ya|be|abi|uzmez|uzmesin|su gibi|cok mu|ne kadar|ne olur|koz|kor)\b",
                normalized,
            ))
        )

        return {
            "category": category,
            "target_slugs": [current_product["slug"]],
            "is_unrelated": category == "nonsense/unrelated",
            "is_purchase_question": has_recommendation,
            "retrieval_query": self._expanded_query(category=category, question=question),
            "active_intents": active_intents,
            "is_casual": is_casual,
        }

    def _focus_aspect(self, intent: dict, chunks: list[dict]) -> str:
        category = intent["category"]
        if category in {"battery", "camera"}:
            return category
        if category == "gaming":
            return "performance"
        if category == "heating":
            return "heat"
        if category == "negative":
            return "general"
        for chunk in chunks:
            if chunk.get("aspect") and chunk["aspect"] != "general":
                return chunk["aspect"]
        return "general"

    def _sentiment_weight(self, chunk: dict) -> float:
        chunk_type = chunk.get("chunk_type")
        sentiment = chunk.get("sentiment", "neutral")
        if chunk_type == "strength":
            return 1.1
        if chunk_type in {"weakness", "risk_signal"}:
            return -1.2
        if chunk_type == "review":
            if sentiment == "positive":
                return 0.95
            if sentiment == "negative":
                return -0.95
            return 0.1
        if chunk_type == "product_description":
            return 0.25
        return 0.15

    def _score_value(self, chunk: dict) -> float:
        return float(chunk.get("ranking_score", chunk.get("similarity_score", 0)))

    def _single_product_verdict(self, product: dict, intent: dict, chunks: list[dict]) -> str:
        if not chunks:
            return f"{product['name']} icin bu soruya net cevap verecek kadar ilgili yorum cikmadi."
        aspect = self._focus_aspect(intent, chunks)
        return self._synthesized_aspect_summary(chunks, aspect_name=aspect, short=True)

    def _reason_from_chunk(self, chunk: dict, *, prefix_model: bool = False) -> str:
        source = chunk["source"]
        similarity = f"{chunk.get('similarity_score', 0):.2f}"
        model_prefix = f"{chunk['model']} icin " if prefix_model else ""
        return f"{model_prefix}{source} kaynaginda '{chunk['text']}' parcasi {similarity} benzerlikle eslesti."

    def _build_reasons(self, chunks: list[dict], *, prefix_model: bool = False, limit: int = 3) -> list[str]:
        reasons: list[str] = []
        seen: set[str] = set()
        for chunk in sorted(chunks, key=lambda item: -self._score_value(item)):
            key = self._normalize_text(f"{chunk['model']}|{chunk['text']}")
            if key in seen:
                continue
            reasons.append(self._reason_from_chunk(chunk, prefix_model=prefix_model))
            seen.add(key)
            if len(reasons) == limit:
                break
        return reasons

    def _build_evidence_snippets(self, chunks: list[dict], fallback_snippets: list[dict]) -> list[dict]:
        snippets: list[dict] = []
        seen: set[str] = set()
        for chunk in sorted(chunks, key=lambda item: -self._score_value(item)):
            cleaned_text = self._quality_evidence_text(chunk)
            key = self._normalize_text(f"{chunk['model']}|{cleaned_text}")
            if key in seen:
                continue
            snippets.append(
                {
                    "source": chunk["source"],
                    "text": cleaned_text,
                    "similarity_score": round(chunk.get("similarity_score", 0), 2),
                    "chunk_type": chunk.get("chunk_type"),
                    "aspect": chunk.get("aspect"),
                    "source_type": chunk.get("source_type"),
                    "source_platform": chunk.get("source_platform"),
                    "verified_purchase": chunk.get("verified_purchase"),
                    "rating": chunk.get("rating"),
                    "review_title": chunk.get("review_title"),
                    "source_url": chunk.get("source_url"),
                }
            )
            seen.add(key)
            if len(snippets) == 3:
                return snippets
        return [
            {
                "source": snippet["source"],
                "text": self._clean_evidence_fragment(snippet["text"]) or snippet["text"],
                "similarity_score": None,
                "chunk_type": None,
                "aspect": None,
                "source_type": None,
                "source_platform": None,
                "verified_purchase": None,
                "rating": None,
                "review_title": None,
                "source_url": None,
            }
            for snippet in fallback_snippets[:3]
        ]

    def _build_multi_intent_evidence_snippets(
        self,
        *,
        active_intents: list[str],
        chunks_by_intent: dict[str, list[dict]],
        fallback_snippets: list[dict],
    ) -> list[dict]:
        ordered_intents = ["gaming", "battery", "camera", "heating", "long-term", "recommendation"]
        selected_chunks: list[dict] = []
        seen: set[str] = set()

        for intent_name in ordered_intents:
            if intent_name not in active_intents:
                continue
            for chunk in chunks_by_intent.get(intent_name, []):
                key = self._normalize_text(f"{chunk.get('model')}|{chunk.get('source')}|{chunk.get('text')}")
                if key in seen:
                    continue
                selected_chunks.append(chunk)
                seen.add(key)
                break
            if len(selected_chunks) == 3:
                break

        if len(selected_chunks) < 3:
            remaining_chunks = self._merge_chunks_by_strength(list(chunks_by_intent.values()))
            for chunk in remaining_chunks:
                key = self._normalize_text(f"{chunk.get('model')}|{chunk.get('source')}|{chunk.get('text')}")
                if key in seen:
                    continue
                selected_chunks.append(chunk)
                seen.add(key)
                if len(selected_chunks) == 3:
                    break

        return self._build_evidence_snippets(selected_chunks, fallback_snippets)

    def _build_strengths(self, chunks: list[dict], review_summary: dict) -> list[str]:
        strengths: list[str] = []
        seen: set[str] = set()
        for chunk in chunks:
            if chunk["chunk_type"] in {"strength", "product_description"} or chunk.get("sentiment") == "positive":
                text = chunk["text"]
                key = self._normalize_text(text)
                if key in seen:
                    continue
                strengths.append(text)
                seen.add(key)
            if len(strengths) == 3:
                break
        return strengths or review_summary["top_positive_aspects"][:3]

    def _build_weaknesses(self, chunks: list[dict], review_summary: dict) -> list[str]:
        weaknesses: list[str] = []
        seen: set[str] = set()
        for chunk in chunks:
            if chunk["chunk_type"] in {"weakness", "risk_signal"} or chunk.get("sentiment") == "negative":
                text = chunk["text"]
                key = self._normalize_text(text)
                if key in seen:
                    continue
                weaknesses.append(text)
                seen.add(key)
            if len(weaknesses) == 3:
                break
        return weaknesses or review_summary["top_negative_aspects"][:3]

    def _build_issue_warnings(self, chunks: list[dict], issues: list[dict]) -> list[str]:
        warnings: list[str] = []
        seen: set[str] = set()
        for chunk in chunks:
            if chunk["chunk_type"] not in {"risk_signal", "weakness"} and chunk.get("sentiment") != "negative":
                continue
            text = chunk["chunk_label"] if chunk["chunk_type"] == "risk_signal" else chunk["text"]
            key = self._normalize_text(text)
            if key in seen:
                continue
            warnings.append(text)
            seen.add(key)
            if len(warnings) == 3:
                break
        return warnings or [issue["title"] for issue in issues[:3]]

    def _build_confidence_score(self, chunks: list[dict]) -> int:
        if not chunks:
            return 18
        top_chunks = chunks[:5]
        avg_similarity = sum(chunk["similarity_score"] for chunk in top_chunks) / len(top_chunks)
        source_diversity = min(len({chunk["source"] for chunk in top_chunks}), 3) / 3
        signal_strength = min(
            1.0,
            abs(
                sum(
                    self._sentiment_weight(chunk) * max(self._score_value(chunk), 0.05)
                    for chunk in top_chunks
                )
            )
            / 3,
        )
        score = avg_similarity * 68 + source_diversity * 12 + signal_strength * 20
        return max(0, min(100, round(score)))

    def _top_retrieved_sources(self, chunks: list[dict]) -> list[str]:
        sources: list[str] = []
        seen: set[str] = set()
        for chunk in chunks[:5]:
            normalized = self._normalize_text(chunk["source"])
            if normalized in seen:
                continue
            sources.append(chunk["source"])
            seen.add(normalized)
            if len(sources) == 3:
                break
        return sources

    def _confidence_label(self, chunks: list[dict], score: int | None = None) -> str:
        if not chunks:
            return "Low"
        top_chunks = chunks[:5]
        if score is None:
            score = self._build_confidence_score(chunks)
        strong_matches = sum(1 for chunk in top_chunks if chunk.get("similarity_score", 0) >= 0.72)
        has_positive = any(
            chunk.get("chunk_type") == "strength" or chunk.get("sentiment") == "positive"
            for chunk in top_chunks
        )
        has_negative = any(
            chunk.get("chunk_type") in {"weakness", "risk_signal"} or chunk.get("sentiment") == "negative"
            for chunk in top_chunks
        )
        if score < 45 or strong_matches <= 1:
            return "Low"
        if has_positive and has_negative:
            return "Medium"
        if strong_matches >= 3 and score >= 72:
            return "High"
        return "Medium"

    def _evidence_phrases(self, chunks: list[dict], *, limit: int = 2) -> list[str]:
        phrases: list[str] = []
        seen: set[str] = set()
        for chunk in sorted(chunks, key=lambda item: -self._score_value(item)):
            phrase = self._quality_evidence_text(chunk)
            key = self._normalize_text(phrase)
            if not phrase or key in seen:
                continue
            phrases.append(phrase)
            seen.add(key)
            if len(phrases) == limit:
                break
        return phrases

    def _issue_pattern_phrases(self, chunks: list[dict], *, limit: int = 1) -> list[str]:
        phrases: list[str] = []
        seen: set[str] = set()
        for chunk in chunks:
            if chunk.get("chunk_type") not in {"risk_signal", "weakness"}:
                continue
            label = (chunk.get("chunk_label") or chunk.get("text") or "").strip()
            if not label:
                continue
            key = self._normalize_text(label)
            if key in seen:
                continue
            phrases.append(label)
            seen.add(key)
            if len(phrases) == limit:
                break
        return phrases

    def _aspect_label_tr(self, aspect: str | None) -> str:
        return {
            "battery": "pil",
            "camera": "kamera",
            "performance": "performans",
            "heat": "isinma",
            "display": "ekran",
            "software": "yazilim",
            "durability": "dayaniklilik",
            "general": "genel kullanim",
        }.get(aspect or "general", "genel kullanim")

    # Each entry: (sentence_1, sentence_2_or_empty)
    # Patterns: A=observation→caveat, B=verdict→detail, C=casual-rec, D=friend-to-friend
    _aspect_sentence_pool: dict[str, dict[str, list[tuple[str, str]]]] = {
        "battery": {
            "positive": [
                ("Gunluk kullanim icin yarida birakmayan bir pil profili var.", "Yogun oyun ve video kullaniminda gun sonuna dogru zorlanabilir ama normal kullanimda iyi tutuyor."),
                ("Pil tarafinda cok buyuk sikayet gorünmüyor.", "Hafif-orta kullanicida iyi tutuyor; sadece cok yogun kullanimda biraz dikkat lazim."),
                ("Bu konuda panikleyecek bir durum yok.", "Normal bir kullanimda gunu rahatlıkla cikariyor; sadece maraton oyunculari dusünsün."),
                ("Gunluk isler, sosyal medya ve arama icin gayet yeterli.", "Oyun ve video odaklı yogun kullanim olacaksa gun sonu sarj arayanlar olabilir."),
            ],
            "negative": [
                ("Pil tarafında herkesin memnun oldugunu söylemek zor.", "Özellikle yogun kullanıcılarda erkenden biten sarj en sık çıkan tema."),
                ("Sarj ömrü konusunda gelen şikayetler var, göz ardı etmemek lazım.", "Hafif kullanıcı için sorun olmayabilir ama yoğun kullanımda beklentiyi aşağı çekmek gerekiyor."),
            ],
            "mixed": [
                ("Ortalama kullanıcıda sorun yok ama yoğun kullanımda tablo değişiyor.", "Gün ortasında şarj arayanların hikayeleri de var ortada."),
                ("Pil tarafından iki taraflı sinyal geliyor.", "Kimi 'yeterli' derken kimi gün bitmeden şarj takıyor."),
            ],
            "low": [
                ("Pil konusunda net bir şey söyleyen yeterli veri yok.", ""),
                ("Bu başlıkta yorum sinyali zayıf kaldı.", ""),
            ],
        },
        "camera": {
            "positive": [
                ("Kamera tarafında fena görünmüyor.", "İnsanların çoğu gündelik ve sosyal medya çekim ihtiyacını rahatlıkla karşılıyor."),
                ("Gece çekimi dahil genel kamera memnuniyeti iyi tarafta.", "Mucize bekleyenler hayal kırıklığına uğrayabilir ama standart beklenti karşılanıyor."),
                ("Bu konuda büyük bir şikayet yok ortada.", "TikTok, Instagram ve günlük hikayeler için yeterli bir profil çiziyor."),
                ("Kamera konusunda çok şikayet görünmüyor.", "Sosyal medya ve günlük çekimler için güven veren bir taraf."),
            ],
            "negative": [
                ("Kamera konusunda herkes aynı fikirde değil.", "Özellikle gece ve düşük ışık koşullarında daha temkinli yorumlar öne çıkıyor."),
                ("Kameranın beklentileri tam karşıladığını söylemek biraz zor.", "Sosyal medya için yeterli ama detay veya gece çekim odaklıysan biraz daha düşünmek lazım."),
            ],
            "mixed": [
                ("Kamera tarafında dengeli bir tablo var; çok iyi ama çok kötü de değil.", "Günlük kullanım için iyi, pro çekim beklentisi olanlar için yeterli olmayabilir."),
                ("Gündüz fotoğrafları için iyi haber; gece çekiminde tablo biraz daha karışık.", "Sosyal medya paylaşımı için yeterli ama gece detayı önemliyse not düşmek lazım."),
            ],
            "low": [
                ("Kamera konusunda net bir sinyal gelmiyor.", ""),
                ("Bu başlıkta veri yeterli değil; net konuşmak zor.", ""),
            ],
        },
        "performance": {
            "positive": [
                ("Oyun performansı tarafı güven veren kısım gibi duruyor.", "Büyük bir kasma şikayeti çok görünmüyor."),
                ("Performans tarafında ciddiye alınacak bir şikayet yok.", "Günlük kullanım akıcılığı ve oyun tarafı genellikle iyi geçen noktalar."),
                ("Bu noktada kullanıcıların büyük kısmı sıkıntı yaşamıyor.", "Oyun, akış ve genel hız için güven veren bir profil çiziyor."),
            ],
            "negative": [
                ("Performans tarafında herkes memnun değil.", "Özellikle güncelleme sonrası veya yoğun kullanımda yavaşlama haberleri var."),
                ("Kasma ve yavaşlama şikayetleri tamamen yok değil.", "Günlük kullanımda sorun çıkarmıyor ama yoğun oyun için biraz temkinli olmak lazım."),
            ],
            "mixed": [
                ("Performans tarafı genel iyi ama ısınma meselesini de hesaba katmak lazım.", "Uzun oyun oturumlarında cihaz ısınıyor; normal ama görmezden gelinecek düzeyde değil."),
                ("Günlük kullanımda akıcı ama uzun süreli yoğun kullanımda tablo biraz değişiyor.", ""),
            ],
            "low": [
                ("Performans konusunda net bir şey söyleyen yeterli yorum yok.", ""),
            ],
        },
        "heat": {
            "positive": [
                ("Isınma tarafında çok ciddi bir şikayet görünmüyor.", "Normal kullanımda termal sorun yaşamayan kullanıcılar çoğunlukta."),
                ("Bu konuda ciddi bir 'elde tutulmaz' durumu yok ortada.", "Hafif ısı normal; büyük çoğunluk bununla yaşayabiliyor."),
            ],
            "negative": [
                ("Uzun oyun oturumlarında ısınma oluyor, bu net.", "Elde tutulmayacak seviyede değil ama fark ediliyor."),
                ("Isınma konusunda bunu hisseden kullanıcı yorumları var.", "PUBG veya benzeri uzun oturumlarda kasanın ısındığını beklemek mantıklı."),
            ],
            "mixed": [
                ("Isınma konusunda biraz karışık bir tablo var.", "Oyun sırasında fark edilebilir ısı olsa da büyük çoğunluk bununla yaşayabiliyor."),
                ("Kısa oyun oturumlarında sorun yok ama uzun oturumlarda ısı hissediliyor.", ""),
            ],
            "low": [
                ("Isınma başlığında net bir sinyal gelmiyor.", ""),
            ],
        },
        "general": {
            "positive": [
                ("Genel kullanımda tatmin edici bir profil çiziyor.", "Büyük bir sürpriz yok ama büyük bir hayal kırıklığı da yok."),
                ("Ortalama kullanıcı için çok şikayet görünmüyor.", "Temel ihtiyaçları karşılayan, büyük sıkıntı çıkarmayan bir cihaz."),
            ],
            "negative": [
                ("Bu konuda temkinli yaklaşmak gerekiyor.", "Kullanıcı yorumlarında dikkat çekici şikayetler var."),
            ],
            "mixed": [
                ("Tablo tam net değil; hem iyi haberler hem temkinli notlar geliyor.", "Kişisel beklentiyi netleştirmek önemli."),
                ("İki taraflı sinyal geliyor; iyi yanları da var, dikkat edilmesi gereken de.", ""),
            ],
            "low": [
                ("Bu konuda net bir şey söylemek için yeterli sinyal yok.", ""),
            ],
        },
    }

    _conclusion_pool: dict[str, list[str]] = {
        "battery": [
            "Kısacası günlük kullanım için yeterli; sadece yoğun oyunculara not düşmek lazım.",
            "Kısacası şarj konusunda çok büyük sürpriz bekleme, ama gün ortasında kalmaz genelde.",
            "Kısacası pil için beklentiyi çok yükseğe koymadan kullanmak mantıklı.",
        ],
        "camera": [
            "Kısacası kamera önceliğinse tatmin edici görünüyor; Pro olmasa da işi görüyor.",
            "Kısacası gündelik ve sosyal medya çekimleri için sorunsuz bir seçenek.",
            "Kısacası kameradan keyif almak için bir üst modele gitmen şart değil.",
        ],
        "performance": [
            "Kısacası yoğun oyuncu değilsen sorun çıkaracak bir tablo görünmüyor.",
            "Kısacası oyun tarafında da kendini iyi tutuyor, büyük bir endişe yok.",
            "Kısacası günlük akıcılık için güven veren bir profil.",
        ],
        "heat": [
            "Kısacası uzun oyun oturumlarında biraz ısınma beklemek mantıklı ama dramatik değil.",
            "Kısacası ısınma var, tamamen soğuk kalmıyor; ama ciddi bir sorun sinyali yok.",
        ],
        "general": [
            "Kısacası genel kullanım için sorun çıkarmayan bir cihaz profili.",
            "Kısacası beklentiyi dengede tutarsan pişman etmeyecek bir seçenek.",
        ],
    }

    def _pick(self, pool: list[str], key: int) -> str:
        return pool[key % len(pool)]

    def _synthesis_key(self, chunks: list[dict]) -> int:
        return sum(hash(chunk.get("text", "")) for chunk in chunks[:3]) & 0xFFFF

    def _synthesized_aspect_summary(
        self,
        chunks: list[dict],
        *,
        aspect_name: str | None = None,
        short: bool = False,
    ) -> str:
        if not chunks:
            return "Bu konuda net bir sinyal gelmiyor." if short else "Yeterli yorum yok."

        confidence_label = self._confidence_label(chunks)
        aspect_key = aspect_name or (chunks[0].get("aspect") or "general")
        # Normalise aspect keys to pool keys
        if aspect_key in {"heat", "isinma"}:
            aspect_key = "heat"
        elif aspect_key not in self._aspect_sentence_pool:
            aspect_key = "general"

        positive = [
            c for c in chunks
            if c.get("chunk_type") == "strength" or c.get("sentiment") == "positive"
        ]
        negative = [
            c for c in chunks
            if c.get("chunk_type") in {"weakness", "risk_signal"} or c.get("sentiment") == "negative"
        ]

        if confidence_label == "Low":
            sentiment_key = "low"
        elif positive and negative:
            sentiment_key = "mixed"
        elif negative:
            sentiment_key = "negative"
        elif positive:
            sentiment_key = "positive"
        else:
            sentiment_key = "mixed"

        pool = self._aspect_sentence_pool.get(aspect_key, self._aspect_sentence_pool["general"])
        sentences = pool.get(sentiment_key) or pool.get("mixed") or pool.get("positive") or [("Yeterli yorum yok.", "")]
        key = self._synthesis_key(chunks)
        s1, s2 = self._pick(sentences, key)
        return f"{s1} {s2}".strip() if s2 else s1

    def _conclusion_sentence(
        self, *, aspect_name: str | None, confidence_label: str, is_purchase_question: bool
    ) -> str | None:
        if confidence_label == "Low":
            return None
        aspect = aspect_name or "general"
        pool = self._conclusion_pool.get(aspect, self._conclusion_pool["general"])
        key = hash(aspect + confidence_label) & 0xFFFF
        conclusion = self._pick(pool, key)
        if not is_purchase_question and confidence_label == "Medium":
            return None
        return conclusion

    _confidence_sentence_pool: dict[str, list[str]] = {
        "High": [
            "Yorumlar bu konuda oldukça tutarlı.",
            "Bu başlıkta tablo daha net okunuyor.",
            "Sinyaller burada daha bir araya gelmiş.",
        ],
        "Medium": [
            "Her kullanıcı aynı deneyimi yaşamıyor ama genel yön belli.",
            "Tabloda net bir çizgi çizmek zor ama ağırlık bir tarafta.",
            "Herkes aynı fikirde değil; ama dengenin bir tarafa fazla kaçtığını söyleyebiliriz.",
        ],
        "Low": [
            "Bu konuda net konuşmak için yeterli sinyal yok.",
            "Yorumlar dağınık kaldığı için burada net bir şey söylemek zor.",
        ],
    }

    def _confidence_sentence(self, confidence_label: str, *, seed: int = 0) -> str:
        pool = self._confidence_sentence_pool.get(confidence_label, self._confidence_sentence_pool["Low"])
        return self._pick(pool, seed)

    def _comparison_aspect_chunk(self, chunks: list[dict], aspect_name: str) -> dict | None:
        aspect_map = {
            "battery": {"battery"},
            "camera": {"camera"},
            "performance": {"performance", "heat"},
        }
        allowed_aspects = aspect_map[aspect_name]
        candidates = [
            chunk for chunk in chunks if chunk.get("aspect") in allowed_aspects
        ]
        if not candidates:
            if aspect_name == "performance":
                candidates = [
                    chunk
                    for chunk in chunks
                    if chunk.get("chunk_type") in {"real_review", "review", "risk_signal"}
                    and chunk.get("aspect") not in {"battery", "camera"}
                ]
        if not candidates:
            return None
        return max(candidates, key=lambda item: self._score_value(item))

    def _comparison_aspect_line(self, chunks: list[dict], aspect_name: str) -> str:
        chunk = self._comparison_aspect_chunk(chunks, aspect_name)
        if chunk is None:
            return "Yeterli yorum yok."
        related_chunks = [
            candidate
            for candidate in chunks
            if candidate.get("aspect") == chunk.get("aspect")
            or (
                aspect_name == "performance"
                and candidate.get("aspect") in {"performance", "heat"}
            )
        ]
        return self._synthesized_aspect_summary(
            related_chunks or [chunk],
            aspect_name="heat" if aspect_name == "performance" and chunk.get("aspect") == "heat" else aspect_name,
        )

    def _lead_phrase(self, category: str, *, is_purchase_question: bool) -> str:
        return {
            "battery": "Gunluk kullanim icin",
            "camera": "Kamera tarafinda",
            "gaming": "Eger onceligin oyun ise" if is_purchase_question else "Oyun tarafinda",
            "heating": "Genel tabloya bakinca",
            "recommendation": "Genel tabloya bakinca",
            "daily-use": "Gunluk kullanim tarafinda",
            "long-term": "Uzun kullanim tarafinda",
            "negative": "Kullanici yorumlarinda sik gorulen durum",
            "general": "Genel tabloya bakinca",
        }.get(category, "Genel tabloya bakinca")

    def _top_chunks_by_sentiment(self, chunks: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
        positive: list[dict] = []
        negative: list[dict] = []
        neutral: list[dict] = []
        for chunk in chunks:
            sentiment = chunk.get("sentiment")
            if chunk.get("chunk_type") in {"risk_signal", "weakness"} or sentiment == "negative":
                negative.append(chunk)
            elif chunk.get("chunk_type") == "strength" or sentiment == "positive":
                positive.append(chunk)
            else:
                neutral.append(chunk)
        return positive, negative, neutral

    def _natural_chunk_phrase(self, chunk: dict) -> str:
        text = chunk.get("text", "").strip().rstrip(".")
        if not text:
            return ""
        return text[0].lower() + text[1:] if len(text) > 1 else text.lower()

    def _build_single_natural_sentences(
        self, *, product: dict, intent: dict, chunks: list[dict], is_purchase_question: bool
    ) -> list[str]:
        sentences: list[str] = []
        confidence_score = self._build_confidence_score(chunks)
        confidence_label = self._confidence_label(chunks, confidence_score)
        aspect = self._focus_aspect(intent, chunks)
        key = self._synthesis_key(chunks)

        # _synthesized_aspect_summary handles Low confidence internally
        summary = self._synthesized_aspect_summary(chunks, aspect_name=aspect)
        sentences.append(summary)

        if confidence_label not in {"Low"}:
            conclusion = self._conclusion_sentence(
                aspect_name=aspect,
                confidence_label=confidence_label,
                is_purchase_question=is_purchase_question,
            )
            if conclusion and conclusion not in sentences:
                sentences.append(conclusion)

        return sentences[:2]

    def _merge_chunks_by_strength(self, chunk_groups: list[list[dict]]) -> list[dict]:
        merged: dict[str, dict] = {}
        for group in chunk_groups:
            for chunk in group:
                key = self._normalize_text(
                    f"{chunk.get('model')}|{chunk.get('source')}|{chunk.get('text')}"
                )
                existing = merged.get(key)
                if existing is None or self._score_value(chunk) > self._score_value(existing):
                    merged[key] = chunk
        return sorted(merged.values(), key=lambda item: -self._score_value(item))

    def _build_multi_intent_answer(
        self,
        *,
        product: dict,
        active_intents: list[str],
        chunks_by_intent: dict[str, list[dict]],
        is_purchase_question: bool,
    ) -> str:
        ordered_intents = ["gaming", "battery", "camera", "heating", "daily-use", "long-term"]
        section_meta = {
            "gaming": ("🎮", "Gaming"),
            "battery": ("🔋", "Battery"),
            "camera": ("📷", "Camera"),
            "heating": ("🔥", "Heating"),
            "daily-use": ("👤", "Daily use"),
            "long-term": ("🕒", "Uzun Kullanım"),
        }

        def section_block(intent_name: str, section_chunks: list[dict]) -> str:
            confidence_label = self._confidence_label(section_chunks)
            aspect_name = {
                "gaming": "performance",
                "battery": "battery",
                "camera": "camera",
                "heating": "heat",
                "daily-use": "general",
                "long-term": "general",
            }.get(intent_name, "general")

            evaluation = self._synthesized_aspect_summary(section_chunks, aspect_name=aspect_name)
            icon, title = section_meta[intent_name]
            return f"{icon} {title}\n{evaluation}"

        sections: list[str] = []
        for intent_name in ordered_intents:
            if intent_name not in active_intents:
                continue
            section_chunks = chunks_by_intent.get(intent_name, [])
            if not section_chunks:
                continue
            sections.append(section_block(intent_name, section_chunks))

        merged_chunks = self._merge_chunks_by_strength(list(chunks_by_intent.values()))
        overall_confidence = self._confidence_label(merged_chunks)
        overall_key = self._synthesis_key(merged_chunks)
        if overall_confidence == "Low":
            final_body = self._pick([
                "Bu konuda net bir şey söylemek için yeterli sinyal yok.",
                "Veri sınırlı; net bir yargıya varmak için yeterli yorum gelmiyor.",
            ], overall_key)
            final_parts = [final_body]
        else:
            evidence_phrases = self._evidence_phrases(merged_chunks, limit=2)
            if len(evidence_phrases) >= 2:
                final_body = self._pick([
                    "Farklı başlıklarda tablo benzer bir yöne işaret ediyor.",
                    "Başlıklar arasında tam örtüşme olmasa da genel bir yön çiziyor.",
                    "Her konu biraz farklı ama ortak bir sinyal var.",
                ], overall_key)
            elif evidence_phrases:
                final_body = self._pick([
                    "Bu tabloya göre bir yönde daha belirgin bir ağırlık var.",
                    "Sinyaller dağınık değil; belirli bir yöne doğru toplanmış.",
                ], overall_key)
            else:
                final_body = "Net bir ortak sonuca bağlamak biraz güçleşiyor."
            conf_line = self._confidence_sentence(overall_confidence, seed=overall_key)
            final_parts = [final_body, conf_line] if conf_line not in [final_body] else [final_body]
            if overall_confidence in {"High", "Medium"}:
                conclusion = self._pick(self._conclusion_pool["general"], overall_key)
                if conclusion not in final_parts:
                    final_parts.append(conclusion)
        final_title = "🎯 Final recommendation" if is_purchase_question else "🎯 Genel tablo"
        final_line = f"{final_title}\n" + "\n".join(final_parts)

        sections.append(final_line)
        return "\n\n".join(sections[:4])

    def _build_retrieval_debug(self, intent: dict, chunks: list[dict]) -> list[dict]:
        debug_items: list[dict] = []
        for chunk in chunks[:5]:
            debug_items.append(
                {
                    "intent": intent["category"].upper(),
                    "model": chunk.get("model"),
                    "source": chunk.get("source"),
                    "text": chunk.get("text"),
                    "similarity": round(chunk.get("similarity_score", 0), 2),
                    "boost": round(chunk.get("boost_score", 0), 2),
                    "penalty": round(chunk.get("penalty_score", 0), 2),
                    "final": round(chunk.get("final_score", chunk.get("ranking_score", 0)), 2),
                    "matched_boost_terms": chunk.get("matched_boost_terms", []),
                    "matched_penalty_terms": chunk.get("matched_penalty_terms", []),
                }
            )
        return debug_items

    def _build_unrelated_response(
        self, *, recommendation_score: int, recommendation_verdict: str
    ) -> dict:
        return {
            "answer": "Bu soru urun bilgisi kapsaminin disinda kaliyor. Asistan yalnizca urun ozellikleri ve kullanici yorumu temelli sorulari yanitliyor.",
            "quick_verdict": "This question is outside the product knowledge scope.",
            "strengths": [],
            "weaknesses": [],
            "issue_warnings": [],
            "recommendation_score": recommendation_score,
            "evidence_snippets": [],
            "recommendation_verdict": recommendation_verdict,
            "confidence_score": 100,
            "confidence_label": "High",
            "evidence_count": 0,
            "top_retrieved_sources": [],
            "intent_category": "NONSENSE/UNRELATED",
            "retrieval_debug": [],
        }

    _casual_prefix_pool: dict[str, list[str]] = {
        "heating": [
            "😄 Uzun oyun oturumlarında biraz ısınmadan bahseden kullanıcılar var ama 'elde tutulmayacak seviyede' bir durum görünmüyor.",
            "😅 Isınıyor mu dersen; biraz evet. Ama elde köz olmak değil bu; normal bir ısı.",
            "😄 Ciddi bir 'elim yandı' hikayesi yok ortada. Hafif ısı olan ama büyük çoğunluğun yaşayabildiği bir tablo.",
            "😅 PUBG'de tam 'kestim batarya' demeyeceksin ama ısındığını hissedeceksin — bu normal.",
        ],
        "gaming": [
            "🎮 Oyun performansı tarafı güven veren kısım gibi duruyor. Büyük bir kasma şikayeti çok görünmüyor.",
            "😄 Oyun için paniklemene gerek yok; ciddi bir performans şikayeti yok ortada.",
            "🎮 Kasma veya takılma haberleri çok yoğun değil. Genel tablo oyun için sorunsuz.",
        ],
        "camera": [
            "📸 Gece çekimi tarafında fena görünmüyor. İnsanların çoğu kameradan memnun ama mucize bekleyenler de var.",
            "😊 Gece story için üzmez gibi görünüyor. Sosyal medya ve günlük paylaşım için çoğu kişi yeterli buluyor.",
            "📸 Kamera konusunda büyük bir şikayet yok; gündelik ve sosyal medya için gayet iyi.",
        ],
        "battery": [
            "🔋 Günlük kullanımda çoğu kişiyi yarı yolda bırakmıyor. Ama oyun, video ve yoğun kullanımda gün sonuna yaklaşırken şarj arayanlar var.",
            "😌 Tam 'su gibi gidiyor' değil ama yoğun kullanım dışında sorun yaratmıyor.",
            "🔋 Şarj konusunda çok büyük sürpriz yok; normal kullanımda gün çıkıyor.",
        ],
        "general": [
            "😄 Genel tablo fena görünmüyor. Büyük bir şikayet başlığı yok.",
            "😊 Kullanıcı tarafında memnuniyetsizlik sesi fazla yüksek değil.",
        ],
    }

    def _build_single_answer(
        self,
        *,
        product: dict,
        intent: dict,
        chunks: list[dict],
        confidence_score: int,
        evidence_count: int,
        top_sources: list[str],
        is_purchase_question: bool,
    ) -> str:
        is_casual = intent.get("is_casual", False)
        category = intent.get("category", "general")

        if is_casual and category in self._casual_prefix_pool:
            key = self._synthesis_key(chunks)
            prefix = self._pick(self._casual_prefix_pool[category], key)
            conf_label = self._confidence_label(chunks)
            conclusion = self._conclusion_sentence(
                aspect_name=self._focus_aspect(intent, chunks),
                confidence_label=conf_label,
                is_purchase_question=is_purchase_question,
            )
            parts = [prefix]
            if conclusion and conclusion not in parts:
                parts.append(conclusion)
            return " ".join(parts)

        sentences = self._build_single_natural_sentences(
            product=product, intent=intent, chunks=chunks, is_purchase_question=is_purchase_question
        )
        return " ".join(sentence.strip() for sentence in sentences if sentence.strip())

    def _build_comparison_response(
        self,
        *,
        current_product: dict,
        intent: dict,
        question: str,
        recommendation_score: int,
        recommendation_verdict: str,
    ) -> dict:
        target_slugs = intent["target_slugs"][:2]
        products = [catalog_service.get_product(target_slugs[0]), catalog_service.get_product(target_slugs[1])]
        per_product_chunks = {
            product["slug"]: retrieval_service.retrieve_chunks(
                question,
                slug=product["slug"],
                allowed_slugs=[product["slug"]],
                category="comparison",
                limit=4,
            )
            for product in products
        }
        combined_chunks = sorted(
            [chunk for product in products for chunk in per_product_chunks[product["slug"]]],
            key=lambda item: -self._score_value(item),
        )
        confidence_score = self._build_confidence_score(combined_chunks)
        evidence_count = len(combined_chunks)
        top_sources = self._top_retrieved_sources(combined_chunks)

        scores = {
            product["slug"]: sum(
                self._sentiment_weight(chunk) * max(self._score_value(chunk), 0.05)
                for chunk in per_product_chunks[product["slug"]]
            )
            for product in products
        }
        winner = max(products, key=lambda product: scores[product["slug"]])
        loser = min(products, key=lambda product: scores[product["slug"]])

        confidence_label = self._confidence_label(combined_chunks, confidence_score)
        enough_data = (
            confidence_label != "Low"
            and all(len(per_product_chunks[product["slug"]]) >= 2 for product in products)
        )
        if not enough_data:
            short_answer = "Karşılaştırma için yeterli veri bulunamadı."
            answer = short_answer
        else:
            short_answer = (
                f"Genel tabloya gore {winner['name']}, {loser['name']} karsisinda biraz daha derli toplu duruyor."
                if abs(scores[winner["slug"]] - scores[loser["slug"]]) >= 0.2
                else f"Gercek yorumlara bakinca {products[0]['name']} ve {products[1]['name']} birbirine epey yakin duruyor."
            )
            answer = "\n".join(
                [
                    f"{products[0]['name']}",
                    f"- Pil: {self._comparison_aspect_line(per_product_chunks[products[0]['slug']], 'battery')}",
                    f"- Kamera: {self._comparison_aspect_line(per_product_chunks[products[0]['slug']], 'camera')}",
                    f"- Performans: {self._comparison_aspect_line(per_product_chunks[products[0]['slug']], 'performance')}",
                    "",
                    f"{products[1]['name']}",
                    f"- Pil: {self._comparison_aspect_line(per_product_chunks[products[1]['slug']], 'battery')}",
                    f"- Kamera: {self._comparison_aspect_line(per_product_chunks[products[1]['slug']], 'camera')}",
                    f"- Performans: {self._comparison_aspect_line(per_product_chunks[products[1]['slug']], 'performance')}",
                    "",
                    "Sonuç:",
                    short_answer,
                ]
            )

        strengths = [
            f"{product['name']}: {per_product_chunks[product['slug']][0]['text']}"
            for product in products
            if per_product_chunks[product["slug"]]
        ][:3]
        weaknesses = [
            f"{chunk['model']}: {chunk['text']}"
            for chunk in combined_chunks
            if chunk.get("sentiment") == "negative" or chunk["chunk_type"] in {"risk_signal", "weakness"}
        ][:3]
        evidence_snippets = self._build_evidence_snippets(
            combined_chunks, current_product["analysis"]["review_summary"]["evidence_snippets"]
        )

        return {
            "answer": answer,
            "quick_verdict": short_answer,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "issue_warnings": weaknesses[:3],
            "recommendation_score": recommendation_score,
            "evidence_snippets": evidence_snippets,
            "recommendation_verdict": recommendation_verdict,
            "confidence_score": confidence_score,
            "confidence_label": confidence_label,
            "evidence_count": evidence_count,
            "top_retrieved_sources": top_sources,
            "intent_category": "COMPARISON",
            "retrieval_debug": self._build_retrieval_debug(intent, combined_chunks),
        }

    def answer_question(self, slug: str, question: str) -> dict:
        product = catalog_service.get_product(slug)
        review_summary = product["analysis"]["review_summary"]
        issues = product["analysis"]["common_issues"]
        decision_support = decision_support_service.build_decision_support(product)
        recommendation_score = decision_support_service.get_recommendation_score(
            product, review_summary, issues
        )
        intent = self._classify_intent(question, product)

        if intent["is_unrelated"]:
            return self._build_unrelated_response(
                recommendation_score=recommendation_score,
                recommendation_verdict=decision_support["recommendation_verdict"],
            )

        if intent["category"] == "comparison" and len(intent["target_slugs"]) >= 2:
            return self._build_comparison_response(
                current_product=product,
                intent=intent,
                question=intent["retrieval_query"],
                recommendation_score=recommendation_score,
                recommendation_verdict=decision_support["recommendation_verdict"],
            )

        active_intents = intent.get("active_intents", [intent["category"]])
        chunks_by_intent = {
            intent_name: retrieval_service.retrieve_chunks(
                self._expanded_query(category=intent_name, question=question),
                slug=slug,
                allowed_slugs=[slug],
                category=intent_name,
                limit=4 if intent_name != "recommendation" else 3,
            )
            for intent_name in active_intents
        }
        chunks = self._merge_chunks_by_strength(list(chunks_by_intent.values()))
        confidence_score = self._build_confidence_score(chunks)
        evidence_count = len(chunks)
        top_retrieved_sources = self._top_retrieved_sources(chunks)
        evidence_snippets = (
            self._build_multi_intent_evidence_snippets(
                active_intents=active_intents,
                chunks_by_intent=chunks_by_intent,
                fallback_snippets=review_summary["evidence_snippets"],
            )
            if len([name for name in active_intents if name != "recommendation"]) > 1
            else self._build_evidence_snippets(chunks, review_summary["evidence_snippets"])
        )
        if len([name for name in active_intents if name != "recommendation"]) > 1:
            answer = self._build_multi_intent_answer(
                product=product,
                active_intents=active_intents,
                chunks_by_intent=chunks_by_intent,
                is_purchase_question=intent.get("is_purchase_question", False),
            )
        else:
            answer = self._build_single_answer(
                product=product,
                intent=intent,
                chunks=chunks,
                confidence_score=confidence_score,
                evidence_count=evidence_count,
                top_sources=top_retrieved_sources,
                is_purchase_question=intent.get("is_purchase_question", False),
            )

        return {
            "answer": answer,
            "quick_verdict": self._single_product_verdict(product, intent, chunks),
            "strengths": self._build_strengths(chunks, review_summary),
            "weaknesses": self._build_weaknesses(chunks, review_summary),
            "issue_warnings": self._build_issue_warnings(chunks, issues),
            "recommendation_score": recommendation_score,
            "evidence_snippets": evidence_snippets,
            "recommendation_verdict": decision_support["recommendation_verdict"],
            "confidence_score": confidence_score,
            "confidence_label": self._confidence_label(chunks, confidence_score),
            "evidence_count": evidence_count,
            "top_retrieved_sources": top_retrieved_sources,
            "intent_category": intent["category"].upper(),
            "retrieval_debug": self._build_retrieval_debug(intent, chunks),
        }


chat_service = ChatService()
