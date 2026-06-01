import json
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "iphone_catalog.json"
REVIEWS_PATH = ROOT / "iphone_reviews.json"

SOURCES = ["Reddit", "Community forum", "User review", "Tech community"]

POSITIVE_TEMPLATES = {
    "battery": [
        "{model} pil tarafinda bekledigimden daha tutarli. {battery}.",
        "Gun sonunda {model} hala rahat kaliyor; ozellikle {battery}.",
    ],
    "camera": [
        "{model} kamerasi gunluk cekimlerde guven veriyor. {camera}.",
        "Ozellikle fotograf ve video tarafinda {model} bekledigimden daha iyi. {camera}.",
    ],
    "performance": [
        "{model} gunluk kullanimda cok akici hissettiriyor. {chipset} hala cok guclu.",
        "Uygulama gecisleri ve oyunlarda {model} oldukca hizli. {chipset} farki hissediliyor.",
    ],
    "display": [
        "{model} ekran kalitesi bu sinifta hala cok iyi. {display} paneli memnun ediyor.",
        "Icerik tuketirken {model} ekrani temiz ve keyifli gorunuyor.",
    ],
    "software": [
        "{model} yazilim tarafinda istikrarli ve uzun sure kullanilabilir hissettiriyor.",
        "iOS deneyimi {model} ustunde tutarli ve sorunsuz ilerliyor.",
    ],
    "durability": [
        "{model} elde kaliteli ve dayanikli hissettiriyor.",
        "Govde kalitesi sayesinde {model} uzun omurlu bir cihaz izlenimi veriyor.",
    ],
}

NEUTRAL_TEMPLATES = {
    "battery": [
        "{model} pili kotu degil ama cok yogun gunde ekstra sarj isteyebiliyor.",
        "{battery}; yani genel olarak yeterli ama buyuk bir surpriz de degil.",
    ],
    "camera": [
        "{model} kamera tarafinda guvenilir ama fark yaratan kisim daha cok isik kosullarina bagli.",
        "{camera}; genel olarak memnunum ama her senaryoda premium seviye degil.",
    ],
    "price": [
        "{model} iyi bir cihaz ama fiyatini de hissettiriyor.",
        "Genel paket dengeli, yine de {model} icin fiyat tarafini iyi tartmak gerekiyor.",
    ],
    "software": [
        "{model} yazilim deneyimi iyi, ama yenilikler bazen bekledigim kadar buyuk hissettirmiyor.",
        "iOS akici ama {model} ile onceki nesil arasinda her zaman dramatik fark hissetmedim.",
    ],
}

NEGATIVE_TEMPLATES = {
    "battery": [
        "{model} yogun kullanimda aksam saatlerine dogru pili hizli dusurebiliyor.",
        "{model} tarafinda pil beklentim biraz daha yuksekti; ozellikle yogun gunlerde yetmiyor.",
    ],
    "camera": [
        "{model} kamera genel olarak iyi ama gece cekimlerinde her zaman bekledigim kadar stabil degil.",
        "Kamera tutarli olsa da {model} fiyatina gore daha guclu bir sicrama bekliyordum.",
    ],
    "heat": [
        "{model} oyun, kamera ve navigasyon gibi yuklerde belirgin isinabiliyor.",
        "Uzun sure cekim veya performans yukunde {model} elde sicak hissettiriyor.",
    ],
    "price": [
        "{model} iyi ama bugunku fiyat seviyesiyle daha zor tavsiye ediyorum.",
        "Performansi guclu olsa da {model} icin fiyat tarafi halen can sikabiliyor.",
    ],
    "durability": [
        "{model} genel olarak kaliteli ama buyuk ya da agir formu uzun kullanimda yorabiliyor.",
        "Ergonomi tarafinda {model} herkese hitap etmiyor; elde uzun sure tasimasi zorlayabiliyor.",
    ],
    "storage": [
        "{model} baslangic depolamasi bana hizli doluyor gibi geldi.",
        "Ozellikle uzun sureli kullanimda {model} icin dusuk depolama secenekleri sinirlayici olabiliyor.",
    ],
}


def normalize_review_counts(product: dict) -> tuple[int, int, int]:
    slug = product["slug"]
    year = product["release_year"]

    positive = 9 + max(0, year - 2021)
    neutral = 4
    negative = 5

    if "pro" in slug:
        positive += 1
    if "max" in slug or "plus" in slug:
        positive += 1
    if "mini" in slug:
        negative += 2
        positive -= 1

    return positive, neutral, negative


