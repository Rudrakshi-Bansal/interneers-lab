from unittest.mock import Mock
import pytest

from core.application.product_category_service import (
    ProductCategoryService,
    _collapse_title_whitespace,
    _apply_title_casing,
    _normalize_title,
)
from core.domain.product_category import ProductCategory
from core.application.repositories.mongo_category_repository import MongoCategoryRepository


# =========================================================
# FIXTURE
# =========================================================

@pytest.fixture
def service_fixture():
    repo = Mock(spec=MongoCategoryRepository)
    service = ProductCategoryService()
    service.repository = repo
    return service


# =========================================================
# HELPER FUNCTIONS
# =========================================================

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("   hello   world   ", "hello world"),
        ("\ta\nb\tc", "a b c"),
        ("single", "single"),
    ],
)
def test_collapse_title_whitespace(raw, expected):
    assert _collapse_title_whitespace(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("hello world", "Hello World"),
        ("HELLO WORLD", "Hello World"),
        ("hElLo WoRlD", "Hello World"),
    ],
)
def test_apply_title_casing(raw, expected):
    assert _apply_title_casing(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("  hello   world  ", "Hello World"),
        ("HELLO WORLD", "Hello World"),
        ("hElLo   WoRlD", "Hello World"),
    ],
)
def test_normalize_title(raw, expected):
    assert _normalize_title(raw) == expected


# =========================================================
# CREATE
# =========================================================

def test_create_category_success(service_fixture):
    service_fixture.repository.get_by_title.return_value = None
    service_fixture.repository.create.side_effect = lambda c: c

    result = service_fixture.create_category(
        {"title": " gaming gear ", "description": "desc"}
    )

    assert result.title == "Gaming Gear"
    assert result.description == "desc"

    service_fixture.repository.get_by_title.assert_called_once_with("Gaming Gear")
    service_fixture.repository.create.assert_called_once()


def test_create_category_missing_title(service_fixture):
    with pytest.raises(ValueError):
        service_fixture.create_category({"description": "desc"})

    service_fixture.repository.get_by_title.assert_not_called()
    service_fixture.repository.create.assert_not_called()


@pytest.mark.parametrize("invalid_title", [None, "", " ", "   ", 123])
def test_create_category_invalid_title_param(service_fixture, invalid_title):
    with pytest.raises(ValueError):
        service_fixture.create_category({"title": invalid_title})

    service_fixture.repository.get_by_title.assert_not_called()
    service_fixture.repository.create.assert_not_called()


def test_create_category_duplicate(service_fixture):
    service_fixture.repository.get_by_title.return_value = ProductCategory(
        id="1", title="Gaming", description=""
    )

    with pytest.raises(ValueError):
        service_fixture.create_category({"title": "gaming"})


def test_create_category_repository_error(service_fixture):
    service_fixture.repository.get_by_title.side_effect = Exception()

    with pytest.raises(ValueError):
        service_fixture.create_category({"title": "Gaming"})


def test_create_category_default_description(service_fixture):
    service_fixture.repository.get_by_title.return_value = None
    service_fixture.repository.create.side_effect = lambda c: c

    result = service_fixture.create_category({"title": "Gaming"})

    assert result.description == ""


# =========================================================
# UPDATE
# =========================================================

def test_update_category_success(service_fixture):
    existing = ProductCategory(id="1", title="Old", description="Old")

    service_fixture.repository.get_by_id.return_value = existing
    service_fixture.repository.get_by_title.return_value = None
    service_fixture.repository.update.side_effect = lambda _id, c: c

    result = service_fixture.update_category(
        "1", {"title": " new title ", "description": "New"}
    )

    assert result.title == "New Title"
    assert result.description == "New"


def test_update_category_not_found(service_fixture):
    service_fixture.repository.get_by_id.return_value = None

    result = service_fixture.update_category("1", {"title": "New"})

    assert result is None
    service_fixture.repository.update.assert_not_called()


@pytest.mark.parametrize("invalid_title", [None, "", " ", 123])
def test_update_category_invalid_title_param(service_fixture, invalid_title):
    existing = ProductCategory(id="1", title="Old", description="")
    service_fixture.repository.get_by_id.return_value = existing

    with pytest.raises(ValueError):
        service_fixture.update_category("1", {"title": invalid_title})

    service_fixture.repository.update.assert_not_called()


def test_update_category_only_description(service_fixture):
    existing = ProductCategory(id="1", title="Old", description="Old")

    service_fixture.repository.get_by_id.return_value = existing
    service_fixture.repository.get_by_title.return_value = existing
    service_fixture.repository.update.side_effect = lambda _id, c: c

    result = service_fixture.update_category("1", {"description": "New"})

    assert result.title == "Old"
    assert result.description == "New"


def test_update_category_duplicate(service_fixture):
    existing = ProductCategory(id="1", title="Gaming", description="")
    other = ProductCategory(id="2", title="Gaming", description="")

    service_fixture.repository.get_by_id.return_value = existing
    service_fixture.repository.get_by_title.return_value = other

    with pytest.raises(ValueError):
        service_fixture.update_category("1", {"title": "gaming"})


def test_update_category_same_title_allowed(service_fixture):
    existing = ProductCategory(id="1", title="Gaming", description="")

    service_fixture.repository.get_by_id.return_value = existing
    service_fixture.repository.get_by_title.return_value = existing
    service_fixture.repository.update.side_effect = lambda _id, c: c

    result = service_fixture.update_category("1", {"title": "gaming"})

    assert result.title == "Gaming"


def test_update_category_repository_lookup_error(service_fixture):
    existing = ProductCategory(id="1", title="Old", description="")

    service_fixture.repository.get_by_id.return_value = existing
    service_fixture.repository.get_by_title.side_effect = Exception()

    with pytest.raises(ValueError):
        service_fixture.update_category("1", {"title": "New"})


def test_update_category_repository_update_error(service_fixture):
    existing = ProductCategory(id="1", title="Old", description="")

    service_fixture.repository.get_by_id.return_value = existing
    service_fixture.repository.get_by_title.return_value = None
    service_fixture.repository.update.side_effect = Exception()

    with pytest.raises(Exception):
        service_fixture.update_category("1", {"title": "New"})


# =========================================================
# DELETE / GET / LIST
# =========================================================

@pytest.mark.parametrize("repo_response", [True, False])
def test_delete_category_param(service_fixture, repo_response):
    service_fixture.repository.delete.return_value = repo_response

    result = service_fixture.delete_category("1")

    assert result == repo_response


def test_get_category(service_fixture):
    service_fixture.repository.get_by_id.return_value = "obj"

    result = service_fixture.get_category("1")

    assert result == "obj"


def test_list_categories(service_fixture):
    service_fixture.repository.get_all.return_value = ["a", "b"]

    result = service_fixture.list_categories()

    assert result == ["a", "b"]