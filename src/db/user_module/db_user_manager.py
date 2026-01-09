from sqlalchemy import insert, select, delete, update, and_
from src.utils.helpers import filter_values
from src.utils.api_exception import APIException


class DbUserManager:
    """
    Database manager for user-related operations.
    Handles CRUD operations for users.
    """

    def __init__(self, TablesManager):
        """
        Initialize the user database manager.

        :param TablesManager: Instance containing database tables and engine
        """

        self.user_table = TablesManager.user_table
        self.engine = TablesManager.engine

    def insert_data(self, username: str, password: str, role: str | None = None):
        """
        Create a new user in the database.

        :param username: User's username
        :param password: User's password
        :param role: Optional user role (admin/user)
        :return: Newly created user ID
        """
        values = filter_values(locals())
        stmt = insert(self.user_table).returning(self.user_table.c.id).values(**values)
        with self.engine.connect() as conn:
            result = conn.execute(stmt).scalar()
            if result is None:
                raise APIException("Could not create user", 500)
            conn.commit()
        return result

    def get_data(self, id_user: int | None = None):
        """
        Retrieve user data.

        :param id_user: Optional user ID to retrieve a single user
        :return: List of users or a specific user
        """
        stmt = select(self.user_table)
        if id_user is not None:
            stmt = stmt.where(self.user_table.c.id == id_user)
        with self.engine.connect() as conn:
            result = conn.execute(stmt).mappings().all()
            if result == []:
                return "Not users found"
            return [dict(row) for row in result]

    def get_user(self, username: str, password: str):
        """
        Retrieve a user ID using credentials.

        :param username: User's username
        :param password: User's password
        :return: User ID if found, otherwise None
        """
        stmt = (
            select(self.user_table)
            .where(self.user_table.c.username == username)
            .where(self.user_table.c.password == password)
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt).scalar()
            return result

    def get_role_by_id(self, id_user: int):
        """
        Retrieve the role of a user by ID.

        :param id_user: User ID
        :return: User role
        """
        stmt = select(self.user_table.c.role).where(self.user_table.c.id == id_user)
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
        if result == None:
            raise APIException("Id not allowed", 404)
        role = result.scalar()
        return role

    def update_data(
        self,
        id_user: int,
        username: str | None = None,
        password: str | None = None,
        role: str | None = None,
    ):
        """
        Update user data.

        :param id_user: User ID
        :param username: New username (optional)
        :param password: New password (optional)
        :param role: New role (optional)
        :return: True if updated successfully
        """
        values = filter_values(locals(), ("self", "id_user"))
        stmt = update(self.user_table).where(self.user_table.c.id == id_user)
        if values:
            stmt = stmt.values(**values)
        else:
            raise APIException("No provide any value", 400)
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise APIException(f"User id:{str(id_user)} not exist", 404)
            conn.commit()
        return True

    def delete_data(self, id_user: int):
        """
        Delete a user by ID.

        :param id_user: User ID
        :return: True if deleted successfully
        """
        stmt = delete(self.user_table).where(self.user_table.c.id == id_user)
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise APIException(f"User id:{str(id_user)} not exist", 404)
            else:
                conn.commit()
        return True
