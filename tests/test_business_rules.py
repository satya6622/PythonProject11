import os
import sys
from uuid import uuid4
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["DATABASE_URL"] = "sqlite:///./test_subledger.db"
Path("test_subledger.db").unlink(missing_ok=True)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def create_plan(price="30.00", active=True):
    response = client.post("/plans", json={"name": "Pro", "price": price, "currency": "USD"})
    assert response.status_code == 201
    if not active:
        response = client.patch(f"/plans/{response.json()['id']}", json={"is_active": False})
    return response.json()

def create_customer(email=None):
    email = email or f"ada-{uuid4().hex}@example.com"
    response = client.post("/customers", json={"name": "Ada", "email": email})
    assert response.status_code == 201
    return response.json()

def create_invoice():
    customer, plan = create_customer(), create_plan()
    sub = client.post("/subscriptions", json={"customer_id": customer["id"], "plan_id": plan["id"]})
    assert sub.status_code == 201
    invoice = client.post("/invoices/generate", json={"subscription_id": sub.json()["id"]})
    assert invoice.status_code == 201
    return customer, invoice.json()

def test_plan_price_must_be_positive():
    assert client.post("/plans", json={"name":"Bad", "price":"0"}).status_code == 422

def test_customer_email_is_unique():
    create_customer("same@example.com")
    assert client.post("/customers", json={"name":"Other", "email":"same@example.com"}).status_code == 400

def test_inactive_plan_cannot_be_subscribed():
    customer, plan = create_customer("inactive@example.com"), create_plan(active=False)
    assert client.post("/subscriptions", json={"customer_id":customer["id"],"plan_id":plan["id"]}).status_code == 400

def test_duplicate_active_subscription_is_rejected():
    customer, plan = create_customer("duplicate@example.com"), create_plan()
    assert client.post("/subscriptions", json={"customer_id":customer["id"],"plan_id":plan["id"]}).status_code == 201
    assert client.post("/subscriptions", json={"customer_id":customer["id"],"plan_id":plan["id"]}).status_code == 400

def test_successful_payments_update_partial_and_paid_status():
    _, invoice = create_invoice()
    payload = {"invoice_id":invoice["id"],"currency":"USD","status":"success"}
    first = client.post("/payments/record", json={**payload,"amount":"10.00","provider_reference":"p1"})
    assert first.status_code == 201 and first.json()["invoice"]["status"] == "partially_paid"
    second = client.post("/payments/record", json={**payload,"amount":"20.00","provider_reference":"p2"})
    assert second.status_code == 201 and second.json()["invoice"]["status"] == "paid"

def test_failed_payment_does_not_change_amount_paid_and_is_ledgered():
    customer, invoice = create_invoice()
    result = client.post("/payments/record", json={"invoice_id":invoice["id"],"amount":"10.00","currency":"USD","status":"failed","provider_reference":"declined","failure_reason":"card declined"})
    assert result.status_code == 201 and result.json()["invoice"]["amount_paid"] == "0.00"
    entries = client.get(f"/ledger/customer/{customer['id']}").json()
    assert [entry["entry_type"] for entry in entries] == ["invoice_created", "payment_failure"]

def test_successful_payment_cannot_exceed_balance():
    _, invoice = create_invoice()
    response = client.post("/payments/record", json={"invoice_id":invoice["id"],"amount":"30.01","currency":"USD","status":"success","provider_reference":"too-much"})
    assert response.status_code == 400
