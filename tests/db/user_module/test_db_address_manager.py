import pytest


def test_create_address(base_user, db_address_manager):
    id_user = base_user
    location = "9 Oak Valley Avenue"
    result_expected = 1

    address_created = db_address_manager.insert_data(id_user, location)

    assert result_expected == address_created


def test_get_all_address(db_address_manager, base_address):
    id_user = base_address
    result_expected = [{"id": 1, "id_user": id_user, "location": "9 Oak Valley Avenue"}]

    address = db_address_manager.get_data(id_user=id_user)

    assert result_expected == address


def test_update_all_address_params(db_address_manager, base_address):
    id_address = base_address
    new_location = "Fiordo de Geirangerfjord, Noruega"
    result_expected = [
        {
            "id": id_address,
            "id_user": 1,
            "location": "Fiordo de Geirangerfjord, Noruega",
        }
    ]

    updated = db_address_manager.update_data(id_user=1, id_address=id_address, location=new_location)
    address = db_address_manager.get_data(id_user=1)

    assert updated == True
    assert address == result_expected


def test_delete_address(db_address_manager, base_address):
    id_address = base_address
    result_expected = "Not address found"
    deleted = db_address_manager.delete_data(id_user=1, id_address=id_address)
    address = db_address_manager.get_data(id_user=1)

    assert deleted == True
    assert address == result_expected
