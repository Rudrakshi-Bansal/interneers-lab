import unittest
from unittest.mock import Mock
import pytest

from core.application.product_service import ProductService
from core.domain.product import Product
from core.application.repositories.mongo_product_repository import MongoProductRepository
from core.application.repositories.mongo_category_repository import MongoCategoryRepository


# =========================================================
# FIXTURE (pytest)
# =========================================================

@pytest.fixture
def service_fixture():
    repo = Mock(spec=MongoProductRepository)
    category_repo = Mock(spec=MongoCategoryRepository)

    service = ProductService()
    service.repository = repo
    service.category_repository = category_repo

    return service


# =========================================================
# PARAMETRIZED VALIDATION TESTS
# =========================================================

@pytest.mark.parametrize("field", ["name", "brand", "price", "quantity"])
def test_validate_missing_required_fields(service_fixture, field):
    data = {
        "name": "Phone",
        "brand": "Apple",
        "price": 100,
        "quantity": 10,
    }
    data.pop(field)

    with pytest.raises(ValueError):
        service_fixture._validate(data)


@pytest.mark.parametrize("invalid", [None, "", "   ", 123])
def test_validate_invalid_name(service_fixture, invalid):
    with pytest.raises(ValueError):
        service_fixture._validate({
            "name": invalid,
            "brand": "Apple",
            "price": 100,
            "quantity": 10,
        })


@pytest.mark.parametrize("invalid", [None, "", "   ", 123])
def test_validate_invalid_brand(service_fixture, invalid):
    with pytest.raises(ValueError):
        service_fixture._validate({
            "name": "Phone",
            "brand": invalid,
            "price": 100,
            "quantity": 10,
        })


@pytest.mark.parametrize("invalid", [None, "100", "abc"])
def test_validate_non_numeric_price(service_fixture, invalid):
    with pytest.raises(ValueError):
        service_fixture._validate({
            "name": "Phone",
            "brand": "Apple",
            "price": invalid,
            "quantity": 10,
        })


def test_validate_negative_price(service_fixture):
    with pytest.raises(ValueError):
        service_fixture._validate({
            "name": "Phone",
            "brand": "Apple",
            "price": -10,
            "quantity": 10,
        })


@pytest.mark.parametrize("invalid", [None, 1.5, "10"])
def test_validate_non_integer_quantity(service_fixture, invalid):
    with pytest.raises(ValueError):
        service_fixture._validate({
            "name": "Phone",
            "brand": "Apple",
            "price": 100,
            "quantity": invalid,
        })


def test_validate_negative_quantity(service_fixture):
    with pytest.raises(ValueError):
        service_fixture._validate({
            "name": "Phone",
            "brand": "Apple",
            "price": 100,
            "quantity": -1,
        })


# =========================================================
# UNITTEST CLASS (SERVICE LOGIC)
# =========================================================

