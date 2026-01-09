# API Documentation

## Overview

This API provides endpoints for managing users, sales, carts, products, and receipts.
The API uses a relational database as the primary data store and integrates additional utilities such as Redis for caching and temporary data storage, JWT for authentication and authorization, and a verification utility for request and data validation.

## Architecture Overview

```bash
src/api/
│── __init__.py
│
│── sell_module/
│   ├── cart_api.py
│   ├── cart_item_api.py
│   ├── product_api.py
│   └── receipt_api.py
│
│── user_module/
│   ├── user_api.py
│   ├── address_api.py
│   └── payment_api.py
```

## Index

- Modules
  - Sell module
    - [Product api](#product)
    - [Cart api](#cart)
    - [Cart Item api](#cart-item)
    - [Receipt api](#receipt)
  - User module
    - [User api](#user)
    - [Address api](#address)
    - [Payment api](#payment)

## Modules

### Product

Product API (`product_api.py`)

Manages products available for sale.
This module can:

- Create product
- Update product
- Delete product
- List products

#### Base Path

```py
/products
```

---

#### Endpoints

```BASH
POST /products
```

Register a product

---

_Authentication_

Required Admin access

---

_JSON Parameters_
| Name | Type | Required | Description |
| ------ | ------- | -------- | ------------------------------- |
| sku | string | Yes | Unique product identifier (SKU) |
| name | string | Yes | Product name |
| price | integer | Yes | Product price |
| amount | integer | Yes | Available stock |

---

_Headers Parameters_
| Name | Required | Description |
| ------------- | -------- | ---------------------------------------------------------- |
| Authorization | Yes | Admin authentication token |
| Content-Type | Yes | Must be `application/json` |

---

_Request Example_

```bash
POST /products
Authorization: Bearer <jwt_token>
Content-Type: application/json
json = {
  "sku": "PROD-001",
  "name": "Wireless Mouse",
  "price": 2599, # for $25.99
  "amount": 100
}
```

---

_Request Body Example_

```bash
{
    "id": 1,
    "message": "Product created"
}
```

---

```BASH
GET /products
```

Get all products or filter by parameters.

---

_Authentication_

Not required

---

JSON Parameters\_
| Name | Type | Required | Description |
| ---------- | ------- | -------- | ------------------------ |
| id_product | integer | No | Unique product ID |
| sku | string | No | Product SKU |
| name | string | No | Product name |
| price | integer | No | Product price |
| amount | integer | No | Product stock |

---

_Headers Parameters_
| Name | Required | Description |
| ------------- | -------- | --------------------------------------------------------|
| Content-Type | Yes | Must be `application/json`, Just if filters will be sent|

---

_Request Example_

```bash
GET /products
json = {
  "price": 2599 # Filter by this price
}
```

---

_Response Body Example_

```bash
{
 "products:[
  {
   "id": 1
   "sku": "PROD-001",
   "name": "Wireless Mouse",
   "price": 2599,
   "amount": 100
  }
 ]
}
```

---

```BASH
GET /products/id_product
```

Get one product, like a whole page for the product

_Authentication_

Not required

---

_Path Parameters_
| Name | Type | Required | Description |
| ---------- | ------- | -------- | -----------------|
| id_product | integer | Yes | Unique product ID|

---

_Response Body Example_

```bash
{
 "products:[
  {
   "id": 1
   "sku": "PROD-001",
   "name": "Wireless Mouse",
   "price": 2599,
   "amount": 100
  }
 ]
}
```

---

```BASH
PUT /products/id_product
```

Updates products data

_Authentication_

Requierd admin access

---

_JSON Parameters_
| Name | Type | Required | Description |
| ------ | ------- | -------- | ------------------------------- |
| sku | string | No | Unique product identifier (SKU) |
| name | string | No | Product name |
| price | integer | No | Product price |
| amount | integer | No | Available stock |

---

_Headers Parameters_
| Name | Required | Description |
| ------------- | -------- | ---------------------------------------------------------- |
| Authorization | Yes | Admin authentication token |
| Content-Type | Yes | Must be `application/json`

---

_Path Parameters_
| Name | Type | Required | Description |
| ------ | ------- | -------- | -------------------- |
| id_product | integer | Yes | Unique product ID|

---

_Request Example_

```bash
PUT /products/1
Authorization: Bearer <jwt_token>
json = {
  "name": "Bluetooth Mouse",
}
```

---

_Response Body Example_

```bash
{
    "message": "Product Updated"
}
```

---

```BASH
DELETE /products/id_product
```

Deletes a product

---

_Authentication_

Requierd admin access

---

_Headers Parameters_
| Name | Required | Description |
| ------------- | -------- | ---------------------------------------------------------- |
| Authorization | Yes | Admin authentication token |
| Content-Type | Yes | Must be `application/json`

---

_Path Parameters_
| Name | Type | Required | Description |
| ------ | ------- | -------- | -------------------- |
| id_product | integer | Yes | Unique product ID|

---

_Request Example_

```bash
DELETE /products/1
Authorization: Bearer <jwt_token>
```

---

_Response Body Example_

```bash
{
   "message": "Product Deleted"}
}
```

---

### Cart

#### Paths

```py
/me/carts
/cart
```

> [!IMPORTANT] > `/cart`, is for arctive cart
> `/me/carts`, base of the another 3 endpoints

#### Endpoints

```BASH
POST /me/carts
```

Create a new cart for the authenticated user.

> [!IMPORTANT]
> When you send a request to /register, automatic creates a cart

---

_Authentication_

Required: admin or user

---

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | -------------- |
| Authorization | Yes | User JWT token |

---

_Request Example_

```bash
POST /me/carts
Authorization: Bearer <jwt_token>
```

---

Response Example

```bash
{
  "message": "Cart created",
  "id": 2
}
```

---

```bash
GET /me/carts
```

Get all carts for the authenticated user or filter by parameters.

_Authentication_

Required: admin or user

_Body Parameters_
| Name | Type | Required | Description |
| ------- | ------- | -------- | --------------------------------------- |
| id_cart | integer | No | Cart ID |
| state | string | No | Cart state (e.g. `active`, `archive`) |

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | --------------------------------- |
| Authorization | Yes | User JWT token |
| Content-Type | No | Required only if filters are sent |

---

_Request Example_

```bash
GET /me/carts
Authorization: Bearer <jwt_token>
```

---

_Response Example_

```bash
{
    "carts": [
        {
            "id": 1,
            "id_user": 1,
            "state": "active",
        }
    ]
}
```

---

```py
GET /cart
```

Get the current active cart with its items.

_Authentication_

Required: admin or user

---

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | -------------- |
| Authorization | Yes | User JWT token |

---

_Request Example_

```bash
GET /cart
Authorization: Bearer <jwt_token>
```

---

_Response Example_

```bash
{
  "cart": {
      "id": 1,
      "id_user": 1,
      "state": "active",
      "items": [{
        "id": 1,
        "id_cart": 1,
        "id_product": 1,
        "amount": 10
        }],
  }
}
```

---

```py
GET /me/carts/id_cart
```

Get a cart with its items.

> [!NOTE]
> If need active cart use `GET /cart`

_Authentication_

Required: admin or user

---

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | -------------- |
| Authorization | Yes | User JWT token |

---

_Request Example_

```bash
GET /me/carts/2
Authorization: Bearer <jwt_token>
```

---

_Response Example_

```bash
{
  "cart": {
      "id": 2,
      "id_user": 1,
      "state": "archive",
      "items": [{
        "id": 1,
        "id_cart": 1,
        "id_product": 2,
        "amount": 3
        }],
    }
}
```

---

```bash
PUT /me/carts/id_cart
```

Update the cart status to active.

---

_Authentication_

Required: admin or user

---

_Path Parameters_
| Name | Type | Required | Description |
| ------- | ------- | -------- | ----------- |
| id_cart | integer | Yes | Cart ID |

---

_Example Request_

```bash
PUT /me/carts/1
Authorization: Bearer <jwt_token>
```

_Response Example_

```bash
{
  "message": "Cart updated"
}
```

---

```bash
DELETE /me/carts/id_cart
```

Delete a cart owned by the authenticated user.

---

_Authentication_

Required: admin or user

---

_Path Parameters_
| Name | Type | Required | Description |
| ------- | ------- | -------- | ----------- |
| id_cart | integer | Yes | Cart ID |

---

_Example Request_

```bash
DELETE /me/carts/1
Authorization: Bearer <jwt_token>
```

_Response Example_

```
{
  "message": "Cart Deleted"
}
```

---

### Cart item

#### Paths

```py
/add-item
/modify-amount-item/id_cart_item
/remove-item/id_cart_item
```

> [!IMPORTANT]
> To get cart items use `/me/carts/<id_cart>`

#### Endpoints

```bash
POST /add-item
```

---

Authentication

Required: admin or user

---

_Body Parameters_
| Name | Type | Required | Description |
| ---------- | ------- | -------- | ----------------------- |
| id_cart | integer | Yes | Cart ID |
| id_product | integer | Yes | Product ID |
| amount | integer | Yes | Quantity of the product |

---

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | -------------------------- |
| Authorization | Yes | User JWT token |
| Content-Type | Yes | Must be `application/json` |

---

_Example Request_

```bash
POST /add-item
Authorization: Bearer <jwt_token>
json={
    id_cart:1,
    id_product:2
    amount:5
}
```

_Response Example_

```bash
{
  "id": 2,
  "message": "Item added"
}

```

---

```bash
PUT /modify-amount-item/id_cart_item
```

Update the quantity of an item in a cart.

---

Authentication

Required: admin or user

_Path Parameters_
| Name | Type | Required | Description |
| ------------ | ------- | -------- | ------------ |
| id_cart_item | integer | Yes | Cart item ID |

---

_Body Parameters_
| Name | Type | Required | Description |
| ------ | ------- | -------- | ------------ |
| amount | integer | Yes | New quantity |

---

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | -------------------------- |
| Authorization | Yes | User JWT token |
| Content-Type | Yes | Must be `application/json` |

---

_Example Request_

```bash
PUT /modify-amount-item/2
Authorization: Bearer <jwt_token>
json={
    amount:5
}
```

_Response Example_

```bash
{
  "message": "Amount updated"
}
```

---

```bash
DELETE /cart-items/remove-item/id_cart_item
```

## Remove an item from a cart.

_Authentication_

Required: admin or user

_Path Parameters_
| Name | Type | Required | Description |
| ------------ | ------- | -------- | ------------ |
| id_cart_item | integer | Yes | Cart item ID |

---

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | -------------- |
| Authorization | Yes | User JWT token |

---

_Example Request_

```bash
PUT /modify-amount-item/2
Authorization: Bearer <jwt_token>
```

_Response Example_

```bash
{
  "message": "Item deleted"
}
```

---

### Receipt

#### Paths

```py
/create-receipt
/me/receipt
```

> [!NOTE] > `/me/receipt`, base of anothers endpoints, `create-receipt` just to create the receipt

#### Endpoints

```bash
POST /create-receipt
```

Create a receipt from a cart.

_Authentication_

Required: admin or user

---

_Body Parameters_
| Name | Type | Required | Description |
| ---------- | ------- | -------- | ----------------- |
| id_cart | integer | Yes | Cart ID |
| id_address | integer | Yes | Address ID |
| id_payment | integer | Yes | Payment method ID |

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | -------------------------- |
| Authorization | Yes | User JWT token |
| Content-Type | Y es | Must be `application/json` |

---

_Example Request_

```bash
POST /create-receipt
Authorization: Bearer <jwt_token>
json={
    "id_cart": 1,
    "id_address": 1,
    "id_payment": 1
}
```

---

_Response Example_

```bash
{
  "message": "Receipt created",
  "id": 1
}
```

---

```bash
GET /me/receipt
```

Get receipts for the authenticated user or filter by parameters.

_Authentication_

Required: admin or user

_Body Parameters (Filters)_
| Name | Type | Required | Description |
| ---------- | ------- | -------- | ---------------------------------- |
| id_receipt | integer | No | Receipt ID |
| id_cart | integer | No | Cart ID |
| id_address | integer | No | Address ID |
| id_payment | integer | No | Payment method ID |
| state | string | No | Receipt state |
| entry_date | string | No | Receipt creation date (YYYY-MM-DD) |

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | --------------------------------- |
| Authorization | Yes | User JWT token |
| Content-Type | No | Required only if filters are sent |

---

_Example Request_

```bash
GET /me/receipt
Authorization: Bearer <jwt_token>
json= {
    "state": "paid"
}
```

_Response Example_

```bash
{
  "data": [
    {
      "id": 1,
      "id_address": 1,
      "id_cart": 1,
      "id_payment": 1,
      "state": "paid",
      "entry_date": "2025-01-10"
    }
  ]
}
```

---

```bash
GET /me/receipt/id_receipt
```

Get a single receipt by ID.

_Authentication_

Required: admin or user

_Path Parameters_
| Name | Type | Required | Description |
| ---------- | ------- | -------- | ----------- |
| id_receipt | integer | Yes | Receipt ID |

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | -------------- |
| Authorization | Yes | User JWT token |

---

_Example Request_

```bash
GET /me/receipt/id_receipt/2
Authorization: Bearer <jwt_token>
```

```bash
{
  "data": [
    {
      "id": 2,
      "id_address": 1,
      "id_cart": 1,
      "id_payment": 1,
      "state": "returned",
      "entry_date": "2025-01-22"
    }
  ]
}
```

---

```bash
POST /receipt/me/receipt/id_receipt/return
```

Return a receipt. And restore stock

_Authentication_

Required: admin or user

_Path Parameters_
| Name | Type | Required | Description |
| ---------- | ------- | -------- | ----------- |
| id_receipt | integer | Yes | Receipt ID |

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | -------------- |
| Authorization | Yes | User JWT token |

---

_Example Request_

```bash
GET /me/receipt/id_receipt/2/return
Authorization: Bearer <jwt_token>
```

_Response Example_

```bash
{
  "message": "Receipt returned"
}
```

---

### User

#### Paths

```py
/register
/login
/me
/users
```

> [!NOTE] > `/me` use in three endpoints

#### Endpoints

```bash
POST /user/register
```

Register a new user.

_Authentication_
Not required

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | --------------------------------------------------------- |
| X-ADMIN-TOKEN | No | Same as `ADMIN_BOOTSTRAP_TOKEN` to register an admin user |
| Content-Type | Yes | Must be `application/json` |

_Body Parameters_
| Name | Type | Required | Description |
| -------- | ------ | -------- | ------------- |
| username | string | Yes | User username |
| password | string | Yes | User password |

---

_Example Request_

```bash
POST /register
JSON={
  "username": "john_doe",
  "password": "StrongPassword123"
}
```

Response Example

```bash
{
  "token": "jwt_token_here",
  "id_cart": 1
}

```

---

```bash
POST /user/login
```

Authenticate a user and return a JWT token.

_Authentication_

Not required

---

_Body Parameters_
| Name | Type | Required | Description |
| -------- | ------ | -------- | ------------- |
| username | string | Yes | User username |
| password | string | Yes | User password |

---

_Example Request_

```bash
POST /login
JSON={
  "username": "john_doe",
  "password": "StrongPassword123"
}
```

_Response Example_

```bash
{
  "token": "jwt_token_here"
}
```

---

```bash
GET /me
```

Get the authenticated user's profile.

_Authentication_

Required: user or admin

---

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | ---------------- |
| Authorization | Yes | Bearer JWT token |

---

_Example Request_

```bash
GET /me
Authorization: Bearer <jwt_token>
```

_Response Example_

```bash
{
  "user": {
    "id_user": 5,
    "username": "john_doe",
    "role": "user"
  }
}
```

---

```bash
GET /users
```

Get all users (admin only).

_Authentication_

Required: admin access

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | --------------- |
| Authorization | Yes | Admin JWT token |

---

_Example Request_

```bash
GET /users
Authorization: Bearer <jwt_admin_token>
```

_Response Example_
{
"user": [
{
"id_user": 1,
"username": "admin",
"role": "admin"
},
{
"id_user": 2,
"username": "jhon doe",
"role": "user"
}
]
}

---

```bash
PUT /me
```

Update the authenticated user's profile.

_Authentication_

Required: admin or user

---

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | -------------------------- |
| Authorization | Yes | Bearer JWT token |
| Content-Type | Yes | Must be `application/json` |

_Body Parameters_
| Name | Type | Required | Description |
| -------- | ------ | -------- | --------------------- |
| username | string | No | New username |
| password | string | No | New password |
| new_role | string | No | New role (admin only) |

---

_Example Request_

```bash
PUT /me
Authorization: Bearer <jwt_token>
json={"username":"Jane Doe"}
```

_Response Example_

```bash
{
  "message": "User updated"
}
```

---

```
DELETE /me
```

Delete the authenticated user's account.

_Authentication_

Required: admin or user

---

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | ---------------- |
| Authorization | Yes | Bearer JWT token |

---

_Example Request_

```bash
DELETE /me
Authorization: Bearer <jwt_token>
```

_Response Example_

```bash
{
  "message": "User deleted"
}
```

---

### Address

All endpoints require authentication and are accessible by users with admin or user roles.

#### Base Path

```py
/me/address
```

#### Endpoints

```bash
POST /me/address
```

Register a new address for the authenticated user.

_Authentication_

Required: admin or user

---

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | -------------------------- |
| Authorization | Yes | Bearer JWT token |
| Content-Type | Yes | Must be `application/json` |

_Body Parameters_
| Name | Type | Required | Description |
| -------- | ------ | -------- | ---------------- |
| location | string | Yes | Address location |

---

_Example Request_

```bash
POST /me/address
Authorization: Bearer <jwt_token>
json={
  "location": "San José, Costa Rica"
}
```

_Response Example_

```bash
{
  "message": "Address created",
  "id": 1
}
```

---

```bash
GET /me/address
```

Get all addresses for the authenticated user.

_Authentication_

Required: admin or user

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | ---------------- |
| Authorization | Yes | Bearer JWT token |

---

_Example Request_

```bash
GET /me/address
Authorization: Bearer <jwt_token>
```

_Response Example_

```bash
{
  "data": [
    {
      "id": 1,
      "id_user": 1,
      "location": "San José, Costa Rica"
    }
  ]
}
```

---

```bash
GET /me/address/id_address
```

Get a specific address by ID.

_Authentication_

Required: admin or user

---

_Path Parameters_
| Name | Type | Required | Description |
| ---------- | ------- | -------- | ----------- |
| id_address | integer | Yes | Address ID |

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | ---------------- |
| Authorization | Yes | Bearer JWT token |

---

_Example Request_

```bash
GET /me/address/2
Authorization: Bearer <jwt_token>
```

_Response Example_

```bash
{
  "data": {
    "id": 2,
    "id_user": 1,
    "location": "Cartago, Costa Rica"
  }
}
```

---

```bash
PUT /me/address/id_address
```

Update an existing address.

_Authentication_

Required: admin or user

---

_Path Parameters_
| Name | Type | Required | Description |
| ---------- | ------- | -------- | ----------- |
| id_address | integer | Yes | Address ID |

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | -------------------------- |
| Authorization | Yes | Bearer JWT token |
| Content-Type | Yes | Must be `application/json` |

_Body Parameters_
| Name | Type | Required | Description |
| -------- | ------ | -------- | ------------------------ |
| location | string | Yes | Updated address location |

---

_Example Request_

```bash
PUT /me/address/1
Authorization: Bearer <jwt_token>
json = {
  "location": "Alajuela, Costa Rica"
}
```

_Response Example_

```bash
{
  "message": "Address updated"
}
```

---

```bash
DELETE /me/address/id_address
```

Delete an address.

_Authentication_

Required: admin or user

---

_Path Parameters_
| Name | Type | Required | Description |
| ---------- | ------- | -------- | ----------- |
| id_address | integer | Yes | Address ID |

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | ---------------- |
| Authorization | Yes | Bearer JWT token |

---

_Example Request_

```bash
DELETE /me/address/1
Authorization: Bearer <jwt_token>
```

_Response Example_

```bash
{
  "message": "Address deleted"
}
```

---

### Payment

#### Base Path

```py
/me/payment
```

All endpoints require authentication and are accessible by users with admin or user roles.

#### Endpoints

```bash
POST /me/payment
```

Register a new payment method for the authenticated user.

---

_Authentication_

Required: admin or user

---

_Header Parameters_

| Name          | Required | Description                |
| ------------- | -------- | -------------------------- |
| Authorization | Yes      | Bearer JWT token           |
| Content-Type  | Yes      | Must be `application/json` |

_Body Parameters_
| Name | Type | Required | Description |
| --------- | ------ | -------- | ------------------------------------ |
| type_data | string | Yes | Payment type (e.g. `credit_card`, `paypal`) |
| data | string | Yes | Payment data (encrypted or masked) |

---

_Request Example_
```bash
POST /me/payment
Authorization: Bearer <jwt_token>
json={
  "type_data": "credit_card",
  "data": "fah5435bsdfghsdufh87fsadfghb454wegfd35446erwfd2435436dnj8udsf87"
}
```

_Response Example_
```bash
{
  "message": "Payment created",
  "id": 1
}
```

---

```bash
GET /me/payment
```

Get all payment methods of the authenticated user or filter by type.

---

_Authentication_

Required: admin or user

---

_Header Parameters_
| Name | Required | Description |
| ------------- | ------------- | --------------------------------- |
| Authorization | Yes | Bearer JWT token |
| Content-Type | Conditional | Required only if filters are sent |

_Body Parameters_
| Name | Type | Required | Description |
| --------- | ------ | -------- | ---------------------- |
| type_data | string | No | Filter by payment type |

---

_Request Example_
```bash
GET /me/payment
Authorization: Bearer <jwt_token>
json={
  "type_data": "credit_card",
}
```

_Response Example_
```bash
{
  "data": [
    {
      "id_payment": 1,
      "type_data": "credit_cart",
      "data": "fah5435bsdfghsdufh87fsadfghb454wegfd35446erwfd2435436dnj8udsf87"
    }
  ]
}
```

---

```bash
GET /payment/me/payment/id_payment
```

Get a single payment method by ID.

---

_Authentication_

Required: admin or user

---

_Response Example_
| Name | Type | Required | Description |
| ---- | ------- | -------- | ----------- |
| id | integer | Yes | Payment ID |

_Header Parameters_
| Name | Required | Description |
| ------------- | -------- | ---------------- |
| Authorization | Yes | Bearer JWT token |

---

_Request Example_
```bash
GET /me/payment/1
Authorization: Bearer <jwt_token>
```

_Response Example_
```bash
{
  "data": {
    "id_payment": 2,
    "type_data": "debit_cart",
    "data": "fsdafkjnfd8u9sfy8shdfh78sdfsd87hgfs78dftgiufdy90j"
  }
}
```

---

> [!NOTE]
> There is not a endpoint to update payment method, to change one payment delete it first and create a new one then.

---

```bash
DELETE /me/payment/id_payment
```

Delete a payment method.

---

_Authentication_

Required: admin or user

---

_Path Parameters_
| Name       | Type    | Required | Description |
| ---------- | ------- | -------- | ----------- |
| id_payment | integer |   Yes    | Payment ID  |

_Header Parameters_
| Name          | Required | Description      |
| ------------- | -------- | ---------------- |
| Authorization |   Yes    | Bearer JWT token |

---

_Request Example_
```bash
DELETE /me/payment/1
Authorization: Bearer <jwt_token>
```

Response Example
```bash
{
  "message": "Payment deleted"
}
```