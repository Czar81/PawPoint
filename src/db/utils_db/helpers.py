def _filter_locals(table, locals_dict: dict, exclude: tuple = ("self",)):
    """
    Generate SQLAlchemy filter conditions from local variables.

    Filters out excluded keys and values that are None,
    then creates equality conditions for each remaining field.

    :param table: SQLAlchemy table object
    :param locals_dict: Dictionary of local variables (usually locals())
    :param exclude: Tuple of keys to exclude from filtering
    :return: List of SQLAlchemy filter conditions
    """
    filtered = {
        k: v for k, v in locals_dict.items() if k not in exclude and v is not None
    }
    return [getattr(table.c, k) == v for k, v in filtered.items()]
