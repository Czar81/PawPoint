from flask import jsonify, Blueprint
from src.extensions import db_product_manager, cache_manager
from src.utils import (
    role_required,
    validate_fields,
    generate_cache_based_filters,
    generate_cache_key,
    register_error_handlers,
    get_cache_if_exist,
)

# Blueprint for all cart_items-related routes
product_bp = Blueprint("product", __name__)

# Custom error handler registry
register_error_handlers(product_bp)


@product_bp.route("/products", methods=["POST"])
@role_required(["admin"])
@validate_fields(required=["sku", "name", "price", "amount"])
def register_product(id_user, role, sku, name, price, amount):
    """
    Create a new product.
    Only administrators are allowed to create products.
    """
    id_product = db_product_manager.insert_data(sku, name, price, amount)

    # Clear product-related cache
    cache_manager.delete_data_with_pattern("getProducts:")
    return jsonify({"id": id_product, "message": "Product created"}), 201


@product_bp.route("/products", methods=["GET"])
@validate_fields(optional=["id_product", "sku", "name", "price", "amount"])
def get_products(**filters):
    """
    Create a new product.
    Only administrators are allowed to create products.
    """
    key = generate_cache_based_filters("getProducts", filters)
    result, code_status = get_cache_if_exist(
        key, cache_manager, db_product_manager, **filters
    )
    return jsonify({"products": result}), code_status


@product_bp.route("/products/<int:id_product>", methods=["GET"])
def get_single_product(id_product):
    """
    Retrieve a single product by its ID.
    """
    id_product = id_product
    key = generate_cache_key("getProduct", id=id_product)
    result, code_status = get_cache_if_exist(
        key, cache_manager, db_product_manager, id=id_product
    )
    return jsonify({"product": result}), code_status


@product_bp.route("/products/<int:id_product>", methods=["PUT"])
@role_required(["admin"])
@validate_fields(optional=["sku", "name", "price", "amount"])
def update_product(id_user, role, id_product, **filters):
    """
    Update an existing product.
    Only administrators can modify product data.
    """
    id_product = id_product
    filters["id_product"] = id_product
    key = generate_cache_key("getProduct", id=id_product)
    db_product_manager.update_data(**filters)
    cache_manager.delete_data(key)
    cache_manager.delete_data_with_pattern("getProducts:")
    return jsonify({"message": "Product Updated"}), 200


@product_bp.route("/products/<int:id_product>", methods=["DELETE"])
@role_required(["admin"])
def delete_product(id_user, role, id_product):
    """
    Delete a product by its ID.
    Only administrators can delete products.
    """
    id_product = id_product
    key = generate_cache_key("getProduct", id=id_product)
    db_product_manager.delete_data(id_product)
    cache_manager.delete_data(key)
    cache_manager.delete_data_with_pattern("getProducts:")
    return jsonify({"message": "Product Deleted"}), 200
