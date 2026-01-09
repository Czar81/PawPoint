import pytest
from src.db import (
    DbPaymentManager,
    DbUserManager,
    DbAddressManager,
    DbCartItemsManager,
    DbCartManager,
    DbProductManager,
    DbReceiptManager,
    TablesManager,
)


@pytest.fixture
def db():
    tm = TablesManager(url="sqlite:///:memory:")
    tm.create_tables()
    return tm

@pytest.fixture(autouse=True)
def clean_db():
    from sqlalchemy import text
    from src.extensions import tm

    engine = tm.engine
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM receipt"))
        conn.execute(text("DELETE FROM cart_item"))
        conn.execute(text("DELETE FROM cart"))
        conn.execute(text("DELETE FROM payment"))
        conn.execute(text("DELETE FROM address"))
        conn.execute(text("DELETE FROM user"))
        conn.execute(text("DELETE FROM product"))

@pytest.fixture
def base_user(db_user_manager):
    id_user = db_user_manager.insert_data("TestUser", "12345", "user")
    return id_user


@pytest.fixture
def base_payment(db_user_manager, db_payment_manager):
    id_user = db_user_manager.insert_data("TestUser", "12345", "user")
    id_payment = db_payment_manager.insert_data(id_user, "card", "data_payment")
    return id_payment


@pytest.fixture
def base_address(db_user_manager, db_address_manager):
    id_user = db_user_manager.insert_data("TestUser", "12345", "user")
    id_address = db_address_manager.insert_data(id_user, "9 Oak Valley Avenue")
    return id_address


@pytest.fixture
def base_product(db_product_manager):
    id_product = db_product_manager.insert_data(
        "FD_NU_132", "nutrisource lite", 1000, 50
    )
    return id_product


@pytest.fixture
def base_cart(db_user_manager, db_cart_manager):
    id_user = db_user_manager.insert_data("TestUser", "12345", "user")
    id_cart = db_cart_manager.insert_data(id_user)
    return id_cart


@pytest.fixture
def base_cart_item(
    request, db_cart_manager, db_user_manager, db_cart_item_manager, db_product_manager
):
    id_user = db_user_manager.insert_data("TestUser", "12345", "user")
    id_cart = db_cart_manager.insert_data(id_user)
    id_product = db_product_manager.insert_data(
        "FD_NU_132", "nutrisource lite", 1000, 50
    )
    id_cart_item = db_cart_item_manager.insert_data(
        id_cart, id_product, 10, id_user
    )
    return id_cart_item


@pytest.fixture
def base_receipt(
    request,
    db_user_manager,
    db_cart_manager,
    db_address_manager,
    db_payment_manager,
    db_cart_item_manager,
    db_product_manager,
    db_receipt_manager,
):

    id_user = db_user_manager.insert_data("TestUser", "12345", "user")
    id_payment = db_payment_manager.insert_data(id_user, "card", "data_payment")
    id_address = db_address_manager.insert_data(id_user, "9 Oak Valley Avenue")
    id_cart = db_cart_manager.insert_data(id_user)
    id_product = db_product_manager.insert_data(
        "FD_NU_132", "nutrisource lite", 1000, 50
    )
    id_cart_item = db_cart_item_manager.insert_data(
        id_cart, id_product, 20, id_user
    )
    id_receip = db_receipt_manager.create_receipt(
        id_cart, id_address, id_payment, id_user
    )
    return id_receip


@pytest.fixture
def db_payment_manager(db):
    return DbPaymentManager(db)


@pytest.fixture
def db_user_manager(db):
    return DbUserManager(db)


@pytest.fixture
def db_address_manager(db):
    return DbAddressManager(db)


@pytest.fixture
def db_cart_item_manager(db):
    return DbCartItemsManager(db)


@pytest.fixture
def db_cart_manager(db):
    return DbCartManager(db)


@pytest.fixture
def db_product_manager(db):
    return DbProductManager(db)


@pytest.fixture
def db_receipt_manager(db):
    return DbReceiptManager(db)
