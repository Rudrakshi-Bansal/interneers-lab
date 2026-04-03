import json
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

pytestmark = pytest.mark.integration


# =========================
# Helpers
# =========================

def _json(response):
    return json.loads(response.content.decode("utf-8"))


def _assert_success(res, status=200):
    assert res.status_code == status
    body = _json(res)
    assert "data" in body
    return body["data"]


# =========================================================
# CATEGORY CRUD
# =========================================================

def test_category_crud_flow(api_client):
    # Create
    data = _assert_success(api_client.post(
        "/api/categories/",
        data=json.dumps({"title": "Books", "description": "Reading"}),
        content_type="application/json",
    ), 201)

    cid = data["id"]

    # Read
    data = _assert_success(api_client.get(f"/api/categories/{cid}/"))
    assert data["title"] == "Books"

    # Update
    data = _assert_success(api_client.put(
        f"/api/categories/{cid}/",
        data=json.dumps({"title": "E-Books"}),
        content_type="application/json",
    ))
    assert data["title"] == "E-Books"

    # Delete
    _assert_success(api_client.delete(f"/api/categories/{cid}/"))

    # Verify deletion
    assert api_client.get(f"/api/categories/{cid}/").status_code == 404


# =========================================================
# PRODUCT CRUD
# =========================================================

def test_product_crud_flow(api_client):
    cid = _assert_success(api_client.post(
        "/api/categories/",
        data=json.dumps({"title": "Electronics"}),
        content_type="application/json",
    ), 201)["id"]

    product = _assert_success(api_client.post(
        "/api/products/",
        data=json.dumps({
            "name": "Mouse",
            "price": 25,
            "brand": "Logi",
            "quantity": 5,
            "category_id": cid,
        }),
        content_type="application/json",
    ), 201)

    pid = product["id"]

    # Read
    data = _assert_success(api_client.get(f"/api/products/{pid}/"))
    assert data["name"] == "Mouse"

    # Update
    data = _assert_success(api_client.put(
        f"/api/products/{pid}/",
        data=json.dumps({"price": 20}),
        content_type="application/json",
    ))
    assert data["price"] == 20

    # Delete
    _assert_success(api_client.delete(f"/api/products/{pid}/"))

    # Verify deletion
    assert api_client.get(f"/api/products/{pid}/").status_code == 404


# =========================================================
# LISTING + FILTERING
# =========================================================

def test_product_listing_and_filtering(api_client, seeded_data):
    data, _, _ = seeded_data

    # Listing
    res = api_client.get("/api/products/?page=1&page_size=10")
    payload = _assert_success(res)

    assert payload["total"] >= len(data["products"])
    assert len(payload["results"]) > 0

    # Filtering
    electronics = data["categories"][0]

    res = api_client.get(f"/api/products/?category_id={electronics.id}")
    results = _assert_success(res)["results"]

    assert results, "Filtering returned empty results unexpectedly"
    assert all(p["category_id"] == electronics.id for p in results)


# =========================================================
# CATEGORY ↔ PRODUCT RELATIONSHIP
# =========================================================

def test_product_category_link_and_remove(api_client, seeded_data):
    data, _, _ = seeded_data
    product = data["products"][0]

    # Create new category
    new_cid = _assert_success(api_client.post(
        "/api/categories/",
        data=json.dumps({"title": "NewCat"}),
        content_type="application/json",
    ), 201)["id"]

    # Link
    data = _assert_success(api_client.post(
        f"/api/products/{product.id}/categories/",
        data=json.dumps({"category_id": new_cid}),
        content_type="application/json",
    ))
    assert data["category_id"] == new_cid

    # Remove
    data = _assert_success(api_client.delete(
        f"/api/products/{product.id}/categories/{new_cid}/"
    ))

    assert "category_id" in data
    assert data["category_id"] is None


# =========================================================
# DB ↔ API CONSISTENCY
# =========================================================

def test_products_match_database(api_client, seeded_data):
    _, product_repo, _ = seeded_data

    db_products = {p.id: p for p in product_repo.get_all()}
    api_products = {
        p["id"]: p
        for p in _assert_success(api_client.get("/api/products/"))["results"]
    }

    assert db_products, "DB should not be empty"

    for pid, db_obj in db_products.items():
        assert pid in api_products, f"Missing product {pid} in API response"
        assert api_products[pid]["name"] == db_obj.name
        assert api_products[pid]["price"] == db_obj.price


# =========================================================
# BULK CSV UPLOAD
# =========================================================

def test_products_bulk_upload(api_client):
    cid = _assert_success(api_client.post(
        "/api/categories/",
        data=json.dumps({"title": "Bulk"}),
        content_type="application/json",
    ), 201)["id"]

    csv_data = (
        b"name,description,price,brand,quantity,category_id\n"
        + f"p1,Desc,10,Brand,1,{cid}\n".encode()
        + f"p2,Desc,20,Brand,2,{cid}\n".encode()
    )

    res = api_client.post(
        "/api/products/bulk/",
        {"file": SimpleUploadedFile("products.csv", csv_data, content_type="text/csv")},
    )

    data = _assert_success(res, 201)
    assert data["created"] == 2


# =========================================================
# FULL END-TO-END FLOW
# =========================================================

def test_full_flow(api_client):
    cid = _assert_success(api_client.post(
        "/api/categories/",
        data=json.dumps({"title": "Gaming"}),
        content_type="application/json",
    ), 201)["id"]

    pid = _assert_success(api_client.post(
        "/api/products/",
        data=json.dumps({
            "name": "Console",
            "price": 500,
            "brand": "Sony",
            "quantity": 5,
            "category_id": cid,
        }),
        content_type="application/json",
    ), 201)["id"]

    # Update
    _assert_success(api_client.put(
        f"/api/products/{pid}/",
        data=json.dumps({"price": 450}),
        content_type="application/json",
    ))

    # Delete chain
    _assert_success(api_client.delete(f"/api/products/{pid}/"))
    _assert_success(api_client.delete(f"/api/categories/{cid}/"))