class TestProductService(unittest.TestCase):

    def setUp(self):
        self.repo = Mock(spec=MongoProductRepository)
        self.category_repo = Mock(spec=MongoCategoryRepository)

        self.service = ProductService()
        self.service.repository = self.repo
        self.service.category_repository = self.category_repo


    # ----------------------------
    # CREATE
    # ----------------------------

    def test_create_product_success(self):
        self.category_repo.get_by_id.return_value = True
        self.repo.create.side_effect = lambda p: p

        result = self.service.create_product({
            "name": "Phone",
            "brand": "Apple",
            "price": 100,
            "quantity": 5,
            "category_id": "cat-1"
        })

        self.assertEqual(result.name, "Phone")
        self.repo.create.assert_called_once()


    def test_create_product_missing_category_id(self):
        with self.assertRaisesRegex(ValueError, "category_id is required"):
            self.service.create_product({
                "name": "Phone",
                "brand": "Apple",
                "price": 100,
                "quantity": 5,
            })


    def test_create_product_category_not_found(self):
        self.category_repo.get_by_id.return_value = None

        with self.assertRaises(ValueError):
            self.service.create_product({
                "name": "Phone",
                "brand": "Apple",
                "price": 100,
                "quantity": 5,
                "category_id": "cat-1"
            })


    def test_create_product_default_description(self):
        self.category_repo.get_by_id.return_value = True
        self.repo.create.side_effect = lambda p: p

        result = self.service.create_product({
            "name": "Phone",
            "brand": "Apple",
            "price": 100,
            "quantity": 5,
            "category_id": "cat-1"
        })

        self.assertEqual(result.description, "")


    # ----------------------------
    # GET / LIST
    # ----------------------------

    def test_get_product(self):
        self.repo.get_by_id.return_value = "obj"

        result = self.service.get_product("1")

        self.assertEqual(result, "obj")


    def test_list_products_all(self):
        self.repo.get_all.return_value = ["a"]

        result = self.service.list_products()

        self.assertEqual(result, ["a"])


    def test_list_products_by_category(self):
        self.repo.get_by_category.return_value = ["filtered"]

        result = self.service.list_products("cat-1")

        self.assertEqual(result, ["filtered"])


    # ----------------------------
    # UPDATE
    # ----------------------------

    def test_update_product_success(self):
        existing = Product(
            id="1", name="Old", description="Old",
            category="", category_id="cat-1",
            price=100, brand="Apple", quantity=5
        )

        self.repo.get_by_id.return_value = existing
        self.category_repo.get_by_id.return_value = True
        self.repo.update.side_effect = lambda _id, p: p

        result = self.service.update_product("1", {"name": "New"})

        self.assertEqual(result.name, "New")


    def test_update_product_not_found(self):
        self.repo.get_by_id.return_value = None

        result = self.service.update_product("1", {})

        self.assertIsNone(result)


    def test_update_product_invalid_category(self):
        existing = Product(
            id="1", name="Old", description="Old",
            category="", category_id="cat-1",
            price=100, brand="Apple", quantity=5
        )

        self.repo.get_by_id.return_value = existing
        self.category_repo.get_by_id.return_value = None

        with self.assertRaises(ValueError):
            self.service.update_product("1", {"category_id": "invalid"})


    def test_update_product_blank_category_becomes_none(self):
        existing = Product(
            id="1", name="Old", description="Old",
            category="", category_id="cat-1",
            price=100, brand="Apple", quantity=5
        )

        self.repo.get_by_id.return_value = existing
        self.repo.update.side_effect = lambda _id, p: p

        result = self.service.update_product("1", {"category_id": ""})

        self.assertIsNone(result.category_id)


    # ----------------------------
    # CATEGORY OPERATIONS
    # ----------------------------

    def test_add_product_to_category(self):
        self.service.update_product = Mock(return_value="updated")

        result = self.service.add_product_to_category("1", "cat-1")

        self.assertEqual(result, "updated")


    def test_remove_product_from_category_success(self):
        product = Product(
            id="1", name="Phone", description="",
            category="", category_id="cat-1",
            price=100, brand="Apple", quantity=5
        )

        self.repo.get_by_id.return_value = product
        self.service.update_product = Mock(return_value="updated")

        result = self.service.remove_product_from_category("1", "cat-1")

        self.assertEqual(result, "updated")


    def test_remove_product_wrong_category(self):
        product = Product(
            id="1", name="Phone", description="",
            category="", category_id="cat-1",
            price=100, brand="Apple", quantity=5
        )

        self.repo.get_by_id.return_value = product

        with self.assertRaises(ValueError):
            self.service.remove_product_from_category("1", "cat-2")


    def test_remove_product_not_found(self):
        self.repo.get_by_id.return_value = None

        result = self.service.remove_product_from_category("1", "cat-1")

        self.assertIsNone(result)


    # ----------------------------
    # DELETE
    # ----------------------------

    def test_delete_product(self):
        self.repo.delete.return_value = True

        result = self.service.delete_product("1")

        self.assertTrue(result)