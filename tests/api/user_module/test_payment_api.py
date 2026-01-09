import pytest


def test_register_payment(client, get_token_user):
    token = get_token_user
    type_payment = "card"
    data = (
        "89fgd7u89d7g897df87fdg89u8y9fg7y78gyhfdghj8dfg6dfsg78dfgy83gt783y3589hdfg8dfgu"
    )
    expected_result = {"message": "Payment created", "id": 1}

    response = client.post(
        "/me/payment",
        json={"type_data": type_payment, "data": data},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json == expected_result


def test_get_payment(client, base_payment_api):
    id_payment, token = base_payment_api
    expected_result = {
        "data": [
            {
                "id": id_payment,
                "id_user": 1,
                "type_data": "card",
                "data": "fsdfsdafsadffsdf",
            },
        ]
    }

    response = client.get("/me/payment", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json == expected_result


def test_get_one_payment(client, base_payment_api):
    id_payment, token = base_payment_api
    expected_result = {
        "data": [
            {
                "id": id_payment,
                "id_user": 1,
                "type_data": "card",
                "data": "fsdfsdafsadffsdf",
            },
        ]
    }

    response = client.get(
        f"/me/payment/{id_payment}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json == expected_result


def test_delete_payment(client, base_payment_api):
    id_payment, token = base_payment_api
    expected_delete_result = {"message": "Payment deleted"}
    expected_get_result = {"data": "Not payments found"}

    response_delete = client.delete(
        f"/me/payment/{id_payment}",
        headers={"Authorization": f"Bearer {token}"},
    )
    response_get = client.get(
        "/me/payment", headers={"Authorization": f"Bearer {token}"}
    )

    assert response_delete.status_code == 200
    assert response_get.status_code == 200
    assert response_get.json == expected_get_result
    assert response_delete.json == expected_delete_result
