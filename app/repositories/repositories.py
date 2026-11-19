from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Customer, Invoice, LedgerEntry, PaymentAttempt, Plan, Subscription

class PlanRepository:
 def __init__(self, db: Session): self.db = db
 def get(self, id): return self.db.get(Plan, id)
 def list(self): return self.db.scalars(select(Plan).order_by(Plan.id)).all()
 def save(self, obj): self.db.add(obj); self.db.flush(); return obj
class CustomerRepository:
 def __init__(self, db): self.db=db
 def get(self,id): return self.db.get(Customer,id)
 def list(self): return self.db.scalars(select(Customer).order_by(Customer.id)).all()
 def by_email(self,email): return self.db.scalar(select(Customer).where(Customer.email == email))
 def save(self,obj): self.db.add(obj); self.db.flush(); return obj
class SubscriptionRepository:
 def __init__(self,db): self.db=db
 def get(self,id): return self.db.get(Subscription,id)
 def list(self): return self.db.scalars(select(Subscription).order_by(Subscription.id)).all()
 def active_for(self,customer_id,plan_id): return self.db.scalar(select(Subscription).where(Subscription.customer_id==customer_id, Subscription.plan_id==plan_id, Subscription.status=="active"))
 def save(self,obj): self.db.add(obj); self.db.flush(); return obj
class InvoiceRepository:
 def __init__(self,db): self.db=db
 def get(self,id): return self.db.get(Invoice,id)
 def list(self): return self.db.scalars(select(Invoice).order_by(Invoice.id)).all()
 def save(self,obj): self.db.add(obj); self.db.flush(); return obj
class PaymentAttemptRepository:
 def __init__(self,db): self.db=db
 def save(self,obj): self.db.add(obj); self.db.flush(); return obj
class LedgerRepository:
 def __init__(self,db): self.db=db
 def for_customer(self,customer_id): return self.db.scalars(select(LedgerEntry).where(LedgerEntry.customer_id==customer_id).order_by(LedgerEntry.id)).all()
 def append(self,obj): self.db.add(obj); self.db.flush(); return obj
