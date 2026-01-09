from sqlalchemy import select, insert, update, and_
from src.utils.api_exception import APIException
from datetime import datetime
from src.db.utils_db.helpers import _filter_locals
from src.db.utils_db.verifies import (
    _verify_user_own_cart,
    _verify_user_own_address,
    _verify_user_own_payment,
)


class DbReceiptManager:
    """
    Database manager for receipts.
    Handles receipt creation, retrieval, updates and returns,
    including stock management and ownership validation.
    """

    def __init__(self, TablesManager):
        """
        Database manager for receipts.
        Handles receipt creation, retrieval, updates and returns,
        including stock management and ownership validation.
        """
        self.cart_item_table = TablesManager.cart_item_table
        self.cart_table = TablesManager.cart_table
        self.receipt_table = TablesManager.receipt_table
        self.product_table = TablesManager.product_table
        self.engine = TablesManager.engine

    def create_receipt(
        self,
        id_cart: int,
        id_address: int,
        id_payment: int,
        id_user: int,
        state: str = "paid",
    ):
        """
        Create a receipt from an active cart.
        Validates ownership, updates product stock, marks cart as bought
        and creates a new active cart for the user.

        :param id_cart: Cart ID
        :param id_address: Address ID
        :param id_payment: Payment method ID
        :param id_user: User ID
        :param state: Initial receipt state (default: paid)
        :return: Newly created receipt ID
        """
        with self.engine.connect() as conn:
            if not _verify_user_own_cart(conn, id_user, id_cart=id_cart):
                raise APIException(
                    f"Cart id:{id_cart} not owned by user or not exist", 403
                )
            if not _verify_user_own_address(conn, id_address, id_user):
                raise APIException(
                    f"Address id:{id_address} not owned by user or not exist", 403
                )
            if not _verify_user_own_payment(conn, id_payment, id_user):
                raise APIException(
                    f"Payment id:{id_payment} not owned by user or not exist", 403
                )
            stmt_product = (
                select(
                    self.cart_item_table.c.id_product,
                    self.cart_item_table.c.amount.label("amount_bought"),
                    self.product_table.c.amount.label("actual_amount"),
                )
                .select_from(self.cart_item_table)
                .join(
                    self.product_table,
                    self.product_table.c.id == self.cart_item_table.c.id_product,
                )
                .where(self.cart_item_table.c.id_cart == id_cart)
            )

            products = conn.execute(stmt_product).mappings().all()

            if not products:
                raise APIException(f"Cart id:{id_cart} not found or has no items", 404)
            products_with_stock = []
            for row in products:
                new_amount = row["actual_amount"] - row["amount_bought"]
                if new_amount < 0:
                    raise APIException(
                        f"Not enough products available: {row['actual_amount']}, requested: {row['amount_bought']} for product id: {row['id_product']}",
                        400,
                    )
                products_with_stock.append((row["id_product"], new_amount))
            stmt_create = (
                insert(self.receipt_table)
                .returning(self.receipt_table.c.id)
                .values(
                    id_cart=id_cart,
                    id_address=id_address,
                    id_payment=id_payment,
                    state=state,
                )
            )
            id_new_receipt = conn.execute(stmt_create).scalar()
            for id_product, new_amount in products_with_stock:
                stmt_update_product = (
                    update(self.product_table)
                    .where(self.product_table.c.id == id_product)
                    .values(amount=new_amount)
                )
                conn.execute(stmt_update_product)
            stmt_update_cart = (
                update(self.cart_table)
                .where(self.cart_table.c.id == id_cart)
                .values(state="bought")
            )
            result = conn.execute(stmt_update_cart)
            if result.rowcount == 0:
                raise APIException(f"Could not update the cart state", 500)
            stmt_create_cart = insert(self.cart_table).values(
                id_user=id_user, state="active"
            )
            result = conn.execute(stmt_create_cart)
            if result.rowcount == 0:
                raise APIException(f"Could not created new active cart state", 500)
            if id_new_receipt is None:
                raise APIException("Could not create receipt", 500)
            conn.commit()
        return id_new_receipt

    def get_data(
        self,
        id: int | None = None,
        id_user: int | None = None,
        id_cart: int | None = None,
        id_address: int | None = None,
        id_payment: int | None = None,
        entry_date: str | None = None,
        state: str | None = None,
    ):
        """
        Create a receipt from an active cart.
        Validates ownership, updates product stock, marks cart as bought
        and creates a new active cart for the user.

        :param id_cart: Cart ID
        :param id_address: Address ID
        :param id_payment: Payment method ID
        :param id_user: User ID
        :param state: Initial receipt state (default: paid)
        :return: Newly created receipt ID
        """
        conditions = _filter_locals(
            self.receipt_table,
            locals(),
            exclude=(
                "self",
                "id_user",
            ),
        )
        with self.engine.connect() as conn:
            if id_user is not None and id is not None:
                if not _verify_user_own_cart(
                    conn, id, id_user, table=self.receipt_table
                ):
                    raise APIException(f"Receipt id:{id} does not exist", 403)
            if entry_date is not None:
                self.__validate_date_str(entry_date)

            stmt = select(self.receipt_table)
            if conditions:
                stmt = stmt.where(and_(*conditions))
            result = conn.execute(stmt).mappings().all()
        if result:
            return [dict(row) for row in result]
        error_msg = (
            f"Receipt id:{id} not found"
            if id is not None
            else "No receipts found matching criteria"
        )
        raise APIException(error_msg, 404)

    def update_data(self, id: int, state: str, id_user: int | None = None):
        """
        Retrieve receipts based on provided filters.

        :param id: Receipt ID
        :param id_user: User ID
        :param id_cart: Cart ID
        :param id_address: Address ID
        :param id_payment: Payment method ID
        :param entry_date: Entry date (YYYY-MM-DD)
        :param state: Receipt state
        :return: List of receipts
        """
        with self.engine.connect() as conn:
            stmt_get_cart_id = select(self.receipt_table.c.id_cart).where(
                self.receipt_table.c.id == id
            )
            id_cart = conn.execute(stmt_get_cart_id).scalar()
            if not _verify_user_own_cart(conn, id_user, id_cart=id_cart):
                raise APIException(f"Cart id:{id} not owned by user or not exist", 403)
            stmt = (
                update(self.receipt_table)
                .where(self.receipt_table.c.id == id)
                .values(state=state)
            )
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise APIException(f"Receipt id:{id} not exist", 404)
            conn.commit()
        return True

    def return_receipt(self, id: int, id_user: int):
        """
        Update the state of a receipt.
        Validates that the receipt belongs to the user's cart.

        :param id: Receipt ID
        :param state: New receipt state
        :param id_user: User ID
        :return: True if updated successfully
        """
        with self.engine.connect() as conn:
            if not _verify_user_own_cart(conn, id_user, id, table=self.receipt_table):
                raise APIException(
                    f"Receipt id:{id} not owned by user or not exist", 403
                )
            stmt_join = (
                select(
                    self.cart_item_table.c.id_product,
                    self.cart_item_table.c.amount.label("amount_bought"),
                    self.product_table.c.amount.label("actual_amount"),
                    self.receipt_table.c.state,
                )
                .select_from(self.receipt_table)
                .join(
                    self.cart_item_table,
                    self.receipt_table.c.id_cart == self.cart_item_table.c.id_cart,
                )
                .join(
                    self.product_table,
                    self.product_table.c.id == self.cart_item_table.c.id_product,
                )
                .where(self.receipt_table.c.id == id)
            )
            products = conn.execute(stmt_join).mappings().all()
            if products[0]["state"] == "returned":
                raise APIException(f"Receipt id{id}, is already returned", 400)
            for row in products:
                new_amount = row["actual_amount"] + row["amount_bought"]
                stmt_update_product = (
                    update(self.product_table)
                    .where(self.product_table.c.id == row["id_product"])
                    .values(amount=new_amount)
                )
                conn.execute(stmt_update_product)
            stmt_update_receipt = (
                update(self.receipt_table)
                .where(self.receipt_table.c.id == id)
                .values(state="returned")
            )
            conn.execute(stmt_update_receipt)
            conn.commit()
        return True

    def __validate_date_str(self, date_str: str):
        """
        Validate date format (YYYY-MM-DD).

        :param date_str: Date string
        :raises APIException: If date format is invalid
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise APIException("Entry date in receipt is not valid", 400)
