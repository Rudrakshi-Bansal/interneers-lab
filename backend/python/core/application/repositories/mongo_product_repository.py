from typing import List, Optional
from core.domain.product import Product
from core.infrastructure.models.product_document import ProductDocument


class MongoProductRepository:
    def create(self, product: Product) -> Product:
        doc = ProductDocument(
            id=product.id,
            name=product.name,
            description=product.description,
            category=product.category,
            price=product.price,
            brand=product.brand,
            quantity=product.quantity,
        )
        doc.save()
        return product

    def get_by_id(self, product_id: str) -> Optional[Product]:
        doc = ProductDocument.objects(id=product_id).first()
        if not doc:
            return None
        return self._to_domain(doc)

    def get_all(self) -> List[Product]:
        docs = ProductDocument.objects()
        return [self._to_domain(doc) for doc in docs]

    def update(self, product_id: str, product: Product) -> Optional[Product]:
        doc = ProductDocument.objects(id=product_id).first()
        if not doc:
            return None

        doc.name = product.name
        doc.description = product.description
        doc.category = product.category
        doc.price = product.price
        doc.brand = product.brand
        doc.quantity = product.quantity
        doc.save()

        return product

    def delete(self, product_id: str) -> bool:
        doc = ProductDocument.objects(id=product_id).first()
        if not doc:
            return False
        doc.delete()
        return True

    def _to_domain(self, doc: ProductDocument) -> Product:
        return Product(
            id=str(doc.id),
            name=doc.name,
            description=doc.description,
            category=doc.category,
            price=doc.price,
            brand=doc.brand,
            quantity=doc.quantity,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )