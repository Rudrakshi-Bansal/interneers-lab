from typing import Dict, List
from core.domain.product import Product


class InMemoryProductRepository:
    def __init__(self):
        self.products: Dict[str, Product] = {}

    def create(self, product: Product) -> Product:
        self.products[product.id] = product
        return product

    def get_by_id(self, product_id: str) -> Product | None:
        return self.products.get(product_id)

    def get_all(self) -> List[Product]:
        return list(self.products.values())

    def update(self, product_id: str, updated_product: Product) -> Product | None:
        if product_id not in self.products:
            return None
        self.products[product_id] = updated_product
        return updated_product

    def delete(self, product_id: str) -> bool:
        if product_id in self.products:
            del self.products[product_id]
            return True
        return False
