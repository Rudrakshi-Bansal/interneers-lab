import uuid
from typing import Dict

from core.domain.product import Product
from core.application.repositories.in_memory_product_repository import (
    InMemoryProductRepository,
)


class ProductService:
    def __init__(self):
        self.repository = InMemoryProductRepository()

    def create_product(self, data: Dict) -> Product:
        self._validate(data)

        product = Product(
            id=str(uuid.uuid4()),
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", ""),
            price=data["price"],
            brand=data["brand"],
            quantity=data["quantity"],
        )

        return self.repository.create(product)

    def get_product(self, product_id: str):
        return self.repository.get_by_id(product_id)

    def list_products(self):
        return self.repository.get_all()

    def update_product(self, product_id: str, data: Dict):
        existing = self.repository.get_by_id(product_id)
        if not existing:
            return None

        updated_data = {
            "name": data.get("name", existing.name),
            "description": data.get("description", existing.description),
            "category": data.get("category", existing.category),
            "price": data.get("price", existing.price),
            "brand": data.get("brand", existing.brand),
            "quantity": data.get("quantity", existing.quantity),
        }

        self._validate(updated_data)

        updated_product = Product(id=product_id, **updated_data)
        return self.repository.update(product_id, updated_product)

    def delete_product(self, product_id: str):
        return self.repository.delete(product_id)

    def _validate(self, data: Dict) -> None:
        required_fields = ["name", "brand", "price", "quantity"]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"{field} is required")

        if not isinstance(data["name"], str) or not data["name"].strip():
            raise ValueError("Name must be a non-empty string")

        if not isinstance(data["brand"], str) or not data["brand"].strip():
            raise ValueError("Brand must be a non-empty string")

        if not isinstance(data["price"], (int, float)):
            raise ValueError("Price must be a number")

        if data["price"] < 0:
            raise ValueError("Price cannot be negative")

        if not isinstance(data["quantity"], int):
            raise ValueError("Quantity must be an integer")

        if data["quantity"] < 0:
            raise ValueError("Quantity cannot be negative")
