from dataclasses import dataclass
from typing import Optional


@dataclass
class ProductCategory:
    id: Optional[str]
    title: str
    description: str