def build_positive_aspects(product: dict) -> list[str]:
    aspects = ["performance", "display", "camera", "battery", "software"]
    slug = product["slug"]
    if "max" in slug or "plus" in slug:
        aspects.insert(0, "battery")
    if "pro" in slug:
        aspects.insert(0, "camera")
    if "mini" in slug:
        aspects.append("durability")
    return aspects


def build_negative_aspects(product: dict) -> list[str]:
    issues_text = " ".join(
        [issue["title"].lower() + " " + issue["description"].lower() for issue in product["analysis"]["common_issues"]]
    )
    aspects = ["price", "storage"]
    if "isinma" in issues_text or "termal" in issues_text:
        aspects.insert(0, "heat")
    if "pil" in issues_text:
        aspects.insert(0, "battery")
    if "ergonomi" in issues_text or "agir" in issues_text or "hacimli" in issues_text:
        aspects.append("durability")
    if "camera" in product["camera_summary"].lower() or "kamera" in product["camera_summary"].lower():
        aspects.append("camera")
    return aspects


def render_text(bucket: str, aspect: str, product: dict, index: int) -> str:
    model = product["name"]
    template_map = {
        "positive": POSITIVE_TEMPLATES,
        "neutral": NEUTRAL_TEMPLATES,
        "negative": NEGATIVE_TEMPLATES,
    }[bucket]
    template = template_map[aspect][index % len(template_map[aspect])]
    return template.format(
        model=model,
        battery=product["battery_summary"],
        camera=product["camera_summary"],
        chipset=product["chipset"],
        display=f"{product['display_type']} {product['display_size']}",
    )


def rating_for(bucket: str, aspect: str, index: int) -> int:
    if bucket == "positive":
        return 5 if index % 3 != 0 else 4
    if bucket == "neutral":
        return 3 if aspect in {"price", "battery"} else 4
    return 2 if index % 2 == 0 else 3


def source_for(index: int) -> str:
    return SOURCES[index % len(SOURCES)]


def timestamp_for(product: dict, index: int) -> str:
    base = datetime(max(2023, product["release_year"]), 1, 15, 10, 30, 0)
    moment = base + timedelta(days=index * 17 + product["release_year"] % 11)
    return moment.isoformat() + "Z"


def build_reviews(products: list[dict]) -> list[dict]:
    reviews: list[dict] = []

    for product in products:
        positive_count, neutral_count, negative_count = normalize_review_counts(product)
        positive_aspects = build_positive_aspects(product)
        negative_aspects = build_negative_aspects(product)
        neutral_aspects = ["price", "battery", "camera", "software"]

        review_index = 0

        for idx in range(positive_count):
            aspect = positive_aspects[idx % len(positive_aspects)]
            reviews.append(
                {
                    "id": f"review-{product['slug']}-{review_index + 1:02d}",
                    "model": product["name"],
                    "rating": rating_for("positive", aspect, idx),
                    "text": render_text("positive", aspect, product, idx),
                    "aspect": aspect,
                    "sentiment": "positive",
                    "source": source_for(review_index),
                    "timestamp": timestamp_for(product, review_index),
                }
            )
            review_index += 1

        for idx in range(neutral_count):
            aspect = neutral_aspects[idx % len(neutral_aspects)]
            reviews.append(
                {
                    "id": f"review-{product['slug']}-{review_index + 1:02d}",
                    "model": product["name"],
                    "rating": rating_for("neutral", aspect, idx),
                    "text": render_text("neutral", aspect, product, idx),
                    "aspect": aspect,
                    "sentiment": "neutral",
                    "source": source_for(review_index),
                    "timestamp": timestamp_for(product, review_index),
                }
            )
            review_index += 1

        for idx in range(negative_count):
            aspect = negative_aspects[idx % len(negative_aspects)]
            reviews.append(
                {
                    "id": f"review-{product['slug']}-{review_index + 1:02d}",
                    "model": product["name"],
                    "rating": rating_for("negative", aspect, idx),
                    "text": render_text("negative", aspect, product, idx),
                    "aspect": aspect,
                    "sentiment": "negative",
                    "source": source_for(review_index),
                    "timestamp": timestamp_for(product, review_index),
                }
            )
            review_index += 1

    return reviews


def main() -> None:
    with CATALOG_PATH.open("r", encoding="utf-8") as fh:
        products = json.load(fh)["products"]

    reviews = build_reviews(products)

    with REVIEWS_PATH.open("w", encoding="utf-8") as fh:
        json.dump({"reviews": reviews}, fh, indent=2, ensure_ascii=True)
        fh.write("\n")


if __name__ == "__main__":
    main()
