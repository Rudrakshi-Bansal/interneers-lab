from typing import Optional

from core.domain.product_category import ProductCategory
from core.application.repositories.mongo_category_repository import (
    MongoCategoryRepository,
)


def _normalize_title(title: str) -> str:
    return " ".join(title.strip().split()).title()


class ProductCategoryService:

    def __init__(self):
        self.repository = MongoCategoryRepository()

    def create_category(self, data: dict) -> ProductCategory:
        self._validate(data)

        title = _normalize_title(data["title"])

        try:
            existing = self.repository.get_by_title(title)
        except Exception:
            raise ValueError("Error while checking existing categories")

        if existing:
            raise ValueError("Category with this title already exists")

        category = ProductCategory(
            id=None,
            title=title,
            description=data.get("description", ""),
        )
        return self.repository.create(category)

    def list_categories(self):
        return self.repository.get_all()

    def get_category(self, category_id: str) -> Optional[ProductCategory]:
        return self.repository.get_by_id(category_id)

    def update_category(
        self, category_id: str, data: dict
    ) -> Optional[ProductCategory]:

        existing = self.repository.get_by_id(category_id)
        if not existing:
            return None

        title = _normalize_title(data.get("title", existing.title))
        description = data.get("description", existing.description)

        self._validate({"title": title, "description": description})

        try:
            other = self.repository.get_by_title(title)
        except Exception:
            raise ValueError("Error while checking existing categories")

        if other and other.id != category_id:
            raise ValueError("Category with this title already exists")

        category = ProductCategory(
            id=category_id,
            title=title,
            description=description,
        )

        return self.repository.update(category_id, category)

    def delete_category(self, category_id: str) -> bool:
        return self.repository.delete(category_id)

    def _validate(self, data: dict) -> None:
        if "title" not in data:
            raise ValueError("title is required")

        if not isinstance(data["title"], str) or not data["title"].strip():
            raise ValueError("Title must be a non-empty string")
