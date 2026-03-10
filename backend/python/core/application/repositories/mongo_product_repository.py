from typing import List, Optional

from core.domain.product import Product
from core.infrastructure.models.product_document import ProductDocument
from core.infrastructure.models.product_category_document import ProductCategoryDocument


class MongoProductRepository:
    def create(self, product: Product) -> Product:
        category_ref = None
        if product.category_id:
            category_ref = ProductCategoryDocument.objects(
                id=product.category_id
            ).first()

        doc = ProductDocument(
            id=product.id,
            name=product.name,
            description=product.description,
            category=category_ref,
            price=product.price,
            brand=product.brand,
            quantity=product.quantity,
        )
        doc.save()
        return self._to_domain(doc)

    def get_by_id(self, product_id: str) -> Optional[Product]:
        doc = ProductDocument.objects(id=product_id).first()
        if not doc:
            return None
        return self._to_domain(doc)

    def get_all(self) -> List[Product]:
        docs = ProductDocument.objects()
        return [self._to_domain(doc) for doc in docs]

    def get_by_category(self, category_id: str) -> List[Product]:
        category_ref = ProductCategoryDocument.objects(id=category_id).first()
        if not category_ref:
            return []
        docs = ProductDocument.objects(category=category_ref)
        return [self._to_domain(doc) for doc in docs]

    def update(self, product_id: str, product: Product) -> Optional[Product]:
        doc = ProductDocument.objects(id=product_id).first()
        if not doc:
            return None

        category_ref = None
        if product.category_id:
            category_ref = ProductCategoryDocument.objects(
                id=product.category_id
            ).first()

        doc.name = product.name
        doc.description = product.description
        doc.category = category_ref
        doc.price = product.price
        doc.brand = product.brand
        doc.quantity = product.quantity
        doc.save()

        return self._to_domain(doc)

    def delete(self, product_id: str) -> bool:
        doc = ProductDocument.objects(id=product_id).first()
        if not doc:
            return False
        doc.delete()
        return True

    def _to_domain(self, doc: ProductDocument) -> Product:
        category_id = str(doc.category.id) if doc.category else None
        category_title = doc.category.title if doc.category else ""
        return Product(
            id=str(doc.id),
            name=doc.name,
            description=doc.description,
            category=category_title,
            category_id=category_id,
            price=doc.price,
            brand=doc.brand,
            quantity=doc.quantity,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
