# SubLedger

FastAPI backend for simplified SaaS plans, customers, subscriptions, invoices, payments, and an append-only ledger.

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI. By default, data is stored in `subledger.db`; override it with `DATABASE_URL`.

## API

| Method | Path | Purpose |
|---|---|---|
| POST /plans, GET /plans, PATCH /plans/{id} | Plans | Create, list, update / activate / deactivate |
| POST /customers, GET /customers, GET /customers/{id} | Customers | Create and retrieve customers |
| POST /subscriptions, GET /subscriptions, POST /subscriptions/{id}/cancel | Subscriptions | Start, list, cancel |
| POST /invoices/generate, GET /invoices, GET /invoices/{id} | Invoices | Generate and retrieve invoices |
| POST /payments/record | Payments | Record success or failure |
| GET /ledger/customer/{id} | Ledger | Customer audit history |

## Tests and Docker

```bash
.venv/bin/pytest -q
docker compose up --build
```

See [DESIGN.md](DESIGN.md) for the ERD, ownership model, and core flows.

## Assumptions and limitations

- Billing cycles are 30, 90, or 365-day periods for monthly, quarterly, and yearly plans.
- This stores payment attempts; it does not contact a payment gateway.
- Ledger rows are only created through the append-only repository API; database-level update/delete permissions are out of scope.
- Production deployment should use a server database, migrations, authentication, idempotency keys, and gateway webhook verification.
