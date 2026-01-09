from .tables_manager import TablesManager
from sqlalchemy import select, and_

payment_table = TablesManager.payment_table
address_table = TablesManager.address_table
product_table = TablesManager.product_table
cart_table = TablesManager.cart_table


def _verify_amount_product(conn, id_product, amount_bought):
    """
    Verify product stock availability.

    Checks if a product exists and if there is enough stock
    to fulfill the requested amount.

    :param conn: Active database connection
    :param id_product: Product ID
    :param amount_bought: Quantity requested
    :return: New available amount after purchase
    :raises ValueError: If product does not exist or stock is insufficient
    """
    stmt = select(product_table.c.amount).where(product_table.c.id == id_product)
    actual_amount = conn.execute(stmt).scalar()
    if actual_amount is None:
        raise ValueError(f"Product with id {id_product} not found")

    if actual_amount < amount_bought:
        raise ValueError(
            f"Insufficient stock. Available: {actual_amount}, Requested: {amount_bought}"
        )
    if actual_amount is None:
        return False
    new_amount = actual_amount - amount_bought
    return new_amount


def _verify_user_own_cart(
    conn,
    id_user: int | None = None,
    id_table: int | None = None,
    id_cart: int | None = None,
    table=None,
):
    """
    Verify product stock availability.

    Checks if a product exists and if there is enough stock
    to fulfill the requested amount.

    :param conn: Active database connection
    :param id_product: Product ID
    :param amount_bought: Quantity requested
    :return: New available amount after purchase
    :raises ValueError: If product does not exist or stock is insufficient
    """
    if id_user is None:
        return True
    if id_table is not None and table is not None:
        stmt = (
            select(cart_table.c.id_user)
            .select_from(table.join(cart_table, table.c.id_cart == cart_table.c.id))
            .where(table.c.id == id_table)
        )
    else:
        stmt = select(cart_table.c.id_user).where(
            and_(cart_table.c.id_user == id_user, cart_table.c.id == id_cart)
        )
    result = conn.execute(stmt).scalar()
    return bool(result and result == id_user)


def _verify_user_own_payment(conn, id_payment: int, id_user: int | None = None):
    """
    Verify that a payment method belongs to a user.

    :param conn: Active database connection
    :param id_payment: Payment ID
    :param id_user: User ID
    :return: True if the payment belongs to the user, False otherwise
    """
    if id_user is None or id_payment is None:
        return True
    stmt = select(payment_table.c.id_user).where(
        and_(payment_table.c.id == id_payment, payment_table.c.id_user == id_user)
    )
    result = conn.execute(stmt).scalar()
    return bool(result and result == id_user)


def _verify_user_own_address(
    conn, id_address: int | None = None, id_user: int | None = None
):
    """
    Verify that an address belongs to a user.

    :param conn: Active database connection
    :param id_address: Address ID
    :param id_user: User ID
    :return: True if the address belongs to the user, False otherwise
    """
    if id_user is None or id_address is None:
        return True
    stmt = select(address_table.c.id_user).where(
        and_(address_table.c.id == id_address, address_table.c.id_user == id_user)
    )
    result = conn.execute(stmt).scalar()
    return bool(result and result == id_user)
