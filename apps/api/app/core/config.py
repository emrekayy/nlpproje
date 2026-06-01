from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Product Intelligence Assistant API"
    api_prefix: str = "/api"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    cors_origins: list[str] = field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
    seed_file: Path = field(
        default_factory=lambda: (
            Path(__file__).resolve().parents[4] / "data" / "seeds" / "iphone_catalog.json"
        )
    )
    reviews_seed_file: Path = field(
        default_factory=lambda: (
            Path(__file__).resolve().parents[4] / "data" / "seeds" / "iphone_reviews.json"
        )
    )
    raw_reviews_dir: Path = field(
        default_factory=lambda: (
            Path(__file__).resolve().parents[4] / "data" / "raw" / "reviews"
        )
    )
    processed_reviews_dir: Path = field(
        default_factory=lambda: (
            Path(__file__).resolve().parents[4] / "data" / "processed" / "reviews"
        )
    )
    processed_real_reviews_file: Path = field(
        default_factory=lambda: (
            Path(__file__).resolve().parents[4]
            / "data"
            / "processed"
            / "reviews"
            / "real_reviews.json"
        )
    )


settings = Settings()
