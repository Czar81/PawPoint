import pytest

def test_create_user(db_user_manager):
    username = "Ian"
    password = "2NFD9JDFI4324NJF20"
    result_expected = 1

    id_user = db_user_manager.insert_data(username, password)

    assert id_user == result_expected


def test_create_admin(db_user_manager):
    username = "Czar"
    password = "2NFD9JDsdaFI4324NJF20"
    role = "admin"

    result_expected = 1

    id_user = db_user_manager.insert_data(username, password, role)

    assert id_user == result_expected


def test_get_users(db_user_manager, base_user):
    result_expected = [
        {"id": 1, "username": "TestUser", "password": "12345", "role":"user"}
    ]

    users = db_user_manager.get_data()

    assert users == result_expected


def test_login(db_user_manager, base_user):
    username="TestUser"
    password="12345"
    result_expected = 1

    me = db_user_manager.get_user(username, password)

    assert me == result_expected


def test_get_role(db_user_manager, base_user):
    result_expected = "user"

    role = db_user_manager.get_role_by_id(base_user)

    assert role == result_expected


def test_update_all_args_user(db_user_manager, base_user):
    username = "Claro"
    password = "e4d909c290d0fb1ca068ffaddf22cbd0"
    role = "vendor"
    result_expected = True

    result = db_user_manager.update_data(base_user, username, password, role)

    assert result == result_expected


def test_update_one_args_user(db_user_manager,base_user):
    new_username = "Nutrisource"
    result_expected = True

    result = db_user_manager.update_data(base_user, new_username)

    assert result == result_expected


def test_delete_user(db_user_manager, base_user):
    result_expected = True

    result = db_user_manager.delete_data(base_user)

    assert result == result_expected
