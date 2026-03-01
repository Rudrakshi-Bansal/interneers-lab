from dataclasses import dataclass


@dataclass
class Product:
    id: str
    name: str
    description: str
    category: str
    price: float
    brand: str
    quantity: int
