import os

# =========================
# Ensure test mode BEFORE Django loads
# =========================
os.environ["PYTEST_RUNNING"] = "1"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_app.settings")

import django
django.setup()

import pytest
from django.test import Client
from core.application.repositories.mongo_category_repository import MongoCategoryRepository
from core.application.repositories.mongo_product_repository import MongoProductRepository
from scripts.seed_data import seed_test_data


# =========================
# Cleanup
# =========================

def _clear_db(product_repo, category_repo):
    
    for p in product_repo.get_all():
        try:
            product_repo.delete(p.id)
        except:
            pass

    for c in category_repo.get_all():
        try:
            category_repo.delete(c.id)
        except:
            pass

    from core.infrastructure.models.product_document import ProductDocument
    from core.infrastructure.models.product_category_document import ProductCategoryDocument

    ProductDocument.objects.delete()
    ProductCategoryDocument.objects.delete()

# =========================
# Fixtures
# =========================

@pytest.fixture
def db_repos():
    product_repo = MongoProductRepository()
    category_repo = MongoCategoryRepository()

    _clear_db(product_repo, category_repo)

    yield product_repo, category_repo

    _clear_db(product_repo, category_repo)


@pytest.fixture
def seeded_data(db_repos):
    product_repo, category_repo = db_repos
    data = seed_test_data(category_repo, product_repo)
    return data, product_repo, category_repo


@pytest.fixture
def api_client(db_repos):
    return Client()