from sqlalchemy import insert, select, delete, update, and_
from src.db.utils_db.helpers import _filter_locals
from src.db.utils_db.verifies import _verify_user_own_cart
from src.utils.api_exception import APIException


class DbCartManager:
    """
    Database manager for shopping carts.
    Handles cart creation, retrieval, updates, deletion
    and cart-item aggregation.
    """

    def __init__(self, TablesManager):
        """
        Initialize the cart database manager.

        :param TablesManager: Instance containing database tables and engine
        """
        self.cart_table = TablesManager.cart_table
        self.cart_item_table = TablesManager.cart_item_table
        self.engine = TablesManager.engine

    def insert_data(self, id_user: int):
        """
        Create a new cart for a user.
        If the user already has an active cart, the new cart
        will be created as inactive.

        :param id_user: User ID
        :return: Newly created cart ID
        """
        values = {"id_user": id_user}
        with self.engine.connect() as conn:
            if self.__verify_if_user_have_active(conn, id_user):
                values["state"] = "inactive"

            stmt = (
                insert(self.cart_table).returning(self.cart_table.c.id).values(**values)
            )
            result = conn.execute(stmt).scalar()
            if result is None:
                raise APIException("Could not create cart", 500)
            conn.commit()
        return result

    def get_data(
        self,
        id_user: int,
        id_cart: int | None = None,
        state: str | None = None,
    ):
        """
        Create a new cart for a user.
        If the user already has an active cart, the new cart
        will be created as inactive.

        :param id_user: User ID
        :return: Newly created cart ID
        """
        conditions = _filter_locals(self.cart_table, locals())
        stmt = select(self.cart_table)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        with self.engine.connect() as conn:
            result = conn.execute(stmt).mappings().all()
            if not result:
                return "Not carts found"
            return [dict(row) for row in result]

    def get_cart_with_items(
        self,
        id_user: int,
        id_cart: int | None = None,
        active: bool = True,
    ):
        """
        Retrieve a cart along with its associated items.
        By default, retrieves the active cart.

        :param id_user: User ID
        :param id_cart: Specific cart ID
        :param active: Whether to retrieve only the active cart
        :return: Cart data including items
        """
        stmt = (
            select(self.cart_table, self.cart_item_table)
            .join(
                self.cart_item_table,
                self.cart_item_table.c.id_cart == self.cart_table.c.id,
                isouter=True,
            )
            .where(
                self.cart_table.c.id_user == id_user,
            )
        )
        if id_cart is not None:
            stmt = stmt.where(self.cart_table.c.id == id_cart)
        elif active:
            stmt = stmt.where(self.cart_table.c.state == "active")

        with self.engine.connect() as conn:
            rows = conn.execute(stmt).mappings().all()
            if not rows:
                raise APIException(
                    "Unexpected error occurred trying to get current cart", 500
                )

            cart_data = dict(rows[0])
            cart_data = {k: cart_data[k] for k in self.cart_table.columns.keys()}

            items = []
            for row in rows:
                item_dict = {k: row[k] for k in self.cart_item_table.columns.keys()}
                if item_dict["id"] is not None:
                    items.append(item_dict)

            cart_data["items"] = items
            return cart_data

    def update_data(self, id_cart: int, state: str, id_user: int):
        """
        Update the state of a cart.
        Ensures that the user always has at least one active cart.

        :param id_cart: Cart ID
        :param state: New cart state
        :param id_user: User ID
        :return: True if updated successfully
        """
        with self.engine.connect() as conn:
            if not _verify_user_own_cart(conn, id_user, id_cart=id_cart):
                raise APIException(f"Cart id:{id_cart} not exist", 401)

            stmt_select = select(self.cart_table).where(
                and_(
                    self.cart_table.c.id_user == id_user,
                    self.cart_table.c.state == "active",
                )
            )
            id_active_cart = conn.execute(stmt_select).scalar()
            if id_active_cart is not None:
                stmt_update_old = (
                    update(self.cart_table)
                    .where(self.cart_table.c.id == id_active_cart)
                    .values(state="inactive")
                )
                updated_old_cart = conn.execute(stmt_update_old)
            if updated_old_cart is None:
                raise APIException(
                    f"Must have another cart, can not have all unactive carts", 400
                )
            stmt = (
                update(self.cart_table)
                .where(self.cart_table.c.id == id_cart)
                .values(state=state)
            )
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise APIException(f"Cart id:{str(id_cart)} does not exist", 404)
            conn.commit()
        return True

    def delete_data(self, id_cart: int, id_user: int):
        """
        Delete a cart.
        Active carts cannot be deleted.

        :param id_cart: Cart ID
        :param id_user: User ID
        :return: True if deleted successfully
        """
        stmt = delete(self.cart_table).where(
            and_(self.cart_table.c.id == id_cart, self.cart_table.c.id_user == id_user)
        )
        with self.engine.connect() as conn:

            if self.__verify_if_cart_is_active(conn, id_cart):
                raise APIException(
                    f"Cart id:{id_cart} is active, can not delete an active cart", 400
                )
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise APIException(f"Cart id:{id_cart} not exist", 404)
            conn.commit()
        return True

    def __verify_if_cart_is_active(self, conn, id_cart: int):
        """
        Check if a cart is currently active.

        :param conn: Database connection
        :param id_cart: Cart ID
        :return: True if cart is active
        """
        stmt = select(self.cart_table).where(
            and_(
                self.cart_table.c.id == id_cart,
                self.cart_table.c.state == "active",
            )
        )
        result = conn.execute(stmt).fetchone()
        return bool(result)

    def __verify_if_user_have_active(self, conn, id_user: int):
        """
        Check if a user already has an active cart.

        :param conn: Database connection
        :param id_user: User ID
        :return: True if user has an active cart
        """
        stmt = select(self.cart_table).where(
            and_(
                self.cart_table.c.id_user == id_user,
                self.cart_table.c.state == "active",
            )
        )
        result = conn.execute(stmt).fetchone()
        return bool(result)
