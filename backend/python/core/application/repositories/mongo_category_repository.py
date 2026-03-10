from mongoengine.errors import DoesNotExist

from core.infrastructure.models.product_category_document import (
    ProductCategoryDocument,
)
from core.domain.product_category import ProductCategory


class MongoCategoryRepository:

    def create(self, category: ProductCategory) -> ProductCategory:
        doc = ProductCategoryDocument(
            title=category.title,
            description=category.description,
        )

        doc.save()

        category.id = str(doc.id)

        return category

    def get_by_title(self, title: str):
        try:
            doc = ProductCategoryDocument.objects.get(title__iexact=title)
        except DoesNotExist:
            return None

        return ProductCategory(
            id=str(doc.id),
            title=doc.title,
            description=doc.description,
        )

    def get_all(self):

        docs = ProductCategoryDocument.objects()

        categories = []

        for doc in docs:
            categories.append(
                ProductCategory(
                    id=str(doc.id),
                    title=doc.title,
                    description=doc.description,
                )
            )

        return categories

    def get_by_id(self, category_id: str):
        try:
            doc = ProductCategoryDocument.objects.get(id=category_id)
        except DoesNotExist:
            return None

        return ProductCategory(
            id=str(doc.id),
            title=doc.title,
            description=doc.description,
        )

    def update(
        self, category_id: str, category: ProductCategory
    ) -> ProductCategory | None:
        try:
            doc = ProductCategoryDocument.objects.get(id=category_id)
        except DoesNotExist:
            return None

        doc.title = category.title
        doc.description = category.description
        doc.save()

        return ProductCategory(
            id=str(doc.id),
            title=doc.title,
            description=doc.description,
        )

    def delete(self, category_id: str) -> bool:
        try:
            doc = ProductCategoryDocument.objects.get(id=category_id)
        except DoesNotExist:
            return False

        doc.delete()
        return True
