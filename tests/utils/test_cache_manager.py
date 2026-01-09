import time
import pytest


def test_store_and_get_data(cache_manager):
    cache_manager.store_data("test_key", [1, 2, 3])
    result = cache_manager.get_data("test_key")
    assert result == [1, 2, 3]


def test_store_data_with_ttl(cache_manager):
    cache_manager.store_data("ttl_key", ["a", "b"], time_to_live=1)
    result = cache_manager.get_data("ttl_key")
    assert result == ["a", "b"]
    time.sleep(1.1)
    result = cache_manager.get_data("ttl_key")
    assert result is None


def test_check_key_exists(cache_manager):
    cache_manager.store_data("exists", [10])
    assert cache_manager.check_key("exists") is True


def test_check_key_not_exists(cache_manager):
    assert cache_manager.check_key("nope") is False


def test_delete_data(cache_manager):
    cache_manager.store_data("to_delete", [1])
    cache_manager.delete_data("to_delete")
    assert cache_manager.check_key("to_delete") is False


def test_delete_data_with_pattern(cache_manager):
    cache_manager.store_data("test:1", [1])
    cache_manager.store_data("test:2", [2])
    cache_manager.store_data("other", [3])

    cache_manager.delete_data_with_pattern("test:*")

    assert cache_manager.check_key("test:1") is False
    assert cache_manager.check_key("test:2") is False
    assert cache_manager.check_key("other") is True
