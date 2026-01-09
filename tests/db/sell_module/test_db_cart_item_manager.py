import pytest


def test_create_cart_item(db_cart_item_manager, base_cart, base_product):
    id_cart = base_cart
    id_product = base_product
    amount = 100
    result_expected = 1

    cart_item_created = db_cart_item_manager.insert_data(id_cart, id_product, amount)

    assert result_expected == cart_item_created


def test_get_all_cart_item(db_cart_item_manager, base_cart_item):
    id_cart_item = base_cart_item
    result_expected = [
        {"id": id_cart_item, "id_cart": 1, "id_product": 1, "amount": 10}
    ]

    cart_items = db_cart_item_manager.get_data()

    assert result_expected == cart_items


def test_update_cart_item_amout(db_cart_item_manager, base_cart_item):
    id_cart_item = base_cart_item
    new_amount = 5

    result_expected = [
        {"id": id_cart_item, "id_cart": 1, "id_product": 1, "amount": new_amount}
    ]
    updated = db_cart_item_manager.update_data(id_cart_item, new_amount, 1)
    cart_items = db_cart_item_manager.get_data()

    assert updated == True
    assert cart_items == result_expected


def test_delete_cart_item(db_cart_item_manager, base_cart_item):
    id_cart_item = base_cart_item
    result_expected = "Not cart items found"

    deleted = db_cart_item_manager.delete_data(id_cart_item, id_user=1)
    cart_items = db_cart_item_manager.get_data()

    assert deleted == True
    assert cart_items == result_expected
