from sqlalchemy import insert, select, delete, update, and_
from src.db.utils_db.helpers import _filter_locals
from src.utils.helpers import filter_values
from src.db.utils_db.verifies import _verify_user_own_payment
from src.utils.api_exception import APIException


class DbPaymentManager:
    """
    Database manager for payment methods.
    Handles CRUD operations and ownership validation.
    """

    def __init__(self, TablesManager):
        """
        Initialize the payment database manager.

        :param TablesManager: Instance containing database tables and engine
        """
        self.payment_table = TablesManager.payment_table
        self.engine = TablesManager.engine

    def insert_data(self, id_user: int, type_data: str, data: str):
        """
        Create a new payment method for a user.

        :param id_user: User ID
        :param type_data: Type of payment (e.g. card, paypal)
        :param data: Payment data (encrypted or masked)
        :return: Newly created payment ID
        """
        stmt = (
            insert(self.payment_table)
            .returning(self.payment_table.c.id)
            .values(id_user=id_user, type_data=type_data, data=data)
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt).scalar()
            if result is None:
                raise APIException("Could not create payment", 500)
            conn.commit()
        return result

    def get_data(
        self,
        id_user: int,
        id: int | None = None,
        type_data: str | None = None,
    ):
        """
        Retrieve payment methods for a user.

        :param id_user: User ID (required)
        :param id: Optional payment ID
        :param type_data: Optional payment type filter
        :return: List of payment methods
        """
        conditions = _filter_locals(self.payment_table, locals())
        stmt = select(self.payment_table)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        with self.engine.connect() as conn:
            result = conn.execute(stmt).mappings().all()
            if not result:
                return "Not payments found"
            return [dict(row) for row in result]

    def update_data(self, id: int, type_data: str, data: str, id_user: str):
        """
        Update an existing payment method.
        Only the owner of the payment method can update it.

        :param id: Payment ID
        :param type_data: New payment type
        :param data: New payment data
        :param id_user: User ID (ownership validation)
        :return: True if updated successfully
        """
        values = filter_values(locals(), ("self", "id", "id_user"))
        stmt = (
            update(self.payment_table)
            .where(
                and_(
                    self.payment_table.c.id == id,
                    self.payment_table.c.id_user == id_user,
                )
            )
            .values(**values)
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise APIException(f"Payment method id:{str(id)} not exist", 404)
            conn.commit()
        return True

    def delete_data(self, id: int, id_user: int):
        """
        Delete a payment method.
        Validates ownership before deletion.

        :param id: Payment ID
        :param id_user: User ID
        :return: True if deleted successfully
        """
        stmt = delete(self.payment_table).where(
            and_(self.payment_table.c.id == id, self.payment_table.c.id_user == id_user)
        )
        with self.engine.connect() as conn:
            if not _verify_user_own_payment(conn, id, id_user):
                raise APIException(f"Payment id:{id} not exist", 404)
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise APIException(f"Payment method id:{id} not exist", 404)
            conn.commit()
        return True
