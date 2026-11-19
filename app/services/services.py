from datetime import timedelta
from decimal import Decimal
from fastapi import HTTPException
from app.models import Customer, Invoice, LedgerEntry, PaymentAttempt, Plan, Subscription
from app.repositories import CustomerRepository, InvoiceRepository, LedgerRepository, PaymentAttemptRepository, PlanRepository, SubscriptionRepository

def missing(resource): raise HTTPException(404, f"{resource} not found")
def invalid(message): raise HTTPException(400, message)
class PlanService:
 def __init__(self,repo): self.repo=repo
 def create(self,data):
  values=data.model_dump(); values["currency"]=data.currency.upper()
  return self.repo.save(Plan(**values))
 def update(self,id,data):
  plan=self.repo.get(id) or missing("Plan")
  for key,value in data.model_dump(exclude_unset=True).items(): setattr(plan,key,value.upper() if key=="currency" else value)
  return self.repo.save(plan)
class CustomerService:
 def __init__(self,repo): self.repo=repo
 def create(self,data):
  if self.repo.by_email(str(data.email)): invalid("Customer email must be unique")
  values=data.model_dump(); values["email"]=str(data.email).lower()
  return self.repo.save(Customer(**values))
class SubscriptionService:
 def __init__(self,customers,plans,repo): self.customers,self.plans,self.repo=customers,plans,repo
 def create(self,data):
  customer=self.customers.get(data.customer_id) or missing("Customer"); plan=self.plans.get(data.plan_id) or missing("Plan")
  if customer.status!="active": invalid("Customer is not active")
  if not plan.is_active: invalid("A subscription cannot be created for an inactive plan")
  if self.repo.active_for(customer.id,plan.id): invalid("Customer already has an active subscription to this plan")
  from app.models.entities import now
  start=now(); days={"yearly":365,"quarterly":90}.get(plan.billing_cycle,30)
  return self.repo.save(Subscription(customer_id=customer.id,plan_id=plan.id,start_date=start,current_period_start=start,current_period_end=start+timedelta(days=days)))
 def cancel(self,id):
  sub=self.repo.get(id) or missing("Subscription")
  if sub.status!="active": invalid("Only active subscriptions can be cancelled")
  sub.status="cancelled"; return self.repo.save(sub)
class LedgerService:
 def __init__(self,repo): self.repo=repo
 def append(self,**kwargs): return self.repo.append(LedgerEntry(**kwargs))
class InvoiceService:
 def __init__(self,subscriptions,plans,invoices,ledger): self.subscriptions,self.plans,self.invoices,self.ledger=subscriptions,plans,invoices,ledger
 def generate(self,data):
  sub=self.subscriptions.get(data.subscription_id) or missing("Subscription")
  if sub.status!="active": invalid("Invoices can only be generated for active subscriptions")
  plan=self.plans.get(sub.plan_id) or missing("Plan"); start=data.period_start or sub.current_period_start; end=data.period_end or sub.current_period_end
  if end<=start: invalid("period_end must be after period_start")
  invoice=self.invoices.save(Invoice(subscription_id=sub.id,customer_id=sub.customer_id,amount_due=plan.price,amount_paid=Decimal("0.00"),currency=plan.currency,status="issued",period_start=start,period_end=end,due_date=end))
  self.ledger.append(customer_id=invoice.customer_id,invoice_id=invoice.id,entry_type="invoice_created",amount=invoice.amount_due,currency=invoice.currency,reference_id=f"invoice:{invoice.id}",description="Invoice issued")
  return invoice
class PaymentService:
 def __init__(self,invoices,payments,ledger): self.invoices,self.payments,self.ledger=invoices,payments,ledger
 def record(self,data):
  invoice=self.invoices.get(data.invoice_id) or missing("Invoice"); status=data.status.lower()
  if data.currency.upper()!=invoice.currency.upper(): invalid("Payment currency must match invoice currency")
  if status not in {"success","failed"}: invalid("Payment status must be success or failed")
  if status=="success" and data.amount>invoice.amount_due-invoice.amount_paid: invalid("Payment cannot exceed the remaining unpaid amount")
  payment=self.payments.save(PaymentAttempt(invoice_id=invoice.id,amount=data.amount,currency=data.currency.upper(),status=status,provider_reference=data.provider_reference,failure_reason=data.failure_reason))
  if status=="success":
   invoice.amount_paid+=data.amount; invoice.status="paid" if invoice.amount_paid==invoice.amount_due else "partially_paid"; self.invoices.save(invoice); event,desc="payment_success","Successful payment recorded"
  else: event,desc="payment_failure",data.failure_reason or "Payment failed"
  self.ledger.append(customer_id=invoice.customer_id,invoice_id=invoice.id,entry_type=event,amount=data.amount,currency=invoice.currency,reference_id=f"payment:{payment.id}",description=desc)
  return payment,invoice
def services(db):
 plans,customers,subs,invoices=PlanRepository(db),CustomerRepository(db),SubscriptionRepository(db),InvoiceRepository(db); ledger=LedgerService(LedgerRepository(db))
 return PlanService(plans),CustomerService(customers),SubscriptionService(customers,plans,subs),InvoiceService(subs,plans,invoices,ledger),PaymentService(invoices,PaymentAttemptRepository(db),ledger),(plans,customers,subs,invoices,LedgerRepository(db))
