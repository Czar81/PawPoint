from sqlalchemy import insert


class DbOrderManager:
    """
    Database manager for checkout orders.
    Handles order creation and retrieval.
    """

    def __init__(self, TablesManager):
        """
        Initialize with table references from TablesManager.

        :param TablesManager: TablesManager instance
        """
        self.order_table = TablesManager.order_table
        self.order_item_table = TablesManager.order_item_table
        self.engine = TablesManager.engine

    def create_order(self, customer, products, total, id_user=None):
        """
        Create a new order with its items.

        :param customer: Dict with name, email, address
        :param products: List of dicts with id, name, price, quantity, subtotal
        :param total: Order total amount
        :param id_user: Optional user ID if authenticated
        :return: Newly created order ID
        """
        with self.engine.connect() as conn:
            stmt_order = (
                insert(self.order_table)
                .returning(self.order_table.c.id)
                .values(
                    id_user=id_user,
                    customer_name=customer["name"],
                    customer_email=customer["email"],
                    customer_phone=customer.get("phone"),
                    customer_address=customer["address"],
                    total=total,
                )
            )
            id_order = conn.execute(stmt_order).scalar()

            for item in products:
                stmt_item = insert(self.order_item_table).values(
                    id_order=id_order,
                    id_product=item["id"],
                    name=item["name"],
                    price=item["price"],
                    quantity=item["quantity"],
                    subtotal=item["subtotal"],
                )
                conn.execute(stmt_item)

            conn.commit()
        return id_order
