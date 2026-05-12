from app import app
from app.views.users import json_response
from app.models import Product, ProductPermission, PermissionService, ProductRepository
from flask import request
from http import HTTPStatus


def check_permission_and_get_user(permission):
    from app.views.users import get_current_user
    user, error = get_current_user()
    if error:
        return None, error

    if not PermissionService.has_permission(user.role, permission):
        return None, json_response({"error": "Нет прав доступа"}, HTTPStatus.FORBIDDEN)

    return user, None


@app.get("/products")
def get_products():
    user, error = check_permission_and_get_user(ProductPermission.PRODUCTS_READ)
    if error:
        return error

    products = ProductRepository.get_all()
    return json_response(
        {"products": [p.to_dict() for p in products], "count": len(products)},
        HTTPStatus.OK,
    )


@app.get("/products/<int:product_id>")
def get_product(product_id):
    user, error = check_permission_and_get_user(ProductPermission.PRODUCTS_READ)
    if error:
        return error

    product = ProductRepository.find_by_id(product_id)
    if not product:
        return json_response(
            {"error": "Товар не найден"},
            HTTPStatus.NOT_FOUND
        )

    return json_response(
        {"message": "Вот ваш товар", "product": product.to_dict()},
        HTTPStatus.OK
    )


@app.post("/products")
def create_product():
    user, error = check_permission_and_get_user(ProductPermission.PRODUCTS_WRITE)
    if error:
        return error

    data = request.get_json()

    if not data:
        return json_response(
            {"error": "JSON обязателен"},
            HTTPStatus.BAD_REQUEST
        )

    name = data.get("name")
    price = data.get("price")
    quantity = data.get("quantity")

    if not name or not price or not quantity:
        return json_response(
            {"error": "Поля name, price, quantity обязательны"},
            HTTPStatus.BAD_REQUEST
        )

    all_products = ProductRepository.get_all()
    next_id = len(all_products) + 1

    new_product = Product(next_id, name, price, quantity)
    ProductRepository.save(new_product)

    return json_response(
        {"message": "Товар создан", "product": new_product.to_dict()},
        HTTPStatus.CREATED,
    )


@app.put("/products/<int:product_id>")
def update_product(product_id):
    user, error = check_permission_and_get_user(ProductPermission.PRODUCTS_WRITE)
    if error:
        return error

    product = ProductRepository.find_by_id(product_id)
    if not product:
        return json_response(
            {"error": "Товар не найден"},
            HTTPStatus.NOT_FOUND
        )

    data = request.get_json()

    if not data:
        return json_response(
            {"error": "JSON обязателен"},
            HTTPStatus.BAD_REQUEST
        )

    if "name" in data:
        product.name = data["name"]
    if "price" in data:
        product.price = data["price"]
    if "quantity" in data:
        product.quantity = data["quantity"]

    return json_response(
        {"message": "Товар успешно обновлен", "product": product.to_dict()},
        HTTPStatus.OK,
    )


@app.delete("/products/<int:product_id>")
def delete_product(product_id):
    user, error = check_permission_and_get_user(ProductPermission.PRODUCTS_DELETE)
    if error:
        return error

    product = ProductRepository.find_by_id(product_id)
    if not product:
        return json_response(
            {"error": "Товар не найден"},
            HTTPStatus.NOT_FOUND
        )

    ProductRepository.delete(product)

    return json_response({"message": "Товар удален"}, HTTPStatus.OK)