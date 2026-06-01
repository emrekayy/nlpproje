from app.repositories.product_repository import product_repository
from app.services.analysis_service import analysis_service


class ProductNotFoundError(Exception):
    def __init__(self, slug: str) -> None:
        super().__init__(f"Product '{slug}' was not found.")
        self.slug = slug


class CatalogService:
    def __init__(self) -> None:
        self._enriched_cache: dict[str, dict] = {}

    def _enrich_product(self, raw_product: dict) -> dict:
        slug = raw_product["slug"]
        if slug not in self._enriched_cache:
            intelligence = analysis_service.build_product_intelligence(raw_product)
            self._enriched_cache[slug] = {**raw_product, **intelligence}
        return self._enriched_cache[slug]

    def _resolve_raw(self, identifier: str) -> dict | None:
        normalized = identifier.strip().lower()
        for product in product_repository.list_products():
            if (
                product["slug"] == normalized
                or product["id"] == normalized
                or product["name"].lower() == normalized
            ):
                return product
        return None

    def list_products(self) -> list[dict]:
        return [self._enrich_product(p) for p in product_repository.list_products()]

    def get_product(self, identifier: str) -> dict:
        raw = self._resolve_raw(identifier)
        if raw is None:
            raise ProductNotFoundError(identifier)
        return self._enrich_product(raw)


catalog_service = CatalogService()
