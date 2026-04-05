from flask import request, jsonify
from functools import wraps


def role_required(allowed_roles):
    """
    Decorator to restrict endpoint access based on user roles.

    Validates JWT token from Authorization header, extracts user ID,
    retrieves the user's role from database, and verifies permissions.

    Injects into the endpoint:
        - id_user: authenticated user ID
        - role: authenticated user role

    :param allowed_roles: List of allowed roles (e.g. ["admin", "user"])
    """
    from src.extensions import db_user_manager, jwt_manager # Avoid circular import

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify(message="Missing token"), 401
            token = token.replace("Bearer ", "")
            id_decoded = jwt_manager.decode(token)
            role = db_user_manager.get_role_by_id(id_decoded["id"])
            if role not in allowed_roles:
                return jsonify(message="Unauthorized"), 403
            kwargs["id_user"] = id_decoded["id"]
            if role is not None:
                kwargs["role"] = role
            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_fields(required=None, optional=None):
    """
    Decorator to validate and extract JSON body fields.

    - Ensures required fields are present
    - Optionally extracts optional fields
    - Injects validated fields as keyword arguments

    :param required: List of required field names
    :param optional: List of optional field names
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            required_fields = required or []
            optional_fields = optional or []
            if not required_fields and not optional_fields:
                return func(*args, **kwargs)

            data = request.get_json(silent=True) or {}

            if required_fields:
                if not data:
                    return jsonify(message="Missing body"), 400

                missing = [f for f in required_fields if data.get(f) is None]
                if missing:
                    return (
                        jsonify(
                            message=f"Missing required fields: {', '.join(missing)}"
                        ),
                        400,
                    )

            for field in required_fields:
                kwargs[field] = data.get(field)

            for field in optional_fields:
                if data.get(field) is not None:
                    kwargs[field] = data.get(field)

            return func(*args, **kwargs)

        return wrapper

    return decorator
