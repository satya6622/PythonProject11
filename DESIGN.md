# SubLedger low-level design

## ERD

```text
Customer 1---* Subscription *---1 Plan
Customer 1---* Invoice *---1 Subscription
Invoice  1---* PaymentAttempt
Customer 1---* LedgerEntry *---0..1 Invoice
```

## Layer responsibilities

| Layer | Responsibility |
|---|---|
| API routes | HTTP validation, dependency injection, response contracts, transaction commit |
| Services | Domain rules and orchestration of repository calls |
| Repositories | Focused read/write queries only; no business decisions |
| Models | SQLAlchemy persistence mappings and relationships |
| Schemas | Pydantic request validation and response serialization |

The implementation uses the Repository pattern: services depend on small repository interfaces, keeping business rules testable and persistence replaceable. Dependency injection provides the session and assembles services per request.

## Business-rule ownership

| Rule | Owner |
|---|---|
| Price is greater than zero | `PlanCreate` / `PlanUpdate` schema |
| Unique email | `CustomerService`, backed by database unique constraint |
| Inactive plans cannot be subscribed | `SubscriptionService` |
| One active customer-plan subscription | `SubscriptionService` |
| Invoice amount is current plan price | `InvoiceService` |
| Payment cannot exceed balance | `PaymentService` |
| Partial / full invoice state | `PaymentService` |
| Failed payment never changes paid amount | `PaymentService` |
| Ledger is append-only and referenceable | `LedgerService` / `LedgerRepository` |

## Invoice generation flow

`POST /invoices/generate` -> `InvoiceService` loads subscription -> validates active -> loads plan -> selects requested or subscription billing period -> creates issued invoice using plan price -> appends `invoice_created` entry with `invoice:<id>` reference -> commits.

## Payment recording flow

`POST /payments/record` -> `PaymentService` loads invoice -> validates currency, status, and remaining balance -> writes immutable `PaymentAttempt` -> on success increments `amount_paid` and assigns `partially_paid` or `paid`; on failure it leaves the invoice unchanged -> appends `payment_success` or `payment_failure` ledger event using `payment:<id>` -> commits.
