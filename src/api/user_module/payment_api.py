from flask import jsonify, Blueprint
from src.extensions import db_payment_manager
from src.utils import (
    role_required,
    validate_fields,
    register_error_handlers,
)

# Create Payment blueprint
payment_bp = Blueprint("payment", __name__)

# Register centralized error handlers for this blueprint
register_error_handlers(payment_bp)


@payment_bp.route("/me/payment", methods=["POST"])
@role_required(["admin", "user"])
@validate_fields(required=["type_data", "data"])
def register_payment(id_user, role, type_data, data):
    """
    Register a new payment method for the authenticated user.
    """
    id_payment = db_payment_manager.insert_data(id_user, type_data, data)
    return jsonify(message="Payment created", id=id_payment), 201


@payment_bp.route("/me/payment", methods=["GET"])
@role_required(["admin", "user"])
@validate_fields(optional=["type_data"])
def get_payment(id_user, role, type_data: str | None = None):
    """
    Retrieve all payment methods of the authenticated user.
    Optionally filter by payment type.
    """
    payment = db_payment_manager.get_data(id_user=id_user, type_data=type_data)
    return jsonify(data=payment), 200


@payment_bp.route("/me/payment/<id_payment>", methods=["GET"])
@role_required(["admin", "user"])
def get_single_payment(id_payment, role, id_user):
    """
    Retrieve a single payment method by ID for the authenticated user.
    """
    payment = db_payment_manager.get_data(id=id_payment, id_user=id_user)
    return jsonify(data=payment), 200


@payment_bp.route("/me/payment/<id_payment>", methods=["DELETE"])
@role_required(["admin", "user"])
def delete_payment(id_user, role, id_payment):
    """
    Delete a payment method belonging to the authenticated user.
    """
    db_payment_manager.delete_data(id_payment, id_user)
    return jsonify(message="Payment deleted"), 200
