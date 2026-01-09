# Database Documentation

## Overview
This document describes the database structure, and usage guidelines for the data base. It provides a clear view of how data is organized, and stored.

## Architecture Overview
```bash
src/db/
│── __init__.py
│
│── sell_module/
│   ├── db_cart_manager.py
│   ├── db_cart_item_manager.py
│   ├── db_product_manager.py
│   └── db_receipt_manager.py
│
│── user_module/
│   ├── db_user_manager.py
│   ├── db_address_manager.py
│   └── db_payment_manager.py

```

## Index

- [Schema Design](#schema-design)
  - [Entity Relationship Diagram](#entity-relationship-diagram)
  - [Table Structures](#table-structures)
    - [user](#user-table)
    - [product](#product-table)
    - [cart](#cart-table)
    - [cart item](#cart_item-table)
    - [address](#address-table)
    - [payment](#payment-table)
    - [receipt](#receipt-table)
  - [Relationships](#relationships)
- [Database Manager](#database-manager)
  - [Sell Module](#sell-module)
    - [Product Manager](#product-manager)
    - [Cart Manager](#cart-manager)
    - [Cart Item Manager](#cart-item-manager)
    - [Receipt Manager](#receipt-manager)
  - [User Module](#user-module)
    - [User Manager](#user-manager)
    - [Address Manager](#address-manager)
    - [Payment Manager](#payment-manager)

## Schema Design

Below is the visual representation of the database structure:

![TABLE_diagram](./diagrams/diagrama_tables.png)

### Entity Relationship Diagram

![ER_diagram](./diagrams/diagrama_er.png)

### Table manager

This defines the relational database schema for the PawPoint system using SQLAlchemy Core.
It centralizes table definitions, constraints, and relationships, and provides a utility class to initialize the database structure.

The database connection URL is loaded from environment variables using python-dotenv.

```python
URL_POSTGRES=postgresql://username:password@localhost:5432/database_name
```

#### Purpose

The TablesManager class is responsible for:

- Creating the SQLAlchemy engine
- Holding metadata definitions
- Initializing all database tables

Usage Example:

```py
from tables import TablesManager

manager = TablesManager()
manager.create_tables()
manager.engine
manager.user_table
```

---

### Table Structures

> [!NOTE]
> Import managers from src.db

#### user table

**Description:** Stores user account information and authentication data.

| Column   | Type    | Constraints | Description                |
| -------- | ------- | ----------- | -------------------------- |
| id       | INTEGER | PRIMARY KEY | Unique user identifier     |
| name     | VARCHAR | NOT NULL    | User's full name           |
| password | VARCHAR | NOT NULL    | Hashed password            |
| role     | VARCHAR | NOT NULL    | User role: 'user', 'admin' |

##### Business Rules:

- Password must be hashed before storage
- Role determines access permissions
- Valid roles: 'user' (default), 'admin'

---

#### product table

**Description:** Product catalog with inventory management.

| Column | Type    | Constraints                   | Description                       |
| ------ | ------- | ----------------------------- | --------------------------------- |
| id     | INTEGER | PRIMARY KEY                   | Unique product identifier         |
| sku    | VARCHAR | UNIQUE, NOT NULL              | Stock Keeping Unit (product code) |
| name   | VARCHAR | NOT NULL                      | Product name                      |
| price  | INTEGER | NOT NULL, CHECK (price > 0)   | Product price in cents            |
| amount | INTEGER | NOT NULL, CHECK (amount >= 0) | Available stock quantity          |

##### Business Rules:

- Price is stored in cents to avoid floating-point precision issues
- Amount represents current inventory stock
- Products with amount = 0 are out of stock
- SKU must be unique across all products
- Price must always be positive (greater than 0)
- Stock (amount) cannot be negative
- When product is added to cart, verify sufficient stock
- Stock is decremented when receipt is generated, not when added to cart

---

#### cart table

**Description:** Shopping carts for users to collect products before checkout.

| Column  | Type    | Constraints                | Description                               |
| ------- | ------- | -------------------------- | ----------------------------------------- |
| id      | INTEGER | PRIMARY KEY                | Unique cart identifier                    |
| id_user | INTEGER | FOREIGN KEY, NOT NULL      | Reference to user who owns the cart       |
| state   | VARCHAR | NOT NULL, DEFAULT 'active' | Cart status: 'active','bought', 'archive' |

##### Business Rules:

- Each user should have just one 'active' cart
- State changes: active to bought, after receipt was generated
- When user creates new cart, previous active cart automatic will be marked archive
- When receipt is generated, also generate a new active cart

---

#### cart_item table

**Description:** Individual items within shopping carts (junction table between cart and product).

| Column     | Type     | Constraints           | Description                 |
| ---------- | -------- | --------------------- | --------------------------- |
| id         | INTEGER  | PRIMARY KEY           | Unique cart item identifier |
| id_cart    | INTEGER  | FOREIGN KEY, NOT NULL | Reference to cart           |
| id_product | INTEGER  | FOREIGN KEY, NOT NULL | Reference to product        |
| amount     | INTERGER | NOT NULL              | Quantity of product         |

**Business Rules:**

- Validate product stock availability before adding to cart
- Amount (quantity) must be positive integer (> 0)
- Amount cannot exceed available product stock
- Cart items are automatically deleted when cart is deleted (CASCADE)
- Same product cannot appear twice in one cart (enforce with UNIQUE constraint)

---

#### address table

**Description:** User delivery addresses for shipping.

| Column   | Type    | Constraints           | Description                            |
| -------- | ------- | --------------------- | -------------------------------------- |
| id       | INTEGER | PRIMARY KEY           | Unique address identifier              |
| id_user  | INTEGER | FOREIGN KEY, NOT NULL | Reference to user who owns the address |
| location | VARCHAR | NOT NULL              | Full address string                    |

**Business Rules:**

- Users can have multiple saved addresses
- Location should include complete address: street, city, state, postal code, country
- Addresses cannot be deleted if used in receipts (preserve history)
- Users must have at least one address before checkout
- When user is deleted, their addresses are deleted (CASCADE)

---

#### payment table

**Description:** User payment methods (credit cards, PayPal, etc.).

| Column  | Type    | Constraints           | Description                                         |
| ------- | ------- | --------------------- | --------------------------------------------------- |
| id      | INTEGER | PRIMARY KEY           | Unique payment method identifier                    |
| id_user | INTEGER | FOREIGN KEY, NOT NULL | Reference to user who owns the payment method       |
| type    | VARCHAR | NOT NULL              | Payment type: 'credit_card', 'debit_card', 'paypal' |
| data    | VARCHAR | NOT NULL              | Tokenized payment data                              |

**Business Rules:**

- **CRITICAL:** NEVER store raw credit card numbers (PCI DSS compliance)
- Valid payment types: 'credit_card', 'debit_card', 'paypal', 'bank_transfer'
- Data field stores ONLY encrypted/tokenized information
- Payment methods cannot be deleted if used in receipts (preserve history)
- Users must have at least one payment method before checkout
- When user is deleted, their payment methods are deleted (CASCADE)

---

#### receipt table

**Description:** Purchase receipts generated from completed carts.

| Column     | Type      | Constraints                         | Description                    |
| ---------- | --------- | ----------------------------------- | ------------------------------ |
| id         | INTEGER   | PRIMARY KEY                         | Unique receipt identifier      |
| id_cart    | INTEGER   | FOREIGN KEY, UNIQUE, NOT NULL       | Reference to cart (one-to-one) |
| id_address | INTEGER   | FOREIGN KEY, NOT NULL               | Shipping address used          |
| id_payment | INTEGER   | FOREIGN KEY, NOT NULL               | Payment method used            |
| entry_date | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Purchase date                  |
| state      | VARCHAR   | NOT NULL, DEFAULT 'paid'            | Receipt status                 |

**Business Rules:**

- One cart can generate multiple receipts
- Receipt is immutable once created (cannot be modified, only state changes)
- Valid states: 'paid', 'cancelled', 'returned'
- Receipts CANNOT be deleted (ON DELETE RESTRICT) to maintain order history
- Entry_date is automatically set to current timestamp
- When receipt is created, cart state automatic change to 'archive', and can be use to generade another receipt
- When receipt is created, product stock automatic decremented
- Refunds restore stock automatically

---

### Relationships

| Relationship        | Type | Description                                          |
| ------------------- | ---- | ---------------------------------------------------- |
| User → Cart         | 1:N  | One user can have multiple shopping carts            |
| User → Address      | 1:N  | One user can have multiple delivery addresses        |
| User → Payment      | 1:N  | One user can have multiple payment methods           |
| Cart → Cart Item    | 1:N  | One cart contains multiple items (products)          |
| Product → Cart Item | 1:N  | One product can be in multiple carts via cart_item   |
| Cart → Receipt      | 1:1  | One completed cart generates exactly one receipt     |
| Address → Receipt   | 1:N  | One address can be used for multiple receipts        |
| Payment → Receipt   | 1:N  | One payment method can be used for multiple receipts |

## Database Manager

**Overview**
The Database Manager layer provides a clean abstraction over database operations, organized into two main modules: Sell Module (e-commerce functionality) and User Module (user management).
Each manager needs a instants of TableManager.
All manager instants can be get from src/extensions.py

### Sell Module

Handles all e-commerce operations including products, carts, and receipts.

#### Product Manager

Location: src/db/sell/product_manager.py
Purpose: Manages product catalog and inventory operations.

##### _Methods_

```python
insert_data(sku, name, price, amount)
```

Creates a new product in the catalog.
Parameters:

- `sku` (str): Unique product code
- `name` (str): Product name
- `price` (int): Price in cents (e.g., 1999 for $19.99)
- `amount` (int): Initial stock quantity

Returns: Product ID (int)

Raises:

- `IntegrityError`: If SKU already exists, estatus code: 400
- `APIException`: As generic if could not create product, estatus code: 500

Example Usage:

```python
# Import requierd libraries and Initialize
from db.utils_db.tables_manager import TablesManager
from src.db import DbProductManager

tm = TablesManager()
pm = DbProductManager(tm)

# The next examples will omit the above lines
product_id = pm.insert_data(
    sku="LAPTOP-001",
    name="Gaming Laptop",
    price=149999,  # $1,499.99
    amount=50,
)
# Return 143
```

---

```python
get_data(id_product, sku, name, price, amount)
```

Retrieves product details by the prams below.
Parameters:

- `id`: (int | None = None), Unique product id
- `sku`: (str | None = None), Unique product code
- `name`: (str | None = None), Product name
- `price`: (int | None = None), Price in cents (e.g., 1999 for $19.99)
- `amount`: (int | None = None), Initial stock quantity

Returns: Dict with product data or "Not found"

Example Usage:

```py
#Get all products
products = pm.get_data()
# Returns: {
#     'id': 123,
#     'sku': 'LAPTOP-001',
#     'name': 'Gaming Laptop',
#     'price': 149999,
#     'amount': 50,
#     'description': 'High-performance gaming laptop'
# }

#Get products filter by price
products = pm.get_data(price=100099)
# Returns: "Not found"
```

---

```python
update_data(id_product, sku, name, price, amount)
```

Updates product atributes below.

Parameters:

- `id_product`: (int), Unique product id
- `sku`: (str | None = None), Unique product code
- `name`: (str | None = None), Product name
- `price`: (int | None = None), Price in cents (e.g., 1999 for $19.99)
- `amount`: (int | None = None), Initial stock quantity

Returns: True

Raises:

- `ValueError`: If operation would result in negative stock, estatus code: 400
- `APIException`: As generic if product not exist, estatus code: 404

Example Usage:

```py
new_stock = pm.update_data(123, amount=50)
# Returns: True
```

---

```py
delete_data(id_product)
```

Parameters:

- `id_product` (int), Unique product id

> [!Note]
> Cannot delete products that are in receipt (RESTRICT constraint), so needs to be set to amount=0

Returns: True

Example Usage:

```py
new_stock = pm.delete_data(123)
# Returns: True
```

---

#### Cart Manager

Location: src/db/sell/cart_manager.py

Purpose: Manages shopping cart operations.

##### _Methods_

```py
insert_data(id_user)
```

Creates a new shopping cart for a user.

Parameters:

- `id_user` (int): User ID

Returns: Cart ID (int)

Raise:

- `APIException`: Raise as generic with "Could not create cart", estatus code: 500

Example Usage:

```py
# Import requierd libraries and Initialize
from db.utils_db.tables_manager import TablesManager
from src.db import CartManager

tm = TablesManager()
cm = CartManager(tm)

# The next examples will omit the above lines
id_cart = cm.insert_data(id_user=1)
# Returns: 456(ID)
```

---

```py
get_data(id_user, id_cart, state)
```

Retrieves cart details.

Parameters:

- `id_user`: (int), User ID
- `id_cart`: (int | None = None), : Cart ID
- `state`: (str | None = None), State of cart

Returns: Dict with carts, could be filter by id_cart o state

Example Usage:

```py
cart = cm.get_cart(id_user=1, state="archive")
# Returns: {
#     'id': 456,
#     'id_user': 1,
#     'state': 'archive',
# }
```

---

```py
get_cart_with_items(id_user)
```

Retrieves cart details with its items.

Parameters:

- `id_user` (int): User ID
- `id_cart`: (int | None = None), Cart ID
- `active`: (bool = True), If need active the cart

> [!IMPORTANT]
> If use id_cart also use active=False. Do NOT use id_cart with active blank or True

Returns: Dict with cart data including items

Example Usage:

```py
cart = cm.get_cart_with_items(id_user=1)
# Returns: {
#     'id': 500,
#     'id_user': 1,
#     'state': 'active',
#     'items': [
#         {'id':32, 'id_cart': 500,'id_product': 123, 'amount': 2},
#         {'id':42, 'id_cart': 500,'id_product': 124, 'amount': 1}
#     ],
# }
```

---

```py
update_data(id_cart, state, id_user)
```

Updates cart from archive or bought, preferably to active, and currect active became archive

Parameters:

- id_cart (int): Cart ID
- State (str): New state
- id_user (int): User ID

Returns: True

Raises:

- `APIException`: If cart not exist, estatus code: 404
- `APIException`: If just have one cart(active)

Example Usage:

```py
updated = cm.update_data(id_cart=500, state="active", id_user=1)
# Returns: True
```

> [!IMPORTANT]
> This function updates only carts that are not in the active status, so at least two carts must exist.

---

```py
delete_data(id_cart, id_user)
```

Delete cart

> [!Note]
> Cannot delete carts that are in receipt (RESTRICT constraint)

Parameters:

- `id_cart`(int): Cart ID
- `id_user`(int): User ID

Returns: True

Raises:

- `APIException`: If the carts state is active, status code: 400
- `APIException`: If could not find the cart, status code: 404

Example Usage:

```py
deleted = cm.delete_data(id_cart=34, id_user=1)
# Returns: True
```

---

#### Cart Item Manager

Location: src/db/sell/cart_item_manager.py
Purpose: Low-level cart item operations (typically used by CartManager).

> [!NOTE]
> There is not a method get in this manager. To get the items must use get_data from cart manager

##### Methods

```PY
create_cart_item(id_cart, id_product, amount)
```

Creates a cart item.

Parameters:

- id_cart: (int), Cart ID
- id_product: (int), Product ID
- amount: (int), Amount of product to buy
- id_user: (int), User ID

Returns: Cart Item ID

Example Usage:

```py
# Import requierd libraries and Initialize
from db.utils_db.tables_manager import TablesManager
from src.db import DbCartItemsManager

tm = TablesManager()
cim = DbCartItemsManager(tm)

# The next examples will omit the above lines
id_item = cim.insert_data(id_cart=400, id_product=123, amount=1, id_user=1)
#returns: 1 (ID)
```

---

```py
update_data(id_item, amount, id_user)
```

Updates the amount of product in cart.

Parameters:

- id_item: (int), Cart Item ID
- amount: (int), New mount of product to buy
- id_user: (int), User ID

Returns: True

Raises:

- `APIException`: If item not exits, status code: 404
- `APIException`: If user do not own item, status code: 403

Example Usage:

```py
updated = cim.update_data(id_item=1, amount=5, id_user=1)
# Returns: True
```

---

```py
delete_cart_item(id_item, id_user)
```

Removes a product from cart.

Parameters:

- `id_item`(int): Cart Item ID
- `id_user`(int): User ID

Returns: True

Example Usage:

```py
deleted = cim.delete_data(id_item=1, id_user=1)
# Returns: True
```

---

#### Receipt Manager

Location: db/sell/receipt_manager.py
Purpose: Manages purchase receipts and order history.

##### Method

```py
create_receipt(id_cart, id_address, id_payment, state, id_user)
```

Generates a receipt from a completed cart.

Parameter:

- `id_cart`: (int), Cart ID
- `id_address`: (int), Shipping address ID
- `id_payment`: (int), Payment method ID
- `id_user`: (int), User ID
- `state`: (str | None = None), State of the cart, default _paid_

Returns: Receipt ID

Raises:

- `APIException`: If user not own cart, address or payment. Status code: 403
- `APIException`: If cart is empty. Status code: 400
- `APIException`: If not enough products avaible to buy. Status code: 400
- `APIException`: If could not update the cart state. Status code: 500
- `APIException`: If could not created new active cart state. Status code: 500
- `APIException`: If could not create receipt. Status code: 500

Example Usage:

```py
# Import requierd libraries and Initialize
from db.utils_db.tables_manager import TablesManager
from src.db import DbReceiptManager

tm = TablesManager()
rm = DbReceiptManager(tm)

# The next examples will omit the above lines
id_receipt = rm.create_receipt(id_cart=400, id_address=12, id_payment=43, id_user=1)
# Returns: 1 (ID)
```

---

```py
get_data(id, id_user,id_cart, id_address, id_payment,entry_date,state)
```

Retrieves receipt details. Could obtain receipt filter with below params.

Parameters:

- `id_user`: (int), User ID
- `id`: (int | None = None), Receipt ID
- `id_cart`: (int | None = None), Cart ID
- `id_address`: (int | None = None), Address ID
- `id_payment`: (int | None = None), Payment ID
- `entry_date`: (str | None = None), Date that receipt was created. Default today()
- `state`: (str | None = None), State of receipt

Returns: Dict with complete receipt data

Example Usage:

```py
receipts = rm.get_data(id_user=1, entry_date="2025-12-15")
# Returns: [
#   {
#   "id": 1,
#   "id_address": 12,
#   "id_cart": 400,
#   "id_payment": 43,
#   "state": "paid",
#   "entry_date": 2025-12-15,
#   }
#]
```

---

```py
update_data(id, state, id_user)
```

Updates receipt state.

Parameters:

- `id`: (int | None = None), Receipt ID
- `state`: (str), State of receipt
- `id_user`: (int), User ID

Returns: True

Example Usage:

```py
updated = update_data(id=400, state="cancelled", id_user=1)
# Returns: True
```

---

```py
return_receipt(id, id_user)
```

Returns receipt and restores stock.
Parameters:

- `id`: (int | None = None), Receipt ID
- `id_user`: (int), User ID
- `id_cart`: (int | None = None), Cart ID

Returns: True

Raise:

- `APIException`: IF Receipt not exist or not own for user. Status code: 403
- `APIException`: IF Receipt is already returned. Status code: 400

Example Usage:

```py
returned = return_receipt(id=400, id_user=1)
# Returns: True
```

---

### User Module

Handles user management, addresses, and payment methods.

#### User Manager

Location: db/user/user_manager.py

Purpose: Manages user accounts.

##### Method

```py
insert_data(username, password, role)
```

Creates a new user account.

Parameters:

- `username`: (str), User name
- `password`: (str), Plain text password (will be hashed)
- `role`: (str | None = None), Role of the user. Default will be "user".

Returns: User id

Raises:

- `APIException`: If Could not create user. Status code: 500

Example Usage:

```py
# Import requierd libraries and Initialize
from db.utils_db.tables_manager import TablesManager
from src.db import DbUserManager

tm = TablesManager()
um = DbUserManager(tm)

# The next examples will omit the above lines
id_user = um.insert_data(username="jonhDoe", password="5e884898da28047151d0e56f8dc6292773603d0d6aabbddc7f6f1a54ef32f5bd")
# Returns: 1 (ID)
```

---

```py
get_data(id_user)
```

Retrieves user information.

Parameters:

- `id_user`: (int | None = None), User ID

Returns: Dict with users data

Example Usage:

```py
users = um.get_data()
# Returns:[
#  {
#   'id': 1,
#   'username': 'jonhDoe',
#   'password':'5e884898da28047151d0e56f8dc6292773603d0d6aabbddc7f6f1a54ef32f5bd',
#   'role': 'user'
#   }
# ]
```

---

```py
get_user(username, password)
```

Authenticates user credentials.

Parameters:

- `username`: (str), User name
- `password`: (str), Password hashed

Returns: Dict with user data, after authentify

Example Usage:

```py
user = um.get_user(username='jonhDoe', password='5e884898da28047151d0e56f8dc6292773603d0d6aabbddc7f6f1a54ef32f5bd')
# Returns:[
#  {
#   'id': 1,
#   'username': 'jonhDoe',
#   'password':'5e884898da28047151d0e56f8dc6292773603d0d6aabbddc7f6f1a54ef32f5bd',
#   'role': 'user'
#   }
# ]
```

---

```py
get_role_by_id(id_user)
```

Retrieves role of user.

Parameters:

- `id_user`: (int), User ID

Returns: Role str of user

Raises:

- `APIException`: If could find role for id provided. Status code: 404

Example Usage:

```py
user_role = um.get_role_by_id(id_user=1)
# Returns: "user"
```

---

```py
update_data(id_user, username, password, role)
```

Update user information.

Parameters:
- `id_user`: (int), User ID
- `username`: (str | None = None), New user name
- `password`: (str | None = None), New  password, need to be hash
- `role`: (str | None = None), New role

Returns: True

Raises:
- `APIException`: If nor provide any value. Status code: 400
- `APIException`: If could not update the user. Status code: 404

Example Usage:

```py
# Updating password
updated=um.update_data(id_user=1, password="9b0d3d4c0f3a5b1a4f2c9e9c8b8d2f7a6f1d4c6a9e0b5a3d2c1f8e7a4b6d9e2")
# Returns: True
```

---

```py
delete_data(id_user)
```

Delete user.

Parameters:
- `id_user`: (int), User ID

Returns: True

Raises:
- `APIException`: If could not update the user. Status code: 404

Example Usage:

```py
deleted=um.delete_data(id_user=1)
# Returns: True
```

---

#### Address Manager

Location: db/user/address_manager.py

Purpose: Manages user shipping addresses.

##### Method

```py
insert_data(id_user, location)
```

Create an address.

Parameters:
- `id_user`: (int), User ID
- `location`: (str), Full address string 

Returns: Address ID

Raises:
- `APIException`: If could not create the address. Status code: 500

Example Usage:

```py
from db.utils_db.tables_manager import TablesManager
from src.db import DbAddressManager

tm = TablesManager()
am = DbAddressManager(tm)

# The next examples will omit the above lines
id_address = am.insert_data(id_user=1, location="742 Los Almendros Street, Apartment 3B, Santa Aurora Neighborhood, North District")
# Returns: 1 (ID)
```

---

```py
get_data(id, id_user, location)
```

Get users address. Could be filter by parameter id and location.

Parameters:
- `id_user`: (int),
- `id`: (int | None = None),
- `location`: (str | None = None),

Returns: Dict with addresses data

Raises:

Example Usage:

```py
addresses=am.get_data(id_user=1)
# Returns: [
#   {
#     "id": 1,
#     "id_user": 1,
#     "location": "742 Los Almendros Street, Apartment 3B, Santa Aurora Neighborhood, North District",
#   }
# ]
```

---

```py
update_data(id_user, id_address, location)
```

Update location of the address

Parameters:
- `id_user`: (int), User ID
- `id_address`: (int), Address to update
- `location`: (str), New location

Returns: True

Raises:
- `APIException`: If could not update the address. Status code: 404

Example Usage:

```py
updated = am.update_data(id_user=1, id_address=1, location="125 Maple Grove Avenue, Suite 4C, Silverwood Neighborhood, West District")
# Returns: True
```

---

```py
delete_data(id_address, id_user)
```

Delete address

Parameters:
- `id_user`: (int), User ID
- `id_address`: (int), Address to delete

Returns: True

Raises:
- `APIException`: If could not delete the address. Status code: 404

Example Usage:

```py
deleted = am.delete_data(id_user=1, id_address=1)
# Returns: True
```

---

#### Payment Manager

Location: db/user/payment_manager.py

Purpose: Manages user payment methods.

##### Method

```py
insert_data(id_user, type_data, data)
```

Create a payment.

Parameters:
- `id_user`: (int), User ID
- `type_data`: (str), Type of payment method
- `data`: (str), Token of the payment

Returns: Payment ID

Raises:
- `APIException`: If could not create the payment. Status code: 500

Example Usage:

```py
from db.utils_db.tables_manager import TablesManager
from src.db import DbPaymentManager

tm = TablesManager()
pm = DbPaymentManager(tm)

# The next examples will omit the above lines
id_payment = pm.insert_data(id_user=1, type_data="credit_card", data="data token")
# Returns: 1 (ID)
```

---

```py
get_data(id, id_user, type_data)
```

Get users payment, could be filter by type.

Parameters:
- `id_user`: (int), User ID
- `id`:(int | None = None), Payment ID
- `type_data`: (str | None = None), Type of payment method

Returns: Dict with all users payments

Example Usage:

```py
id_payment = pm.get_data(id_user=1, type_data="credit_card")
# Returns: [
#   {
#     "id": 1,
#     "id_user": 1,
#     "type_data": "credit_card",
#     "data": "data token",
#   }
# ]
```

---

```py
update_data(id, id_user, type_data, data)
```

Update payment data

> [!WARNING]
> Do not use with cards. Only use for update money to a wallet or updating PayPal.

Parameters:
- `id`: (int), Payment ID
- `type_data`: (str), Type method
- `data`: (str), Information of payment
- `id_user`: (str), User ID

Returns: True

Raises:
- `APIException`: If could not delete the payment. Status code: 404

Example Usage:

```py
updated = pm.update_data(id=2, id_user=1, data="New paypal")
# Returns: True
```

---

```py
delete_data(id, id_user)
```

Delete payment

Parameters:
- `id`: (int), Payment ID
- `id_user`: (str), User ID

Returns: True

Raises:
- `APIException`: If could not delete the payment. Status code: 404

Example Usage:

```py
deleted = pm.delete_data(id=1, id_user=1)
# Returns: True
```
