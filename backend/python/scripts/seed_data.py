from core.domain.product import Product
from core.domain.product_category import ProductCategory


def seed_test_data(category_repo, product_repo):
    """
    Seed minimal deterministic data for testing.
    Returns created entities for direct use in tests.
    """

    # Create categories
    electronics = category_repo.create(
        ProductCategory(id=None, title="Electronics", description="Devices")
    )
    fashion = category_repo.create(
        ProductCategory(id=None, title="Fashion", description="Clothing")
    )

    # Create products
    p1 = product_repo.create(
        Product(
            id=None,
            name="Phone",
            description="Smartphone",
            category="",
            category_id=electronics.id,
            price=500,
            brand="Apple",
            quantity=10,
        )
    )

    p2 = product_repo.create(
        Product(
            id=None,
            name="Laptop",
            description="Gaming Laptop",
            category="",
            category_id=electronics.id,
            price=1200,
            brand="Dell",
            quantity=5,
        )
    )

    p3 = product_repo.create(
        Product(
            id=None,
            name="T-Shirt",
            description="Cotton",
            category="",
            category_id=fashion.id,
            price=20,
            brand="H&M",
            quantity=50,
        )
    )

    return {
        "categories": [electronics, fashion],
        "products": [p1, p2, p3],
    }