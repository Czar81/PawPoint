import pytest

def test_raise_value_error(client):
    res = client.get("/value-error")

    assert res.status_code == 400
    assert res.json["error"] == "bad value"


def test_raise_sqlalchemy_error(client):
    res = client.get("/db-error")

    assert res.status_code == 500
    assert "Internal database error" in res.json["error"]
    assert "db failed" in res.json["error"]


def test_raise_api_exception(client):
    res = client.get("/api-error")

    assert res.status_code == 418
    assert res.json["error"] == "custom fail"


def test_raise_recursion_error(client):
    res = client.get("/rec-error")

    assert res.status_code == 500
    assert res.json["error"] == "An unexpected error occurred with redis"


def test_raise_generic_exception(client):
    res = client.get("/generic-error")

    assert res.status_code == 500
    assert "An unexpected error occurred" in res.json["error"]
    assert "boom" in res.json["error"]