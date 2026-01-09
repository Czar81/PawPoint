import pytest
from datetime import date


def test_create_receipt(
    db_receipt_manager, db_address_manager, db_payment_manager, base_cart_item
):
    id_user = 1
    id_cart = 1
    id_address = db_address_manager.insert_data(id_user, "9 Oak Valley Avenue")
    id_payment = db_payment_manager.insert_data(id_user, "card", "data_payment")
    result_expected = 1

    receipt_created = db_receipt_manager.create_receipt(
        id_cart, id_address, id_payment, id_user=id_user
    )

    assert result_expected == receipt_created


def test_get_all_receipt(db_receipt_manager, base_receipt):
    id_receipt = base_receipt
    result_expected = [
        {
            "id": 1,
            "id_address": 1,
            "id_cart": 1,
            "id_payment": 1,
            "state": "paid",
            "entry_date": str(date.today()),
        }
    ]
    receipts = db_receipt_manager.get_data()

    assert result_expected == receipts


def test_update_receipt_state(db_receipt_manager, base_receipt):
    id_user = 1
    id_receipt = base_receipt
    new_state = "canceled"
    result_expected = [
        {
            "id": 1,
            "id_address": 1,
            "id_cart": 1,
            "id_payment": 1,
            "state": "canceled",
            "entry_date": str(date.today()),
        }
    ]

    updated = db_receipt_manager.update_data(id_receipt, new_state, id_user)
    receipts = db_receipt_manager.get_data()

    assert updated == True
    assert receipts == result_expected


def test_return_receipt(db_receipt_manager, db_product_manager, base_receipt):
    id_user = 1
    id_receipt = base_receipt
    result_receipt_expected = [
        {
            "id": 1,
            "id_address": 1,
            "id_cart": 1,
            "id_payment": 1,
            "state": "returned",
            "entry_date": str(date.today()),
        }
    ]
    result_product_expected = [
        {
            "id": 1,
            "sku": "FD_NU_132",
            "name": "nutrisource lite",
            "price": 1000,
            "amount": 50,
        }
    ]
    returned = db_receipt_manager.return_receipt(id_user, id_receipt)
    receipts = db_receipt_manager.get_data()
    product = db_product_manager.get_data()
    assert returned == True
    assert receipts == result_receipt_expected
    assert product == result_product_expected
