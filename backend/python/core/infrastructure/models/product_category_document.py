from mongoengine import Document, StringField


class ProductCategoryDocument(Document):

    title = StringField(required=True, unique=True)
    description = StringField()

    meta = {"collection": "product_categories"}
