from src.api import (
    address_bp,
    cart_bp,
    user_bp,
    payment_bp,
    product_bp,
    receipt_bp,
    cart_items_bp,
)
from flask import Flask
import pytest
from os import getenv


@pytest.fixture
def client():
    app = Flask("Store-service")
    app.config["TESTING"] = True
    app.register_blueprint(address_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(receipt_bp)
    app.register_blueprint(cart_items_bp)
    with app.test_client() as client:
        yield client


@pytest.fixture
def get_token_user(client):
    response = client.post(
        "/register", json={"username": "TestUser", "password": "12345"}
    )
    return response.json["token"]


@pytest.fixture
def get_token_admin(client):
    response = client.post(
        "/register",
        json={"username": "admin232", "password": "fds67tf67dstf67sdf687sd"},
        headers={"X-ADMIN-TOKEN": getenv("ADMIN_BOOTSTRAP_TOKEN")},
    )
    return response.json["token"]


@pytest.fixture
def base_address_api(client, get_token_user):
    token = get_token_user
    response = client.post(
        "/me/address",
        json={"location": "Test location"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json["id"], token


@pytest.fixture
def base_payment_api(client, get_token_user):
    token = get_token_user
    response = client.post(
        "/me/payment",
        json={"type_data": "card", "data": "fsdfsdafsadffsdf"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json["id"], token


@pytest.fixture
def base_product_api(client, get_token_admin):
    token = get_token_admin
    response = client.post(
        "/products",
        json={
            "sku": "TESTN1",
            "name": "Test product",
            "price": 1000,
            "amount": 30,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    return response.json["id"], token


@pytest.fixture
def base_cart_api(client, get_token_user):
    token = get_token_user
    response = client.post(
        "/me/carts",
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json["id"], token


@pytest.fixture
def base_cart_item_api(client, get_token_user, base_product_api):
    token_user = get_token_user
    id_product, token_admin = base_product_api

    response = client.post(
        "/add-item",
        json={"id_cart": 1, "id_product": id_product, "amount": 10},
        headers={"Authorization": f"Bearer {token_user}"},
    )
    return response.json["id"], token_user


@pytest.fixture
def base_receipt_api(client, base_cart_item_api):
    id_cart, token = base_cart_item_api

    response_payment = client.post(
        "/me/payment",
        json={"type_data": "Card", "data": "fsdfsdafsfdsfadffsdf"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response_address = client.post(
        "/me/address",
        json={"location": "Test location"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.post(
        "/create-receipt",
        json={
            "id_cart": id_cart,
            "id_address": response_address.json["id"],
            "id_payment": response_payment.json["id"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json["id"], token


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
