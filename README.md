# PawPoint – Essentials & Care

## Index

- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [Quick Installation](#quick-installation)
- [How to Run the Project](#how-to-run-the-project)
- [How to run the unit testing](#how-to-run-the-unit-testing)
- [Advanced Documentation](#advanced-documentation)

## What PawPoint is?

PawPoint is a modular system for managing pet products and veterinary services. It uses an API-driven architecture that centralizes inventory control, user management, and service operations. The platform integrates a relational database for data persistence and Redis as a caching and performance optimization layer, enabling faster operations, scalability, and efficient communication between modules.

## Key Features

- API-driven architecture for integrations and seamless communication between modules.
- Inventory management for essential products and veterinary supplies.
- User and role management with permission control.
- Relational SQL database for reliable data persistence.
- Redis integration for caching and performance optimization.
- Robust input validation for critical operations.
- Centralized error handling for consistent API responses.
- Authentication and authorization using token-based mechanisms.

## Technologies Used

- **Python** – Core programming language
- **Flask** – Web framework for building APIs and backend services
- **SQLAlchemy** – ORM for relational SQL database interactions
- **PostgreSQL** – Relational SQL database
- **Redis** – Caching and session management
- **python-dotenv** – Environment variable management (.env)
- **PyJWT** – Authentication with JSON Web Tokens
- **pytest** – Testing framework
- **Click** – Command-line utilities

## Quick Installation

1. Clone this project:

   ```bash
   git clone https://github.com/Czar81/DUAD.git
   ```

2. Move to the project directory:

   ```bash
   cd DUAD/M2/Back_end/pet_shop

   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
4. Activate the virtual environment:
   - Windows:
   ```bash
   .venv\Scripts\activate
   ```
   - Linux/macOS:
   ```bash
   source .venv/bin/activate
   ```
5. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Make sure you have a PostgreSQL database running.

7. Create a .env file based on .env.example. You need to configure:

   - JWT:

     Public and private keys. You can generate them with OpenSSL:

     - Windows: download from [OpenSSL](https://slproweb.com/products/Win32OpenSSL.html)

     - macOS: `brew install openssl`

     - Debian/Ubuntu: `sudo apt install openssl`

   - API:

     - Specify the host and port for the API (examples: _localhost, 192.168.1.100, api.pawpoint_).

     - Set _DEBUG_MODE=false_ in production.

   - Database:

     - Provide the database URL (example: _postgresql://username:password@localhost:5432/database_name_)

   - Redis:

     - Server address (_localhost_ for development, IP or domain for production)

     - Redis port

     - Password/key if authentication is enabled

   - Admin registration:

     - Add ADMIN_BOOTSTRAP_TOKEN to safely register an admin account

## How to run the project

With the virtual environment activated and inside the `pet_shop` directory, run:

```bash
python main.py
```

Alternatively, you can run the file directly from VS Code.

## How to run the unit testing
Before running the tests, update your .env file:

Set the database URL to use SQLite in-memory for testing:
```bash
DATABASE_URL="sqlite:///:memory:"
```
Set DEBUG_MODE=True.

Then, run the tests with:
```bash
python -m pytest
```

## Advanced documentation

To see the full documentation of the project look [here](./docs/index.md)
