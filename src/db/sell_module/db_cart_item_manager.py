from sqlalchemy import insert, select, delete, update, and_
from src.db.utils_db.helpers import _filter_locals
from src.db.utils_db.verifies import _verify_user_own_cart, _verify_amount_product
from src.utils.api_exception import APIException


class DbCartItemsManager:
    """
    Database manager for cart items.
    Handles creation, retrieval, update and deletion
    of products inside shopping carts.
    """

    def __init__(self, TablesManager):
        """
        Initialize the cart items database manager.

        :param TablesManager: Instance containing database tables and engine
        """
        self.cart_item_table = TablesManager.cart_item_table
        self.cart_table = TablesManager.cart_table
        self.engine = TablesManager.engine

    def insert_data(
        self, id_cart: int, id_product: int, amount: int, id_user: int | None = None
    ):
        """
        Add a product to a user's cart.

        :param id_cart: Cart ID
        :param id_product: Product ID
        :param amount: Quantity to add
        :param id_user: User ID
        :return: Newly created cart item ID
        """
        with self.engine.connect() as conn:
            if not _verify_user_own_cart(conn=conn, id_user=id_user, id_cart=id_cart):
                raise APIException(
                    f"Cart id:{id_cart} not owned by user id:{id_user}, or not exist",
                    403,
                )
            stmt = (
                insert(self.cart_item_table)
                .returning(self.cart_item_table.c.id)
                .values(id_cart=id_cart, id_product=id_product, amount=amount)
            )
            result = conn.execute(stmt).scalar()
            if result is None:
                raise APIException(f"Could not create cart item", 500)
            conn.commit()
        return result

    def get_data(
        self,
        id_item: int | None = None,
        id_user: int | None = None,
        id_cart: int | None = None,
        id_product: int | None = None,
        amount: int | None = None,
    ):
        """
        Retrieve cart items using optional filters.
        Validates that the cart belongs to the user.

        :param id_item: Cart item ID
        :param id_user: User ID
        :param id_cart: Cart ID
        :param id_product: Product ID
        :param amount: Item quantity
        :return: List of cart items
        """
        conditions = _filter_locals(self.cart_item_table, locals())
        with self.engine.connect() as conn:
            if not _verify_user_own_cart(
                conn=conn,
                id_user=id_user,
                id_table=id_item,
                id_cart=id_cart,
                table=self.cart_item_table,
            ):
                raise APIException(f"Cart not owned by user id:{id_user}", 403)
            stmt = select(self.cart_item_table)
            if conditions:
                stmt = stmt.where(and_(*conditions))
            result = conn.execute(stmt).mappings().all()
        if not result:
            return "Not cart items found"
        return [dict(row) for row in result]

    def update_data(
        self,
        id_item: int,
        amount: int,
        id_user: int,
    ):
        """
        Update the quantity of a product in a cart.
        Verifies product stock before updating.

        :param id_item: Cart item ID
        :param amount: New quantity
        :param id_user: User ID
        :return: True if updated successfully
        """
        with self.engine.connect() as conn:
            if not _verify_user_own_cart(
                conn=conn, id_user=id_user, id_table=id_item, table=self.cart_item_table
            ):
                raise APIException(f"Item id:{id_item} not exist", 404)
            stmt_id_product = select(self.cart_item_table.c.id_product).where(
                self.cart_item_table.c.id == id_item
            )
            id_product = conn.execute(stmt_id_product).scalar()
            actual_amount = _verify_amount_product(conn, id_product, amount)
            stmt = (
                update(self.cart_item_table)
                .where(self.cart_item_table.c.id == id_item)
                .values(amount=amount)
            )
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise APIException((f"Item id:{id_item} not exist"), 404)
            conn.commit()
        return True

    def delete_data(self, id_item: int, id_user: int | None = None):
        """
        Remove an item from a user's cart.

        :param id_item: Cart item ID
        :param id_user: User ID
        :return: True if deleted successfully
        """
        with self.engine.connect() as conn:
            if not _verify_user_own_cart(
                conn=conn, id_user=id_user, id_table=id_item, table=self.cart_item_table
            ):
                raise APIException(f"Item id:{id_item} not exist", 403)
            stmt = delete(self.cart_item_table).where(
                self.cart_item_table.c.id == id_item
            )
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise APIException(f"Item id:{id_item} not exist", 404)
            conn.commit()
        return True
