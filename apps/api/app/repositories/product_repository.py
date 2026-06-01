import json
from functools import cached_property

from app.core.config import settings


class ProductRepository:
    @cached_property
    def _catalog(self) -> list[dict]:
        with settings.seed_file.open("r", encoding="utf-8") as seed_file:
            return json.load(seed_file)["products"]

    def list_products(self) -> list[dict]:
        return self._catalog

    def get_product_by_slug(self, slug: str) -> dict | None:
        for product in self._catalog:
            if product["slug"] == slug:
                return product
        return None


product_repository = ProductRepository()
