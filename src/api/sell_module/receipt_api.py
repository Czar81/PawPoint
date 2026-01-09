from flask import jsonify, Blueprint
from src.extensions import db_receipt_manager
from src.utils import (
    APIException,
    role_required,
    validate_fields,
    register_error_handlers,
)

# Blueprint for all receipt-related routes
receipt_bp = Blueprint("receipt", __name__)

# Custom error handler registry
register_error_handlers(receipt_bp)


@receipt_bp.route("/create-receipt", methods=["POST"])
@role_required(["admin", "user"])
@validate_fields(required=["id_cart", "id_address", "id_payment"])
def create_receipt(id_cart, id_address, id_payment, id_user, role):
    """
    Create a new receipt for the authenticated user.
    Generates a receipt based on the cart, address and payment method.
    """
    id_receipt = db_receipt_manager.create_receipt(
        id_cart, id_address, id_payment, id_user=id_user
    )
    return jsonify(message="Receipt created", id=id_receipt), 201


@receipt_bp.route("/me/receipt", methods=["GET"])
@role_required(["admin", "user"])
@validate_fields(
    optional=[
        "id_receipt",
        "id_cart",
        "id_address",
        "id_payment",
        "state",
        "entry_date",
    ]
)
def get_receipt(role, **filters):
    """
    Retrieve all receipts of the authenticated user.
    Allows filtering by receipt attributes.
    """
    data = db_receipt_manager.get_data(**filters)
    return jsonify(data=data)


@receipt_bp.route("/me/receipt/<int:id_receipt>", methods=["GET"])
@role_required(["admin", "user"])
def get_single_receipt(id_receipt, id_user, role):
    """
    Retrieve a single receipt by its ID.
    """
    receipts = db_receipt_manager.get_data(id_receipt)
    return jsonify(receipt=receipts)


@receipt_bp.route("/me/receipt/<int:id_receipt>/return", methods=["POST"])
@role_required(["admin", "user"])
def return_receipt(id_user, role, id_receipt):
    """
    Return a receipt and revert its associated operations.
    """
    db_receipt_manager.return_receipt(id_receipt, id_user)
    return jsonify(message="Receipt returned"), 200
