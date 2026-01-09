from src.utils import register_error_handlers, APIException
from src.extensions import jwt_manager, db_user_manager
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask, Blueprint
import pytest
from redis import Redis
from src.utils.cache_manager import CacheManager
import os


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_KEY = os.getenv("REDIS_KEY", None)


@pytest.fixture(scope="module")
def redis_client():
    client = Redis(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_KEY, decode_responses=True
    )
    yield client
    client.flushdb()


@pytest.fixture
def cache_manager(redis_client):
    cm = CacheManager()
    cm.redis_client = redis_client
    redis_client.flushdb()
    return cm


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client():
    app = Flask(__name__)
    bp = Blueprint("test_bp", __name__)

    register_error_handlers(bp)

    @bp.route("/value-error")
    def route_value_error():
        raise ValueError("bad value")

    @bp.route("/db-error")
    def route_db_error():
        raise SQLAlchemyError("db failed")

    @bp.route("/api-error")
    def route_api_error():
        raise APIException("custom fail", 418)

    @bp.route("/rec-error")
    def route_rec_error():
        raise RecursionError("stack explosion")

    @bp.route("/generic-error")
    def route_generic_error():
        raise RuntimeError("boom")

    app.register_blueprint(bp)
    client = app.test_client()

    return client


@pytest.fixture
def admin_token():
    user_data = {"username": "admin_test", "password": "1234"}
    id_user = db_user_manager.insert_data(**user_data, role="admin")
    token = jwt_manager.encode({"id": id_user})
    return token


@pytest.fixture
def user_token():
    user_data = {"username": "user_test", "password": "1234"}
    id_user = db_user_manager.insert_data(**user_data, role="user")
    token = jwt_manager.encode({"id": id_user})
    return token
