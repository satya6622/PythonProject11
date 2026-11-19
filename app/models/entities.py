from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def now() -> datetime:
    return datetime.now(timezone.utc)

class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    billing_cycle: Mapped[str] = mapped_column(String(20), default="monthly")
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="plan")

class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    company: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="customer")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="customer")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    status: Mapped[str] = mapped_column(String(20), default="active")
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    customer: Mapped[Customer] = relationship(back_populates="subscriptions")
    plan: Mapped[Plan] = relationship(back_populates="subscriptions")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="subscription")

class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"))
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    amount_due: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(20), default="issued")
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    subscription: Mapped[Subscription] = relationship(back_populates="invoices")
    customer: Mapped[Customer] = relationship(back_populates="invoices")
    payment_attempts: Mapped[list["PaymentAttempt"]] = relationship(back_populates="invoice")

class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(20))
    provider_reference: Mapped[str] = mapped_column(String(120))
    failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    invoice: Mapped[Invoice] = relationship(back_populates="payment_attempts")

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    invoice_id: Mapped[int | None] = mapped_column(ForeignKey("invoices.id"), nullable=True)
    entry_type: Mapped[str] = mapped_column(String(40))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3))
    reference_id: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
