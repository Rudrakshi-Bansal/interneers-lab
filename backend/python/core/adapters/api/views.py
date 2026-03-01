import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.application.product_service import ProductService

service = ProductService()


# ==============================
# Response Helpers
# ==============================


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


# ==============================
# Serialization Helper
# ==============================


def product_to_dict(product):
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "price": product.price,
        "brand": product.brand,
        "quantity": product.quantity,
    }


# ==============================
# Collection Endpoints
# ==============================


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

        all_products = service.list_products()

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


# ==============================
# Detail Endpoints
# ==============================


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
