from flask import Blueprint, request, jsonify
from src.extensions import db_order_manager
from src.utils import (
    register_error_handlers,
)

# Blueprint for checkout order routes
order_bp = Blueprint("orders", __name__)

# Custom error handler registry
register_error_handlers(order_bp)


@order_bp.route("/api/orders", methods=["POST"])
def create_order():
    """
    Create a new checkout order.
    Receives customer info, products array, and total.
    Optionally links order to authenticated user.
    """
    data = request.get_json()

    if not data:
        return jsonify(error="No data provided"), 400

    customer = data.get("customer")
    products = data.get("products")
    total = data.get("total")

    if not customer or not products or total is None:
        return jsonify(error="Missing required fields: customer, products, total"), 400

    required_customer_fields = ["name", "email", "address"]
    for field in required_customer_fields:
        if not customer.get(field):
            return jsonify(error=f"Missing customer field: {field}"), 400

    if not isinstance(products, list) or len(products) == 0:
        return jsonify(error="products must be a non-empty array"), 400

    # Extract user ID from token if available (optional)
    id_user = None
    try:
        from src.utils.encoding import JWTManager
        from src.extensions import jwt_manager
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = jwt_manager.decode(token)
            id_user = payload.get("id")
    except Exception:
        pass

    try:
        id_order = db_order_manager.create_order(
            customer=customer,
            products=products,
            total=total,
            id_user=id_user,
        )
        return jsonify(message="Order registered", id=id_order), 201
    except Exception as e:
        return jsonify(error=str(e)), 500
