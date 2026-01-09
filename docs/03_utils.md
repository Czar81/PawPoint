# Database Documentation

## Overview
This document describes the internal utility modules used across the project.
These modules provide shared functionality such as error handling, data validation, caching, encoding, and helper utilities.

## Architecture Overview
```bash
src/utils
│   __init__.py
│   api_exception.py
│   cache_manager.py
│   encoding.py
│   error_handler.py
│   helpers.py
│   verify_data.py
```

## Index
- [](#api_exceptionpy)

## api_exception.py

### Overview

The api_exception.py module defines a custom exception class used across the API to represent controlled application errors with HTTP status codes.

It allows raising errors that can later be converted into consistent HTTP responses.

### Class: APIException
Custom exception class for API-related errors.

_Constructor_
```py
APIException(message, status_code=400)
```

_Parameters_
| Name        | Type    | Required | Description                     |
| ----------- | ------- | -------- | ------------------------------- |
| message     | string  |   Yes    | Error message to be returned    |
| status_code | integer |   No     | HTTP status code (default: 400) |


### Typical Usage
```py
raise ApiException("Invalid credentials", status_code=401)
```

---

## Cache Manager Utility

### Overview
The cache_manager.py module provides an abstraction layer over Redis for caching data within the application.
It centralizes cache access logic and ensures consistent handling of Redis operations and errors.

### Responsibilities
- Improve performance
- Reduce database load
- Temporarily store computed or frequently accessed data

### Environment Variables
This module depends on the following environment variables:
| Variable     | Required   | Description           |
| ------------ | ---------- | --------------------- |
| `REDIS_HOST` |   Yes      | Redis server hostname |
| `REDIS_PORT` |   Yes      | Redis server port     |
| `REDIS_KEY`  |   Optional | Redis password        |

### Class: CacheManager
Manages all Redis cache interactions.

_Initialization_
```
cache = CacheManager()
```

On initialization, the class:
- Loads environment variables
- Creates a Redis client instance
- Connects to the configured Redis server

#### Methods
```py
store_data(key, values, time_to_live=None)
```
Stores data in Redis under a specific key.

_Parameters_
| Name         | Type    | Required | Description                       |
| ------------ | ------- | -------- | --------------------------------- |
| key          | string  |   Yes    | Redis key                         |
| values       | list    |   Yes    | Data to store (JSON serializable) |
| time_to_live | integer |   No     | Expiration time in seconds        |

_Behavior_
- Data is serialized to JSON before storing
- If time_to_live is provided, the key expires automatically
- Uses SET or SETEX depending on TTL

_Example Usage_
```py
cache.store_data(
    key="products:list",
    values=[{"id": 1, "name": "Mouse"}],
    time_to_live=300
)
```

---

```py
check_key(key)
```
Checks whether a key exists in Redis.

_Parameters_
| Name | Type   | Required | Description |
| ---- | ------ | -------- | ----------- |
| key  | string |   Yes    | Redis key   |

_Returns_
- True if key exists
- False otherwise

_Example Usage_
```py
if cache.check_key("products:list"):
    ...
```

---

```py
get_data(key)
```
Retrieves cached data from Redis.

_Parameters_
| Name | Type   | Required | Description |
| ---- | ------ | -------- | ----------- |
| key  | string |   Yes    | Redis key   |

_Returns_
- Json if key exists
- None if key does not exist

_Behavior_
- Automatically decodes bytes
- Deserializes JSON data

_Example Usage_
```py
products = cache.get_data("products:list")
# Returns: [
#    {
#       "id": 1, "name": "Mouse"
#    }
# ]
```

---

```py
delete_data(key)
```
Deletes a specific key from Redis.

_Parameters_
| Name | Type   | Required | Description |
| ---- | ------ | -------- | ----------- |
| key  | string |   Yes    | Redis key   |

_Example Usage_
```py
cache.delete_data("products:list")
```

---

```py
delete_data_with_pattern(pattern)
```
Deletes multiple keys matching a pattern.

_Parameters_
| Name    | Type   | Required | Description                           |
| ------- | ------ | -------- | ------------------------------------- |
| pattern | string |   Yes    | Redis key pattern (wildcards allowed) |

_Behavior_
- Iterates keys using SCAN
- Deletes all matching keys safely

_Example Usage_
```py
cache.delete_data_with_pattern("products:*")
```
---

> [!IMPORTANT]
- All Redis-related exceptions are caught by [error_handler]()CAMBIAR ESTO
- Uses RedisError to preserve Redis context

> [!NOTE]
> - Data is always JSON serialized
> - Cache values are expected to be lists
> - TTL is optional and configurable per entry
> - Designed for reuse across multiple modules

---

## JWT Manager Utility

### Overview
The` encoding.py` module provides JWT (JSON Web Token) encoding and decoding functionality using asymmetric encryption (RS256).

It is responsible for:
- Generating JWT tokens for authentication
- Verifying and decoding JWT tokens
- Managing cryptographic keys via environment variables

### Environment Variables
This module requires the following variables to be defined in `.env`:
| Variable      | Required | Description                              |
| ------------- | -------- | ---------------------------------------- |
| `PRIVATE_KEY` |   Yes    | RSA private key used to sign JWT tokens  |
| `PUBLIC_KEY`  |   Yes    | RSA public key used to verify JWT tokens |

> [!WARNING]
> If either key is missing, the application will fail on startup.

### Class: JWTManager
Handles JWT token encoding and decoding using the RS256 algorithm.

_Initialization_
```py
jwt_manager = JWTManager()
```

_Behavior_
- Loads environment variables
- Validates the presence of cryptographic keys
- Raises ValueError if keys are missing

#### Methods
```py
encode(data)
```
Encodes a payload into a JWT token.

_Parameters_
| Name | Type | Required | Description                      |
| ---- | ---- | -------- | -------------------------------- |
| data | dict |   Yes    | Payload data to embed in the JWT |

_Returns_

- `string`: Encoded JWT token

_Example Usage_
```py
token = jwt_manager.encode({"id": 10})
```

---

```py
decode(token)
```
Decodes and validates a JWT token.

_Parameters_
| Name  | Type   | Required | Description |
| ----- | ------ | -------- | ----------- |
| token | string |   Yes    | JWT token   |

_Returns_

- `dict`: Decoded token payload

_Example Usage_
```py
payload = jwt_manager.decode(token)
user_id = payload["id"]
```

> [!IMPORTANT]
> Uses RS256 (asymmetric encryption) instead of shared secrets
> Private key is only used for signing tokens
> Public key is used for verification
> Keys should never be committed to version control

> [!CAUTION]
> Rotate RSA keys periodically
> Store keys securely using environment variables
> Keep token payload minimal (e.g. user ID only)
> Always validate tokens before accessing protected routes

---

## Global Error Handling Utility

### Overview

The error_handler.py module centralizes error handling logic for the API by registering custom exception handlers on Flask blueprints.
Also prints a traceback to debbug easier.

Its main purpose is to:
- Convert Python and database exceptions into consistent JSON responses
- Prevent unhandled exceptions from crashing the API
- Log errors for debugging and monitoring

### Function: register_error_handlers(blueprint)
Registers a set of exception handlers on a given Flask blueprint.

This allows each blueprint to:

- Catch specific exceptions
- Return structured JSON error responses
- Assign appropriate HTTP status codes

_Parameters_
| Name      | Type            | Required | Description                          |
| --------- | --------------- | -------- | ------------------------------------ |
| blueprint | Flask Blueprint | ✅ Yes    | Blueprint to register error handlers |

Example Usage
```py
from utils.error_handler import register_error_handlers

register_error_handlers(user_bp)
```

#### Registered Error Handlers

_`ValueError`_

| Attribute   | Value                                  |
| ----------- | -------------------------------------- |
| HTTP Status | `400 Bad Request`                      |
| Description | Invalid input or business logic errors |

_Response Example_
```json
{
  "error": "Invalid value"
}
status code: 400
```

---

_`IntegrityError`_ (SQLAlchemy)

| Attribute   | Value                         |
| ----------- | ----------------------------- |
| HTTP Status | `409 Conflict`                |
| Description | Database constraint violation |

_Response Example_
```json
{
  "error": "Database integrity error: duplicate key"
}
status code: 409
```
--

_`SQLAlchemyError`_

| Attribute   | Value                       |
| ----------- | --------------------------- |
| HTTP Status | `500 Internal Server Error` |
| Description | General database failure    |

_Response Example_
```json
{
  "error": "Internal database error"
}
status code: 500
```
---

_`APIException`_

| Attribute   | Value                |
| ----------- | -------------------- |
| HTTP Status | Custom               |
| Description | Controlled API error |

_Response Example_
```json
{
  "error": "Unauthorized"
}
status code: 500
```

---

_`RecursionError`_

| Attribute   | Value                                      |
| ----------- | ------------------------------------------ |
| HTTP Status | `500 Internal Server Error`                |
| Description | Potential Redis recursion or infinite loop |

_Response Example_
```json
{
  "error": "An unexpected error occurred with redis"
}
status code: 500
```

---

_`Generic Exception`_

| Attribute   | Value                          |
| ----------- | ------------------------------ |
| HTTP Status | `500 Internal Server Error`    |
| Description | Unhandled or unexpected errors |

_Response Example_
```json
{
  "error": "An unexpected error occurred"
}
status code: 500
```

### Logging Behavior

- Uses Python’s logging module
- Logs warning-level events for client-related errors
- Logs error-level events for system failures
- Includes stack traces via traceback.print_exc()

---

## Helper Utilities
The helpers.py module provides reusable helper functions used across the app, mainly for:

- Filtering function parameters
- Generating cache keys
- Abstracting cache + database fallback logic

### Functions
```py
filter_values(locals_dict, exclude=("self",))
```
Filters out unwanted or None values from a dictionary. Principal think to use in a class, pasing its locals(). 

_Parameters_
| Name        | Type  | Required | Description                         |
| ----------- | ----- | -------- | ----------------------------------- |
| locals_dict | dict  |   Yes    | Dictionary of local variables       |
| exclude     | tuple |   No     | Keys to exclude (default: `"self"`) |

_Returns_
- `dict`: Filtered dictionary with only valid values

_Example Usage_
```
filters = filter_values(locals())
```
_Typical Use Case_
- Cleaning parameters before database queries
- Ignoring optional None values

---

```py
generate_cache_based_filters(key_prefix, filters_dict)
```
Generates a cache key suffix based on filter parameters.

_Parameters_
| Name         | Type   | Required | Description       |
| ------------ | ------ | -------- | ----------------- |
| key_prefix   | string |   Yes    | Base cache key    |
| filters_dict | dict   |   Yes    | Filter parameters |

_Returns_
- `string`: Cache key with filters

_Behavior_
- Sorts filters to ensure deterministic cache keys
- Appends filters as `key=value`
- Falls back to `:all` when no filters exist

_Example Usage_
```py
key = generate_cache_based_filters("products", filters)
# products:price=100:category=electronics
```

---

```py
generate_cache_key(key_prefix, id)
```
Generates a simple cache key using a prefix and identifier.

_Parameters_
| Name       | Type    | Required | Description         |
| ---------- | ------- | -------- | ------------------- |
| key_prefix | string  |   Yes    | Base cache key      |
| id         | integer |   Yes    | Resource identifier |

_Returns_
- `string`: Cache key

_Example Usage_
```py
key = generate_cache_key("product", 10)
# product:10
```

---

```py
get_cache_if_exist(key, cache_manager, db_manager, **search_params)
```
Retrieves data from cache if available; otherwise queries the database and caches the result.

_Parameters_
| Name          | Type              | Required | Description               |
| ------------- | ----------------- | -------- | ------------------------- |
| key           | string            |   Yes    | Cache key                 |
| cache_manager | CacheManager      |   Yes    | Cache manager instance    |
| db_manager    | SQLAlchemy object |   Yes    | Database manager instance |
| search_params | dict              |   No     | Database query parameters |

_Returns_
- `(data, status_code)`
    - `200 OK` on success
    - `404 Not Found` if data does not exist

_Behavior_
- Checks cache first
- Queries DB if cache miss
- Stores DB result in cache
- Returns standardized response

_Example Usage_
```py
data, status = get_cache_if_exist(
    key="products:all",
    cache_manager=cache_manager,
    db_manager=db_products_manager,
    category="electronics"
)
```

---

## Request Validation & Authorization Utilities

### Overview
The verify_data.py module provides decorators used to:
- Enforce role-based access control (RBAC)
- Validate request payloads
- Inject authenticated user data into route handlers

#### Decorator: role_required(allowed_roles)
Restricts access to endpoints based on user roles extracted from a JWT token.

_Parameters_
| Name          | Type      | Required | Description                          |
| ------------- | --------- | -------- | ------------------------------------ |
| allowed_roles | list[str] |   Yes    | Roles allowed to access the endpoint |

_Authentication Flow_
1. Reads Authorization header
2. Extracts and decodes JWT token
3. Retrieves user role from database
4. Validates role against allowed roles
5. Injects id_user and role into the route function

_Required Headers_
| Name          | Required | Description      |
| ------------- | -------- | ---------------- |
| Authorization | Yes      | Bearer JWT token |

_Possible Responses_
| Status | Description       |
| ------ | ----------------- |
| 401    | Missing token     |
| 403    | Unauthorized role |

_Example Usage_
```py
@role_required(["admin", "user"])
def get_profile(id_user, role):
    ...
```

#### Decorator: validate_fields(required=None, optional=None)
Validates JSON request bodies and injects validated fields into route functions.

_Parameters_
| Name     | Type      | Required | Description          |
| -------- | --------- | -------- | -------------------- |
| required | list[str] |   No     | Required JSON fields |
| optional | list[str] |   No     | Optional JSON fields |

_Validation Rules_
- Reads request body as JSON
- Ensures required fields exist and are not None
- Ignores missing optional fields if are not provide
- Ensure that only values defined in the optional list are accepted.
- Automatically injects fields as function arguments

Example Usage (Required Fields)
```py
@validate_fields(required=["username", "password"])
def register(username, password):
    ...
```

Example Usage (Optional Fields)
```py
@validate_fields(optional=["name"])
def get_product(name=None):
    ...
```

Combined Usage Example (role_required and validate_fields)
```py
@role_required(["admin"])
@validate_fields(required=["name"], optional=["price"])
def create_product(id_user, role, name, price=None):
    ...
```

[!NOTE]
- JWT is validated before role checks
- Role verification always hits the database
- Unauthorized access is blocked early