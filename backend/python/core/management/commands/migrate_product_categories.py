from django.core.management.base import BaseCommand

from core.infrastructure.models.product_category_document import (
    ProductCategoryDocument,
)
from core.infrastructure.models.product_document import ProductDocument


def _norm_title(value: str) -> str:
    return value.strip().casefold()


class Command(BaseCommand):
    help = (
        "Migrate legacy Product.category string values to ProductCategory references."
    )

    def handle(self, *args, **options):

        self.stdout.write(self.style.NOTICE("Starting category migration..."))

        existing_categories = {
            _norm_title(cat.title): cat for cat in ProductCategoryDocument.objects()
        }

        updates = {}
        created_categories = []

        stats = {
            "products_scanned": 0,
            "products_migrated": 0,
            "categories_created": 0,
        }

        # RAW Mongo collection
        collection = ProductDocument._get_collection()

        for product in collection.find():

            stats["products_scanned"] += 1

            legacy = product.get("category")

            # Only migrate string categories
            if not isinstance(legacy, str):
                continue

            legacy = legacy.strip()

            if not legacy:
                continue

            key = _norm_title(legacy)

            category = existing_categories.get(key)

            if not category:
                category = ProductCategoryDocument(
                    title=legacy,
                    description="Migrated",
                )
                category.save()

                existing_categories[key] = category
                created_categories.append(category)
                stats["categories_created"] += 1

            updates.setdefault(str(category.id), []).append(product["_id"])

            stats["products_migrated"] += 1

        # Batch updates
        for category_id, product_ids in updates.items():

            category_doc = ProductCategoryDocument.objects.get(id=category_id)

            collection.update_many(
                {"_id": {"$in": product_ids}},
                {"$set": {"category": category_doc.id}},
            )

        self.stdout.write(self.style.SUCCESS("Migration completed"))

        self.stdout.write(f"Products scanned: {stats['products_scanned']}")
        self.stdout.write(f"Products migrated: {stats['products_migrated']}")
        self.stdout.write(f"Categories created: {stats['categories_created']}")

        if created_categories:
            self.stdout.write(self.style.NOTICE("New categories created:"))
            for cat in created_categories:
                self.stdout.write(f"  - {cat.title} (id={cat.id})")
        else:
            self.stdout.write("No new categories were created.")
