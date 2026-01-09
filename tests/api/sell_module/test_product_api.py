import pytest


def test_register_product(client, get_token_admin):
    token = get_token_admin
    sku = "TESTN1"
    name = "Test product"
    price = 1000
    amount = 30
    expected_result = {"id": 1, "message": "Product created"}

    response = client.post(
        "/products",
        json={"sku": sku, "name": name, "price": price, "amount": amount},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json == expected_result


def test_get_all_products(client, base_product_api):
    id_address, token = base_product_api
    expected_result = {
        "products": [
            {
                "id": 1,
                "sku": "TESTN1",
                "name": "Test product",
                "price": 1000,
                "amount": 30,
            }
        ]
    }

    response = client.get("/products")

    assert response.status_code == 200
    assert response.json == expected_result


def test_get_filter_products(client, base_product_api):
    id_address, token = base_product_api
    price = 1000
    expected_result = {
        "products": [
            {
                "id": 1,
                "sku": "TESTN1",
                "name": "Test product",
                "price": 1000,
                "amount": 30,
            }
        ]
    }
    response = client.get("/products", json={"price": price})

    assert response.status_code == 200
    assert response.json == expected_result


def test_get_single_product(client, base_product_api):
    id_address, token = base_product_api
    id_product = 1
    expected_result = {
    "product": [
        {
            "id": 1,
            "sku": "TESTN1",
            "name": "Test product",
            "price": 1000,
            "amount": 30,
        }
    ]
}
    response = client.get(
        f"/products/{id_product}"
    )

    assert response.status_code == 200
    assert response.json == expected_result


def test_update_product(client, base_product_api):
    id_product, token = base_product_api
    id_product = 1
    expected_put_result = {"message": "Product Updated"}
    new_price = 1000
    new_amount = 30
    expected_get_result = {
    "product": [
        {
            "id": 1,
            "sku": "TESTN1",
            "name": "Test product",
            "price": new_price,
            "amount": new_amount,
        }
    ]
}
    response_put = client.put(
        f"/products/{id_product}", json={"price":new_price, "amount":new_amount}, headers={"Authorization": f"Bearer {token}"}
    )
    response_get = client.get(
        f"/products/{id_product}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response_put.status_code == 200
    assert response_get.status_code == 200
    assert response_put.json == expected_put_result
    assert response_get.json == expected_get_result


def test_delete_product(client, base_product_api):
    id_product, token = base_product_api
    id_product = 1
    expected_delete_result = {"message": "Product Deleted"}
    expected_get_result = {"product": "Could not find any item"}

    response_delete = client.delete(
        f"/products/{id_product}", headers={"Authorization": f"Bearer {token}"}
    )
    response_get = client.get(
        f"/products/{id_product}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response_delete.status_code == 200
    assert response_get.status_code == 404
    assert response_delete.json == expected_delete_result
    assert response_get.json == expected_get_result
