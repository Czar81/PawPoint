from sqlalchemy import insert, select, delete, update, and_
from src.db.utils_db.helpers import _filter_locals
from src.utils.api_exception import APIException


class DbAddressManager:
    """
    Database manager for user addresses.
    Handles CRUD operations scoped to the owning user.
    """

    def __init__(self, TablesManager):
        """
        Initialize the address database manager.

        :param TablesManager: Instance containing database tables and engine
        """
        self.address_table = TablesManager.address_table
        self.engine = TablesManager.engine

    def insert_data(self, id_user: int, location: str):
        """
        Create a new address for a user.

        :param id_user: User ID
        :param location: Address location string
        :return: Newly created address ID
        """
        stmt = (
            insert(self.address_table)
            .returning(self.address_table.c.id)
            .values(id_user=id_user, location=location)
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt).scalar()
            if result is None:
                raise APIException("Could not create address", 500)
            conn.commit()
        return result

    def get_data(
        self,
        id_user: int,
        id: int | None = None,
        location: str | None = None,
    ):
        """
        Retrieve addresses belonging to a user.

        :param id_user: User ID (required)
        :param id: Optional address ID
        :param location: Optional location filter
        :return: List of addresses
        """
        conditions = _filter_locals(self.address_table, locals())
        stmt = select(self.address_table)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        with self.engine.connect() as conn:
            result = conn.execute(stmt).mappings().all()
            if not result:
                return "Not address found"
            return [dict(row) for row in result]

    def update_data(self, id_user: int, id_address: int, location: str):
        """
        Update an existing address.
        Only the owner of the address can update it.

        :param id_user: User ID
        :param id_address: Address ID
        :param location: New address location
        :return: True if updated successfully
        """
        with self.engine.connect() as conn:
            stmt = (
                update(self.address_table)
                .where(
                    and_(
                        self.address_table.c.id == id_address,
                        self.address_table.c.id_user == id_user,
                    )
                )
                .values(location=location)
            )
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise APIException(f"Address id:{str(id_address)} not exist", 404)
            conn.commit()
        return True

    def delete_data(self, id_user: int, id_address: int):
        """
        Delete an address owned by a user.

        :param id_user: User ID
        :param id_address: Address ID
        :return: True if deleted successfully
        """
        with self.engine.connect() as conn:
            stmt = delete(self.address_table).where(
                and_(
                    self.address_table.c.id == id_address,
                    self.address_table.c.id_user == id_user,
                )
            )
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise APIException(f"Address id:{str(id_address)} not exist", 404)
            conn.commit()
        return True
