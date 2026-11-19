from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class PlanCreate(BaseModel):
    name: str
    description: str | None = None
    billing_cycle: str = "monthly"
    price: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
class PlanUpdate(BaseModel):
    name: str | None = None; description: str | None = None; billing_cycle: str | None = None
    price: Decimal | None = Field(default=None, gt=0); currency: str | None = Field(default=None, min_length=3, max_length=3); is_active: bool | None = None
class PlanOut(PlanCreate, ORMModel): id: int; is_active: bool; created_at: datetime; updated_at: datetime

class CustomerCreate(BaseModel): name: str; email: EmailStr; company: str | None = None
class CustomerOut(CustomerCreate, ORMModel): id: int; status: str; created_at: datetime

class SubscriptionCreate(BaseModel): customer_id: int; plan_id: int
class SubscriptionOut(ORMModel): id: int; customer_id: int; plan_id: int; status: str; start_date: datetime; current_period_start: datetime; current_period_end: datetime

class InvoiceCreate(BaseModel): subscription_id: int; period_start: datetime | None = None; period_end: datetime | None = None
class InvoiceOut(ORMModel): id: int; subscription_id: int; customer_id: int; amount_due: Decimal; amount_paid: Decimal; currency: str; status: str; period_start: datetime; period_end: datetime; due_date: datetime; created_at: datetime

class PaymentCreate(BaseModel): invoice_id: int; amount: Decimal = Field(gt=0); currency: str = Field(min_length=3, max_length=3); status: str; provider_reference: str; failure_reason: str | None = None
class PaymentOut(ORMModel): id: int; invoice_id: int; amount: Decimal; currency: str; status: str; provider_reference: str; failure_reason: str | None; created_at: datetime
class PaymentResult(BaseModel): payment: PaymentOut; invoice: InvoiceOut
class LedgerOut(ORMModel): id: int; customer_id: int; invoice_id: int | None; entry_type: str; amount: Decimal; currency: str; reference_id: str; description: str | None; created_at: datetime
