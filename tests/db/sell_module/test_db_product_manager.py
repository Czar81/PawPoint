import pytest


def test_create_product(db_product_manager):
    sku = "FD_NU_132"
    name = "nutrisource lite"
    price = 1000
    amount = 50
    result_expected = 1

    product_created = db_product_manager.insert_data(sku, name, price, amount)

    assert result_expected == product_created


def test_get_all_product(db_product_manager, base_product):
    id_product = base_product
    result_expected = [
        {
            "id": id_product,
            "sku": "FD_NU_132",
            "name": "nutrisource lite",
            "price": 1000,
            "amount": 50,
        }
    ]

    products = db_product_manager.get_data()

    assert result_expected == products


def test_update_all_product_params(db_product_manager, base_product):
    id_product = base_product
    new_sku = "FD_NU_780"
    new_name = "nutrisource plus"
    new_price = 3000
    new_amount = 10
    result_expected = [
        {
            "id": id_product,
            "sku": "FD_NU_780",
            "name": "nutrisource plus",
            "price": 3000,
            "amount": 10,
        }
    ]

    updated = db_product_manager.update_data(
        id_product, new_sku, new_name, new_price, new_amount
    )
    products = db_product_manager.get_data()

    assert updated == True
    assert products == result_expected


def test_delete_product(db_product_manager, base_product):
    id_product = base_product
    result_expected = "Not found"
    deleted = db_product_manager.delete_data(id_product)
    products = db_product_manager.get_data()

    assert deleted == True
    assert products == result_expected
