import pytest


def test_register_cart_item(client, base_cart_api, base_product_api):
    id_cart, token = base_cart_api
    id_prodcut, token_admin = base_product_api
    expected_result = {"id": 1, "message": "Item added"}

    response = client.post(
        "/add-item",
        json={"id_cart": id_cart, "id_product": 1, "amount": 1},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json == expected_result


def test_update_cart(client, base_cart_item_api):
    id_cart_item, token = base_cart_item_api
    expected_result = {"message": "Amount updated"}

    response = client.put(
        f"/modify-amount-item/{id_cart_item}",
        json={"id_cart_item": id_cart_item, "amount": 4},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json == expected_result


def test_delete_cart(client, base_cart_item_api):
    id_cart_item, token = base_cart_item_api
    expected_result = {"message": "Item deleted"}
    response = client.delete(
        f"/remove-item/{id_cart_item}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json == expected_result
