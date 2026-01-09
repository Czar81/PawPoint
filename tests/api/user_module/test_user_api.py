import pytest
from os import getenv
from src.extensions import db_user_manager


def test_register_user(client):
    response = client.post(
        "/register", json={"username": "TestUser1", "password": "12345"}
    )

    assert response.status_code == 201
    assert "token" in response.json


def test_register_admin(client):
    response = client.post(
        "/register",
        json={"username": "admin232", "password": "12345"},
        headers={"X-ADMIN-TOKEN": getenv("ADMIN_BOOTSTRAP_TOKEN")},
    )
    assert response.status_code == 201
    assert "token" in response.json


def test_login(client, get_token_user):
    response = client.post("/login", json={"username": "TestUser", "password": "12345"})

    assert response.status_code == 200
    assert "token" in response.json

def test_get_all_users(client, get_token_user, get_token_admin):
    token = get_token_admin
    result_expected = {
        'user': [
            {
                'id': 1,
                'password': '12345',
                'role': 'user',
                'username': 'TestUser',
            },
            {
                'id': 2,
                'password': 'fds67tf67dstf67sdf687sd',
                'role': 'admin',
                'username': 'admin232',
            },
        ],
    }
    response = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert result_expected == response.json

def test_get_profile(client, get_token_user):
    token = get_token_user
    result_expected = {
        "user": [
            {
                "id": 1,
                "password": "12345",
                "role": "user",
                "username": "TestUser",
            }
        ]
    }
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert result_expected == response.json


def test_update_profile(client, get_token_user):
    token = get_token_user
    expected_message = {"message": "User updated"}
    updated_user = {
        "user": [
            {
                "id": 1,
                "password": "678910",
                "role": "user",
                "username": "TestUser2",
            }
        ]
    }

    response_update = client.put(
        "/me",
        json={
            "username": "TestUser2",
            "password": "678910",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    response_get = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response_update.status_code == 200
    assert expected_message == response_update.json
    assert updated_user == response_get.json


def test_delete_user(client, get_token_user):
    token = get_token_user
    expected_message_delete = {"message": "User deleted"}
    expected_message_get = {"message": "User not found, register first"}

    response_delete = client.delete("/me", headers={"Authorization": f"Bearer {token}"})
    response_get = client.post(
        "/login", json={"username": "TestUser", "password": "12345"}
    )

    assert response_delete.status_code == 200
    assert expected_message_delete == response_delete.json
    assert expected_message_get == response_get.json
