import pytest
from datetime import date


def test_create_receipt(client, base_cart_item_api):
    id_cart_item, token = base_cart_item_api
    expected_result = {"id": 1, "message": "Receipt created"}

    response_payment = client.post(
        "/me/payment",
        json={"type_data": "Card", "data": "fsdfsdafsfdsfadffs"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response_address = client.post(
        "/me/address",
        json={"location": "Test location"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.post(
        "/create-receipt",
        json={
            "id_cart": 1,
            "id_address": response_address.json["id"],
            "id_payment": response_payment.json["id"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json == expected_result


def test_get_all_receipt(client, base_receipt_api):
    id_receipt, token = base_receipt_api
    expected_result = {
        "data": [
            {
                "entry_date": str(date.today()),
                "id": 1,
                "id_address": 1,
                "id_cart": 1,
                "id_payment": 1,
                "state": "paid",
            },
        ],
    }

    response = client.get("/me/receipt", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json == expected_result


def test_get_filter_receipt(client, base_receipt_api):
    id_receipt, token = base_receipt_api
    expected_result = {
        "data": [
            {
                "entry_date": str(date.today()),
                "id": 1,
                "id_address": 1,
                "id_cart": 1,
                "id_payment": 1,
                "state": "paid",
            },
        ],
    }

    response = client.get(
        "/me/receipt",
        json={"entry_date": str(date.today())},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json == expected_result


def test_get_single_receipt(client, base_receipt_api):
    id_receipt, token = base_receipt_api
    expected_result = {
        "receipt": [
            {
                "entry_date": str(date.today()),
                "id": 1,
                "id_address": 1,
                "id_cart": 1,
                "id_payment": 1,
                "state": "paid",
            },
        ],
    }

    response = client.get(
        f"/me/receipt/{id_receipt}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json == expected_result


def test_return_receipt(client, base_receipt_api):
    id_receipt, token = base_receipt_api
    expected_return_result = {"message": "Receipt returned"}
    expected_get_result = {
        "receipt": [
            {
                "entry_date": str(date.today()),
                "id": 1,
                "id_address": 1,
                "id_cart": 1,
                "id_payment": 1,
                "state": "returned",
            },
        ],
    }

    response_return = client.post(
        f"/me/receipt/{id_receipt}/return", headers={"Authorization": f"Bearer {token}"}
    )
    response_get = client.get(
        f"/me/receipt/{id_receipt}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response_return.status_code == 200
    assert response_get.status_code == 200
    assert response_return.json == expected_return_result
    assert response_get.json == expected_get_result
