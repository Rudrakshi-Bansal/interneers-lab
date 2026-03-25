import unittest
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
# PARAMETRIZED TESTS (pytest style - OUTSIDE class)
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


@pytest.mark.parametrize("invalid_title", [None, "", " ", "   ", 123])
def test_create_category_invalid_title_param(service_fixture, invalid_title):
    with pytest.raises(ValueError):
        service_fixture.create_category({"title": invalid_title})


@pytest.mark.parametrize("invalid_title", [None, "", " ", 123])
def test_update_category_invalid_title_param(service_fixture, invalid_title):
    existing = ProductCategory(id="1", title="Old", description="")
    service_fixture.repository.get_by_id.return_value = existing

    with pytest.raises(ValueError):
        service_fixture.update_category("1", {"title": invalid_title})


@pytest.mark.parametrize("repo_response", [True, False])
def test_delete_category_param(service_fixture, repo_response):
    service_fixture.repository.delete.return_value = repo_response

    result = service_fixture.delete_category("1")

    assert result == repo_response


# =========================================================
# FIXTURE (pytest)
# =========================================================

@pytest.fixture
def service_fixture():
    repo = Mock(spec=MongoCategoryRepository)
    service = ProductCategoryService()
    service.repository = repo
    return service


# =========================================================
# UNITTEST CLASS (core service logic)
# =========================================================

class TestProductCategoryService(unittest.TestCase):

    def setUp(self):
        self.repo = Mock(spec=MongoCategoryRepository)
        self.service = ProductCategoryService()
        self.service.repository = self.repo


    # ----------------------------
    # CREATE
    # ----------------------------

    def test_create_category_success(self):
        self.repo.get_by_title.return_value = None
        self.repo.create.side_effect = lambda c: c

        result = self.service.create_category(
            {"title": " gaming gear ", "description": "desc"}
        )

        self.assertEqual(result.title, "Gaming Gear")
        self.assertEqual(result.description, "desc")

        self.repo.get_by_title.assert_called_once_with("Gaming Gear")
        self.repo.create.assert_called_once()


    def test_create_category_missing_title(self):
        with self.assertRaisesRegex(ValueError, "title is required"):
            self.service.create_category({"description": "desc"})


    def test_create_category_duplicate(self):
        self.repo.get_by_title.return_value = ProductCategory(
            id="1", title="Gaming", description=""
        )

        with self.assertRaises(ValueError):
            self.service.create_category({"title": "gaming"})


    def test_create_category_repository_error(self):
        self.repo.get_by_title.side_effect = Exception()

        with self.assertRaisesRegex(ValueError, "Error while checking existing categories"):
            self.service.create_category({"title": "Gaming"})


    def test_create_category_default_description(self):
        self.repo.get_by_title.return_value = None
        self.repo.create.side_effect = lambda c: c

        result = self.service.create_category({"title": "Gaming"})

        self.assertEqual(result.description, "")


    # ----------------------------
    # UPDATE
    # ----------------------------

    def test_update_category_success(self):
        existing = ProductCategory(id="1", title="Old", description="Old")

        self.repo.get_by_id.return_value = existing
        self.repo.get_by_title.return_value = None
        self.repo.update.side_effect = lambda _id, c: c

        result = self.service.update_category(
            "1", {"title": " new title ", "description": "New"}
        )

        self.assertEqual(result.title, "New Title")
        self.assertEqual(result.description, "New")


    def test_update_category_not_found(self):
        self.repo.get_by_id.return_value = None

        result = self.service.update_category("1", {"title": "New"})

        self.assertIsNone(result)
        self.repo.update.assert_not_called()


    def test_update_category_only_description(self):
        existing = ProductCategory(id="1", title="Old", description="Old")

        self.repo.get_by_id.return_value = existing
        self.repo.get_by_title.return_value = existing
        self.repo.update.side_effect = lambda _id, c: c

        result = self.service.update_category("1", {"description": "New"})

        self.assertEqual(result.title, "Old")
        self.assertEqual(result.description, "New")


    def test_update_category_duplicate(self):
        existing = ProductCategory(id="1", title="Gaming", description="")
        other = ProductCategory(id="2", title="Gaming", description="")

        self.repo.get_by_id.return_value = existing
        self.repo.get_by_title.return_value = other

        with self.assertRaises(ValueError):
            self.service.update_category("1", {"title": "gaming"})


    def test_update_category_same_title_allowed(self):
        existing = ProductCategory(id="1", title="Gaming", description="")

        self.repo.get_by_id.return_value = existing
        self.repo.get_by_title.return_value = existing
        self.repo.update.side_effect = lambda _id, c: c

        result = self.service.update_category("1", {"title": "gaming"})

        self.assertEqual(result.title, "Gaming")


    def test_update_category_repository_lookup_error(self):
        existing = ProductCategory(id="1", title="Old", description="")

        self.repo.get_by_id.return_value = existing
        self.repo.get_by_title.side_effect = Exception()

        with self.assertRaisesRegex(ValueError, "Error while checking existing categories"):
            self.service.update_category("1", {"title": "New"})


    def test_update_category_repository_update_error(self):
        existing = ProductCategory(id="1", title="Old", description="")

        self.repo.get_by_id.return_value = existing
        self.repo.get_by_title.return_value = None
        self.repo.update.side_effect = Exception()

        with self.assertRaises(Exception):
            self.service.update_category("1", {"title": "New"})


    # ----------------------------
    # DELETE / GET / LIST
    # ----------------------------

    def test_delete_category(self):
        self.repo.delete.return_value = True

        result = self.service.delete_category("1")

        self.assertTrue(result)
        self.repo.delete.assert_called_once_with("1")


    def test_get_category(self):
        self.repo.get_by_id.return_value = "obj"

        result = self.service.get_category("1")

        self.assertEqual(result, "obj")


    def test_list_categories(self):
        self.repo.get_all.return_value = ["a", "b"]

        result = self.service.list_categories()

        self.assertEqual(result, ["a", "b"])