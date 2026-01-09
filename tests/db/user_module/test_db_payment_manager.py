import pytest


def test_create_payment(base_user, db_payment_manager):
    id_user = base_user
    type_payment = "card"
    data = "data_payment"  # hash or encrypted data of the card
    result_expected = 1

    payment_created = db_payment_manager.insert_data(id_user, type_payment, data)

    assert result_expected == payment_created


def test_get_all_payment(db_payment_manager, base_payment):
    result_expected = [
        {"id": 1, "id_user": 1, "type_data": "card", "data": "data_payment"}
    ]

    payments = db_payment_manager.get_data(id_user=1)

    assert result_expected == payments


def test_update_all_payment_params(db_payment_manager, base_payment):
    id_payment = base_payment
    new_type = "visa card"
    new_data = "new data content"
    result_expected = [
        {
            "id": id_payment,
            "id_user": id_payment,
            "type_data": "visa card",
            "data": "new data content",
        }
    ]

    updated = db_payment_manager.update_data(id_payment, new_type, new_data, id_user=1)
    payments = db_payment_manager.get_data(id_user=1)

    assert updated == True
    assert payments == result_expected


def test_delete_payment(db_payment_manager, base_payment):
    id_payment = base_payment
    result_expected = "Not payments found"
    deleted = db_payment_manager.delete_data(id_payment, id_user=1)
    payments = db_payment_manager.get_data(id_user=1)

    assert deleted == True
    assert payments == result_expected
