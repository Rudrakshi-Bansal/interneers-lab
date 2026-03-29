from unittest.mock import Mock
import pytest

from core.application.product_service import ProductService
from core.domain.product import Product
from core.application.repositories.mongo_product_repository import MongoProductRepository
from core.application.repositories.mongo_category_repository import MongoCategoryRepository


# =========================================================
# FIXTURE
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
# VALIDATION 
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
# CREATE
# =========================================================

def test_create_product_success(service_fixture):
    service_fixture.category_repository.get_by_id.return_value = True
    service_fixture.repository.create.side_effect = lambda p: p

    result = service_fixture.create_product({
        "name": "Phone",
        "brand": "Apple",
        "price": 100,
        "quantity": 5,
        "category_id": "cat-1"
    })

    assert result.name == "Phone"
    service_fixture.repository.create.assert_called_once()


def test_create_product_missing_category_id(service_fixture):
    with pytest.raises(ValueError):
        service_fixture.create_product({
            "name": "Phone",
            "brand": "Apple",
            "price": 100,
            "quantity": 5,
        })

    service_fixture.repository.create.assert_not_called()
    service_fixture.category_repository.get_by_id.assert_not_called()


def test_create_product_category_not_found(service_fixture):
    service_fixture.category_repository.get_by_id.return_value = None

    with pytest.raises(ValueError):
        service_fixture.create_product({
            "name": "Phone",
            "brand": "Apple",
            "price": 100,
            "quantity": 5,
            "category_id": "cat-1"
        })

    service_fixture.repository.create.assert_not_called()


def test_create_product_default_description(service_fixture):
    service_fixture.category_repository.get_by_id.return_value = True
    service_fixture.repository.create.side_effect = lambda p: p

    result = service_fixture.create_product({
        "name": "Phone",
        "brand": "Apple",
        "price": 100,
        "quantity": 5,
        "category_id": "cat-1"
    })

    assert result.description == ""


# =========================================================
# GET / LIST
# =========================================================

def test_get_product(service_fixture):
    service_fixture.repository.get_by_id.return_value = "obj"

    result = service_fixture.get_product("1")

    assert result == "obj"


def test_list_products_all(service_fixture):
    service_fixture.repository.get_all.return_value = ["a"]

    result = service_fixture.list_products()

    assert result == ["a"]


def test_list_products_by_category(service_fixture):
    service_fixture.repository.get_by_category.return_value = ["filtered"]

    result = service_fixture.list_products("cat-1")

    assert result == ["filtered"]


# =========================================================
# UPDATE
# =========================================================

def test_update_product_success(service_fixture):
    existing = Product(
        id="1", name="Old", description="Old",
        category="", category_id="cat-1",
        price=100, brand="Apple", quantity=5
    )

    service_fixture.repository.get_by_id.return_value = existing
    service_fixture.category_repository.get_by_id.return_value = True
    service_fixture.repository.update.side_effect = lambda _id, p: p

    result = service_fixture.update_product("1", {"name": "New"})

    assert result.name == "New"


def test_update_product_not_found(service_fixture):
    service_fixture.repository.get_by_id.return_value = None

    result = service_fixture.update_product("1", {})

    assert result is None


def test_update_product_invalid_category(service_fixture):
    existing = Product(
        id="1", name="Old", description="Old",
        category="", category_id="cat-1",
        price=100, brand="Apple", quantity=5
    )

    service_fixture.repository.get_by_id.return_value = existing
    service_fixture.category_repository.get_by_id.return_value = None

    with pytest.raises(ValueError):
        service_fixture.update_product("1", {"category_id": "invalid"})

    service_fixture.repository.update.assert_not_called()


def test_update_product_blank_category_becomes_none(service_fixture):
    existing = Product(
        id="1", name="Old", description="Old",
        category="", category_id="cat-1",
        price=100, brand="Apple", quantity=5
    )

    service_fixture.repository.get_by_id.return_value = existing
    service_fixture.repository.update.side_effect = lambda _id, p: p

    result = service_fixture.update_product("1", {"category_id": ""})

    assert result.category_id is None


# =========================================================
# CATEGORY OPERATIONS
# =========================================================

def test_add_product_to_category(service_fixture):
    service_fixture.update_product = Mock(return_value="updated")

    result = service_fixture.add_product_to_category("1", "cat-1")

    assert result == "updated"


def test_remove_product_from_category_success(service_fixture):
    product = Product(
        id="1", name="Phone", description="",
        category="", category_id="cat-1",
        price=100, brand="Apple", quantity=5
    )

    service_fixture.repository.get_by_id.return_value = product
    service_fixture.update_product = Mock(return_value="updated")

    result = service_fixture.remove_product_from_category("1", "cat-1")

    assert result == "updated"


def test_remove_product_wrong_category(service_fixture):
    product = Product(
        id="1", name="Phone", description="",
        category="", category_id="cat-1",
        price=100, brand="Apple", quantity=5
    )

    service_fixture.repository.get_by_id.return_value = product

    service_fixture.update_product = Mock()

    with pytest.raises(ValueError):
        service_fixture.remove_product_from_category("1", "cat-2")

    service_fixture.update_product.assert_not_called()


def test_remove_product_not_found(service_fixture):
    service_fixture.repository.get_by_id.return_value = None

    result = service_fixture.remove_product_from_category("1", "cat-1")

    assert result is None


# =========================================================
# DELETE
# =========================================================

def test_delete_product(service_fixture):
    service_fixture.repository.delete.return_value = True

    result = service_fixture.delete_product("1")

    assert result is True