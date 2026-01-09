import pytest


def test_register_cart(client, get_token_user):
    token = get_token_user
    expected_result = {"id": 2, "message": "Cart created"}

    response = client.post(
        "/me/carts",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json == expected_result


def test_get_all_carts(client, get_token_user):
    token = get_token_user
    expected_result = {
        "carts": [
            {
                "id": 1,
                "id_user": 1,
                "state": "active",
            }
        ]
    }

    response = client.get("/me/carts", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json == expected_result


def test_get_current_cart(client, base_cart_item_api):
    id_cart, token = base_cart_item_api
    expected_result = {
        "cart": {
            "id": 1,
            "id_user": 1,
            "state": "active",
            "items": [{"id": 1, "id_cart": 1, "id_product": 1, "amount": 10}],
        }
    }
    response = client.get("/cart", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json == expected_result

def test_get_items_cart(client, base_cart_item_api):
    id_cart, token = base_cart_item_api
    expected_result = {
        "cart": {
            "id": 1,
            "id_user": 1,
            "state": "active",
            "items": [{"id": 1, "id_cart": 1, "id_product": 1, "amount": 10}],
        }
    }
    response = client.get(f"/me/carts/{id_cart}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json == expected_result

def test_update_cart(client, base_cart_api):
    id_cart, token = base_cart_api
    expected_put_result = {"message": "Cart updated"}
    expected_get_result = {
        "carts": [
            {
                "id": 1,
                "id_user": 1,
                "state": "inactive",
            },
            {
                "id": 2,
                "id_user": 1,
                "state": "active",
            },
        ]
    }

    response_put = client.put(
        f"/me/carts/{id_cart}",
        headers={"Authorization": f"Bearer {token}"},
    )
    response_get = client.get(
        f"/me/carts", headers={"Authorization": f"Bearer {token}"}
    )

    assert response_put.status_code == 200
    assert response_get.status_code == 200
    assert response_put.json == expected_put_result
    assert response_get.json == expected_get_result


def test_delete_cart(client, base_cart_api):
    id_cart, token = base_cart_api
    expected_delete_result = {"message": "Cart Deleted"}
    expected_get_result = {
        "carts": [
            {
                "id": 1,
                "id_user": 1,
                "state": "active",
            },
        ],
    }

    response_delete = client.delete(
        f"/me/carts/{id_cart}",
        headers={"Authorization": f"Bearer {token}"},
    )
    response_get = client.get(
        f"/me/carts", headers={"Authorization": f"Bearer {token}"}
    )
    assert response_delete.status_code == 200
    assert response_get.status_code == 200
    assert response_delete.json == expected_delete_result
    assert response_get.json == expected_get_result
