from flask import Blueprint, jsonify
from src.extensions import db_cart_item_manager
from src.utils import (
    role_required,
    validate_fields,
    register_error_handlers,
)

# Blueprint for all cart_items-related routes
cart_items_bp = Blueprint("cart_items", __name__)

# Custom error handler registry
register_error_handlers(cart_items_bp)


@cart_items_bp.route("/add-item", methods=["POST"])
@role_required(["admin", "user"])
@validate_fields(required=["id_cart", "id_product", "amount"])
def create_cart_item(id_cart, id_product, amount, id_user, role):
    """
    Add a product to a cart.
    Creates a new cart item with the specified amount.
    """
    id_cart_item = db_cart_item_manager.insert_data(
        id_cart, id_product, amount, id_user
    )
    return jsonify(id=id_cart_item, message="Item added"), 201


@cart_items_bp.route("/modify-amount-item/<int:id_cart_item>", methods=["PUT"])
@role_required(["admin", "user"])
@validate_fields(required=["id_cart_item", "amount"])
def update_cart_item(id_user, role, id_cart_item, amount):
    """
    Update the quantity of a cart item.
    """
    result = db_cart_item_manager.update_data(id_cart_item, amount, id_user)
    return jsonify(message="Amount updated"), 200


@cart_items_bp.route("/remove-item/<int:id_cart_item>", methods=["DELETE"])
@role_required(["admin", "user"])
def delete_cart_item(id_user, role, id_cart_item):
    """
    Remove an item from the cart.
    """
    db_cart_item_manager.delete_data(id_cart_item, id_user)
    return jsonify(message="Item deleted"), 200
