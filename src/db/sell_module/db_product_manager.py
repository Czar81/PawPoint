from sqlalchemy import insert, select, delete, update, and_
from src.utils.api_exception import APIException
from src.db.utils_db.helpers import _filter_locals
from src.utils.helpers import filter_values


class DbProductManager:
    """
    Database manager for products.
    Handles product creation, retrieval, updates and deletion.
    """

    def __init__(self, TablesManager):
        """
        Initialize the product database manager.

        :param TablesManager: Instance containing database tables and engine
        """
        self.product_table = TablesManager.product_table
        self.engine = TablesManager.engine

    def insert_data(self, sku: str, name: str, price: int, amount: int):
        """
        Insert a new product into the database.

        :param sku: Product SKU
        :param name: Product name
        :param price: Product price
        :param amount: Available stock amount
        :return: Newly created product ID
        """
        stmt = (
            insert(self.product_table)
            .returning(self.product_table.c.id)
            .values(sku=sku, name=name, price=price, amount=amount)
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt).scalar()
            if result is None:
                raise APIException("Could not create product", 500)
            conn.commit()
        return result

    def get_data(
        self,
        id: int | None = None,
        sku: str | None = None,
        name: str | None = None,
        price: int | None = None,
        amount: int | None = None,
    ):
        """
        Retrieve products based on optional filters.

        :param id: Product ID
        :param sku: Product SKU
        :param name: Product name
        :param price: Product price
        :param amount: Product stock amount
        :return: List of matching products
        """
        conditions = _filter_locals(self.product_table, locals())
        stmt = select(self.product_table)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        with self.engine.connect() as conn:
            result = conn.execute(stmt).mappings().all()
        if not result:
            return "Not found"
        return [dict(row) for row in result]

    def update_data(
        self,
        id_product: int,
        sku: str | None = None,
        name: str | None = None,
        price: int | None = None,
        amount: int | None = None,
    ):
        """
        Update an existing product.
        Only provided fields will be updated.

        :param id_product: Product ID
        :param sku: New SKU
        :param name: New name
        :param price: New price
        :param amount: New stock amount
        :return: True if updated successfully
        """
        values = filter_values(locals(), ("self", "id_product"))
        if not values:
            raise APIException("No provide any value", 400)
        stmt = (
            update(self.product_table)
            .where(self.product_table.c.id == id_product)
            .values(**values)
        )
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise APIException(f"Product id:{id_product} not exist", 404)
            conn.commit()
        return True

    def delete_data(self, id_product: int):
        """
        Delete a product by its ID.

        :param id_product: Product ID
        :return: True if deleted successfully
        """
        stmt = delete(self.product_table).where(self.product_table.c.id == id_product)
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            if result.rowcount == 0:
                raise APIException(f"Product id:{id_product} not exist", 404)
            conn.commit()
        return True
