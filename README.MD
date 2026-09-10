# StockFlow — Inventory & Stock Management Platform

StockFlow is a Django application for small businesses to manage products, categories, suppliers and auditable stock movements.

## Features

- Session-based registration, login and logout; every application/API view requires authentication.
- Public landing page with secure Django password reset by email.
- Admin/Manager/Staff roles. Managers administer products, categories and suppliers; Staff can record stock movements but cannot change catalog records.
- Product search by name, SKU or category, category filtering, low-stock detection and pagination.
- Atomic stock-in/stock-out logic that locks the product row and rejects insufficient stock.
- REST API at `/api/categories/`, `/api/suppliers/`, `/api/products/`, and `/api/transactions/`.

## Stack and architecture

Python, Django, Django REST Framework, PostgreSQL, Django templates and Docker. `accounts` owns registration; `inventory` owns the Category, Supplier, Product and InventoryTransaction models, web views, and API.

Products belong to categories and optionally suppliers. Every stock movement belongs to a product and user. Categories/suppliers are protected from deletion while products reference them.

## Setup

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Create a PostgreSQL database and set the variables in `.env` (or your shell): `DJANGO_SECRET_KEY`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, and `DATABASE_PORT`. The default runtime backend is PostgreSQL. `DB_ENGINE=sqlite` is available only for a quick local demo; tests automatically use SQLite.

Password reset uses the configured SMTP backend. Set `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (a Gmail App Password, never your account password), and `DEFAULT_FROM_EMAIL` before using that flow. The `.env` file is local-only and must never be committed.

Run checks with `python manage.py check` and tests with `python manage.py test`.

## API

Use a logged-in Django session. Product `quantity` is read-only in the API: create an `IN` or `OUT` transaction instead. Product/category/supplier mutations require Manager or Admin; transaction creation is available to all authenticated roles. A rejected stock-out returns a validation error.

## Security

Secrets are environment based, CSRF middleware remains enabled, passwords use Django hashing, ORM queries are used throughout, and write permissions are enforced server-side.


