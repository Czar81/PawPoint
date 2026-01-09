def filter_values(locals_dict: dict, exclude: tuple = ("self",)):
    """
    Filter a dictionary removing None values and excluded keys.

    Commonly used to build update values.

    :param locals_dict: Dictionary (usually locals())
    :param exclude: Keys to exclude from the result
    :return: Dictionary with valid values only
    """
    return {k: v for k, v in locals_dict.items() if k not in exclude and v is not None}


def generate_cache_based_filters(key_prefix: str, filters_dict: dict):
    """
    Generate a cache key based on provided filter values.

    Useful for caching filtered query results.

    :param key_prefix: Base cache key
    :param filters_dict: Dictionary with filter parameters
    :return: Generated cache key
    """

    value_filters = filter_values(filters_dict)
    if value_filters:
        cache_suffix = ":".join(f"{k}={v}" for k, v in sorted(value_filters.items()))
        return f"{key_prefix}:{cache_suffix}"
    else:
        return f"{key_prefix}:all"


def generate_cache_key(key_prefix, id):
    """
    Generate a simple cache key using an identifier.

    :param key_prefix: Base cache key
    :param id: Resource identifier
    :return: Generated cache key
    """
    return f"{key_prefix}:{id}"


def get_cache_if_exist(key, cache_manager, db_manager, **search_params):
    """
    Retrieve data from cache if available, otherwise fetch from database
    and store the result in cache.

    :param key: Cache key
    :param cache_manager: Cache manager instance
    :param db_manager: Database manager instance
    :param search_params: Parameters passed to db_manager.get_data()
    :return: Tuple (result, HTTP status code)
    """
    result = cache_manager.get_data(key)
    if result is None:
        result = db_manager.get_data(**search_params)
        if result == "Not found":
            return "Could not find any item", 404
        cache_manager.store_data(key, result)
    return result, 200
