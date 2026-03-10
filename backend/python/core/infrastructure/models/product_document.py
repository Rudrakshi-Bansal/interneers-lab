from mongoengine import (
    Document,
    StringField,
    FloatField,
    IntField,
    DateTimeField,
)
from datetime import datetime
from mongoengine import ReferenceField
from core.infrastructure.models.product_category_document import ProductCategoryDocument


class ProductDocument(Document):
    meta = {"collection": "products"}

    id = StringField(primary_key=True)
    name = StringField(required=True)
    description = StringField()
    category = ReferenceField(ProductCategoryDocument, required=False)
    price = FloatField(required=True, min_value=0)
    brand = StringField(required=True)
    quantity = IntField(required=True, min_value=0)

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
