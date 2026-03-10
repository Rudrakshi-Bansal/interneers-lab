from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    id: str
    name: str
    description: str
    category: str
    price: float
    brand: str
    quantity: int
    category_id: Optional[str] = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
