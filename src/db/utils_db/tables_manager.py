from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
)
from dotenv import load_dotenv
from datetime import date
from os import environ

load_dotenv()


class TablesManager:
    """
    Centralized manager for SQLAlchemy engine and table definitions.

    This class initializes the database engine and defines all database tables
    used by the application. It also provides a helper method to create
    all tables in the database.
    """

    def __init__(self, url=environ.get("URL_POSTGRES")):
        """
        Initialize the database engine.

        :param url: Database connection URL
        """
        self.engine = create_engine(url)

    metadata_obj = MetaData()
    product_table = Table(
        "product",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("sku", String(20), nullable=False, unique=True),
        Column("name", String(30), nullable=False),
        Column("price", Integer, nullable=False),
        Column("amount", Integer, nullable=False),
        CheckConstraint("price > 0", name="chk_price_positive"),
        CheckConstraint("amount >= 0", name="chk_amount_non_negative"),
    )
    user_table = Table(
        "user",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("username", String(30), nullable=False),
        Column("password", String, nullable=False),
        Column("role", String(10), server_default="user"),
    )
    cart_table = Table(
        "cart",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("id_user", Integer, ForeignKey("user.id", ondelete="CASCADE")),
        Column("state", String(10), server_default="active"),
    )
    address_table = Table(
        "address",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("id_user", Integer, ForeignKey("user.id", ondelete="CASCADE")),
        Column("location", String(30), nullable=False),
    )
    payment_table = Table(
        "payment",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("id_user", Integer, ForeignKey("user.id", ondelete="CASCADE")),
        Column("type_data", String(10), nullable=False),
        Column("data", String(30)),
    )
    cart_item_table = Table(
        "cart_item",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("id_cart", Integer, ForeignKey("cart.id", ondelete="CASCADE")),
        Column("id_product", Integer, ForeignKey("product.id", ondelete="RESTRICT")),
        Column("amount", Integer, nullable=False),
        CheckConstraint("amount > 0", name="chk_amount_plus_zero"),
        UniqueConstraint("id_cart", "id_product", name="uk_cart_item_unique"),
    )
    receipt_table = Table(
        "receipt",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("id_cart", Integer, ForeignKey("cart.id", ondelete="RESTRICT")),
        Column("id_address", Integer, ForeignKey("address.id", ondelete="RESTRICT")),
        Column("id_payment", Integer, ForeignKey("payment.id", ondelete="RESTRICT")),
        Column("entry_date", String(10), server_default=str(date.today())),
        Column("state", String(10), server_default="paid"),
    )

    def create_tables(self):
        """
        Create all database tables defined in metadata.

        This method should be executed once during application setup.
        """
        self.metadata_obj.create_all(self.engine)
