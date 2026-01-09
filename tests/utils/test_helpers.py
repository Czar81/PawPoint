from src.utils import filter_values, generate_cache_based_filters, generate_cache_key

import pytest


def test_filter_values():
    v_test1 = None
    v_test2 = "Test"
    v_test3 = "Must be exclude"
    expected_result = {"v_test2": "Test"}

    filters = filter_values(locals(), exclude=("v_test3", "expected_result",))

    assert filters == expected_result


def test_generate_cache_based_filters():
    filters_dict = {"f_test1": None, "f_test2": "Test", "f_test3": "3rdFilter"}
    expected_result = "getTest:f_test2=Test:f_test3=3rdFilter"

    filters = generate_cache_based_filters("getTest", filters_dict)

    assert filters == expected_result

def test_generate_cache_key():
    key_prefix = "getTests"
    id = 4389
    expected_result = "getTests:4389"

    cache_key = generate_cache_key(key_prefix, id)

    assert cache_key == expected_result

def test_get_cache_if_exist():
    from src.extensions import cache_manager
    from src.extensions import db_product_manager
    from src.utils import get_cache_if_exist
    key = "getProductTests"

    result, code = get_cache_if_exist(key, cache_manager, db_product_manager, id=1)

    assert result == "Could not find any item"
    assert code ==  404
