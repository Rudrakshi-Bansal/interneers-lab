import csv
import io
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.application.product_service import ProductService
from core.application.product_category_service import ProductCategoryService

service = ProductService()
category_service = ProductCategoryService()


# ======================
# Response Helpers
# ======================


def success_response(data, status=200):
    return JsonResponse(
        {"success": True, "data": data},
        status=status,
    )


def error_response(message, status=400):
    return JsonResponse(
        {"success": False, "error": message},
        status=status,
    )


# ======================
# Serialization Helper
# ======================


def product_to_dict(product):
    result = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "category_id": product.category_id,
        "price": product.price,
        "brand": product.brand,
        "quantity": product.quantity,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }
    return result


def category_to_dict(category):
    return {
        "id": category.id,
        "title": category.title,
        "description": category.description,
    }


# ======================================================
# Products Collection Endpoints (Create, List)
# ======================================================


@csrf_exempt
def products(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product = service.create_product(data)
            return success_response(
                product_to_dict(product),
                status=201,
            )

        except ValueError as exc:
            return error_response(str(exc), 400)

        except json.JSONDecodeError:
            return error_response("Invalid JSON", 400)

    if request.method == "GET":
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
        category_id = request.GET.get("category_id") or None

        all_products = service.list_products(category_id=category_id)

        start = (page - 1) * page_size
        end = start + page_size

        paginated = all_products[start:end]

        serialized = [product_to_dict(product) for product in paginated]

        return success_response(
            {
                "page": page,
                "page_size": page_size,
                "total": len(all_products),
                "results": serialized,
            }
        )

    return error_response("Method not allowed", 405)


# ======================================================
# Products Detail Endpoints (Get, Update, Delete)
# ======================================================


@csrf_exempt
def product_detail(request, product_id):
    if request.method == "GET":
        product = service.get_product(product_id)
        if not product:
            return error_response("Product not found", 404)

        return success_response(product_to_dict(product))

    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            updated = service.update_product(product_id, data)

            if not updated:
                return error_response("Product not found", 404)

            return success_response(product_to_dict(updated))

        except ValueError as exc:
            return error_response(str(exc), 400)

        except json.JSONDecodeError:
            return error_response("Invalid JSON", 400)

    if request.method == "DELETE":
        deleted = service.delete_product(product_id)

        if not deleted:
            return error_response("Product not found", 404)

        return success_response(
            {"message": "Product deleted"},
            status=200,
        )

    return error_response("Method not allowed", 405)


# ======================================================
# Products Bulk Endpoints (Create from CSV)
# ======================================================


@csrf_exempt
def products_bulk(request):
    if request.method != "POST":
        return error_response("Method not allowed", 405)

    file = request.FILES.get("file")
    if not file:
        return error_response("CSV file is required", 400)

    try:
        decoded_file = file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded_file))
        rows = list(reader)
    except (UnicodeDecodeError, csv.Error) as e:
        return error_response(f"Invalid CSV: {e}", 400)

    if not rows:
        return error_response("CSV has no data rows", 400)

    created = []

    for i, row in enumerate(rows, start=2):
        try:
            data = {
                "name": row.get("name", "").strip(),
                "description": row.get("description", "").strip(),
                "price": float(row.get("price", 0)),
                "brand": row.get("brand", "").strip(),
                "quantity": int(row.get("quantity", 0)),
            }

            if row.get("category_id", "").strip():
                data["category_id"] = row.get("category_id").strip()

            product = service.create_product(data)
            created.append(product_to_dict(product))

        except (ValueError, KeyError) as e:
            return error_response(f"Row {i}: {e}", 400)

    return success_response({"created": len(created), "products": created}, status=201)


# ======================================================
# Products Categories Endpoints (Add or Remove from Category)
# ======================================================


@csrf_exempt
def product_categories(request, product_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            category_id = data.get("category_id")
            if not category_id:
                return error_response("category_id is required", 400)
            updated = service.add_product_to_category(product_id, category_id)
            if not updated:
                return error_response("Product not found", 404)
            return success_response(product_to_dict(updated))
        except ValueError as exc:
            return error_response(str(exc), 400)
        except json.JSONDecodeError:
            return error_response("Invalid JSON", 400)
    return error_response("Method not allowed", 405)


@csrf_exempt
def product_category_detail(request, product_id, category_id):
    if request.method == "DELETE":
        try:
            updated = service.remove_product_from_category(product_id, category_id)
            if not updated:
                return error_response("Product not found", 404)
            return success_response(product_to_dict(updated))
        except ValueError as exc:
            return error_response(str(exc), 400)
    return error_response("Method not allowed", 405)


# ======================================================
# Categories Collection Endpoints (Create, List)
# ======================================================


@csrf_exempt
def categories(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            category = category_service.create_category(data)
            return success_response(
                category_to_dict(category),
                status=201,
            )
        except ValueError as exc:
            return error_response(str(exc), 400)
        except json.JSONDecodeError:
            return error_response("Invalid JSON", 400)

    if request.method == "GET":
        categories_list = category_service.list_categories()
        serialized = [category_to_dict(c) for c in categories_list]
        return success_response(serialized)

    return error_response("Method not allowed", 405)


# ======================================================
# Categories Detail Endpoints (Get, Update, Delete)
# ======================================================


@csrf_exempt
def category_detail(request, category_id):
    if request.method == "GET":
        category = category_service.get_category(category_id)
        if not category:
            return error_response("Category not found", 404)
        return success_response(category_to_dict(category))

    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            updated = category_service.update_category(category_id, data)
            if not updated:
                return error_response("Category not found", 404)
            return success_response(category_to_dict(updated))
        except ValueError as exc:
            return error_response(str(exc), 400)
        except json.JSONDecodeError:
            return error_response("Invalid JSON", 400)

    if request.method == "DELETE":
        deleted = category_service.delete_category(category_id)
        if not deleted:
            return error_response("Category not found", 404)
        return success_response(
            {"message": "Category deleted"},
            status=200,
        )

    return error_response("Method not allowed", 405)
