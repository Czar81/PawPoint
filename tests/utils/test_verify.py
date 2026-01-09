import pytest
from src.utils import role_required, validate_fields

def test_role_required_success(app, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    with app.test_request_context(headers=headers):
        @role_required(["admin"])
        def endpoint(id_user=None, role=None):
            return {"id_user": id_user, "role": role}

        result = endpoint()
        assert result["role"] == "admin"


def test_role_required_unauthorized(app, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}

    with app.test_request_context(headers=headers):
        @role_required(["admin"])
        def endpoint(id_user=None, role=None):
            return {"id_user": id_user, "role": role}

        response, status = endpoint()
        assert status == 403
        assert response.json["message"] == "Unauthorized"


def test_validate_fields_required(app, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    json_body = {"field1": "value1", "field2": "value2"}

    with app.test_request_context(headers=headers, json=json_body):
        @validate_fields(required=["field1", "field2"])
        def endpoint(field1=None, field2=None):
            return {"field1": field1, "field2": field2}

        result = endpoint()
        assert result == json_body