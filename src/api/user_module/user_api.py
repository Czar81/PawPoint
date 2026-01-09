from flask import jsonify, Blueprint, request
from src.extensions import db_user_manager, db_cart_manager, jwt_manager
from src.utils import (
    role_required,
    validate_fields,
    register_error_handlers,
)
from os import getenv

# Create User blueprint
user_bp = Blueprint("user", __name__)

# Create User blueprint
register_error_handlers(user_bp)


@user_bp.route("/register", methods=["POST"])
@validate_fields(required=["username", "password"])
def register(username, password):
    """
    Register a new user.
    If a valid X-ADMIN-TOKEN is provided, the user is created as admin.
    Automatically creates a cart and returns a JWT token.
    """
    role = None
    x_admin_token = request.headers.get("X-ADMIN-TOKEN")
    if x_admin_token == getenv("ADMIN_BOOTSTRAP_TOKEN"):
        role = "admin"

    id_user = db_user_manager.insert_data(username, password, role=role)
    id_cart = db_cart_manager.insert_data(id_user)
    token = jwt_manager.encode({"id": id_user})

    return jsonify(token=token, id_cart=id_cart), 201


@user_bp.route("/login", methods=["POST"])
@validate_fields(required=["username", "password"])
def login(username, password):
    """
    Authenticate a user and return a JWT token.
    """
    id_user = db_user_manager.get_user(username, password)
    if id_user is None:
        return jsonify(message="User not found, register first"), 404
    token = jwt_manager.encode({"id": id_user})
    return jsonify(token=token), 200


@user_bp.route("/me", methods=["GET"])
@role_required(["user", "admin"])
def me(id_user, role):
    """
    Retrieve the authenticated user's profile.
    """
    myself = db_user_manager.get_data(id_user)
    return jsonify(user=myself), 200


@user_bp.route("/users", methods=["GET"])
@role_required(["admin"])
def get_users(id_user, role):
    """
    Retrieve all users (admin only).
    """
    users = db_user_manager.get_data()
    return jsonify(user=users), 200


@user_bp.route("/me", methods=["PUT"])
@role_required(["admin", "user"])
@validate_fields(optional=["username", "password"])
def update_profile(
    id_user,
    role,
    username: str | None = None,
    password: str | None = None,
    new_role: str | None = None,
):
    """
    Update the authenticated user's profile.
    Allows updating username and/or password.
    """
    db_user_manager.update_data(id_user, username, password)
    return jsonify({"message": "User updated"}), 200


@user_bp.route("/me", methods=["DELETE"])
@role_required(["admin", "user"])
def delete_profile(id_user, role):
    """
    Delete the authenticated user's account.
    """
    db_user_manager.delete_data(id_user)
    return jsonify(message="User deleted"), 200
