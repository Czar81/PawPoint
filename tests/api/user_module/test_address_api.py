import pytest


def test_register_address(client, get_token_user):
    token = get_token_user
    location = "Test location"
    expected_result = {"message": "Address created", "id": 1}

    response = client.post(
        "/me/address",
        json={"location": location},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json == expected_result


def test_get_address(client, base_address_api):
    id_address, token = base_address_api
    expected_result = {
        "data": [
            {"id": id_address, "id_user": 1, "location": "Test location"},
        ]
    }

    response = client.get("/me/address", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json == expected_result


def test_get_one_address(client, base_address_api):
    id_address, token = base_address_api
    expected_result = {
        "data": [
            {"id": id_address, "id_user": 1, "location": "Test location"},
        ]
    }

    response = client.get(
        f"/me/address/{id_address}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json == expected_result


def test_update_address(client, base_address_api):
    id_address, token = base_address_api
    new_location = "200 New Jersey Avenue NY"

    expected_update_result = {"message": "Address updated"}
    expected_get_result = {
        "data": [
            {"id": id_address, "id_user": 1, "location": "200 New Jersey Avenue NY"},
        ]
    }

    response_update = client.put(
        f"/me/address/{id_address}",
        json={"location": "200 New Jersey Avenue NY"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response_get = client.get(
        "/me/address", headers={"Authorization": f"Bearer {token}"}
    )
    assert response_update.status_code == 200
    assert response_get.status_code == 200
    assert response_get.json == expected_get_result
    assert response_update.json == expected_update_result


def test_delete_address(client, base_address_api):
    id_address, token = base_address_api

    expected_delete_result = {"message": "Address deleted"}
    expected_get_result = {"data": "Not address found"}

    response_delete = client.delete(
        f"/me/address/{id_address}",
        headers={"Authorization": f"Bearer {token}"},
    )
    response_get = client.get(
        "/me/address", headers={"Authorization": f"Bearer {token}"}
    )

    assert response_delete.status_code == 200
    assert response_get.status_code == 200
    assert response_get.json == expected_get_result
    assert response_delete.json == expected_delete_result
