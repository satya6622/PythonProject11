from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import *
from app.services import services
router=APIRouter()
def deps(db:Session=Depends(get_db)): return services(db)
def commit(x): x[5][0].db.commit()
@router.post('/plans',response_model=PlanOut,status_code=201)
def create_plan(data:PlanCreate,x=Depends(deps)): obj=x[0].create(data); commit(x); return obj
@router.get('/plans',response_model=list[PlanOut])
def list_plans(x=Depends(deps)): return x[5][0].list()
@router.patch('/plans/{id}',response_model=PlanOut)
def update_plan(id:int,data:PlanUpdate,x=Depends(deps)): obj=x[0].update(id,data); commit(x); return obj
@router.post('/customers',response_model=CustomerOut,status_code=201)
def create_customer(data:CustomerCreate,x=Depends(deps)): obj=x[1].create(data); commit(x); return obj
@router.get('/customers',response_model=list[CustomerOut])
def list_customers(x=Depends(deps)): return x[5][1].list()
@router.get('/customers/{id}',response_model=CustomerOut)
def get_customer(id:int,x=Depends(deps)): return x[5][1].get(id) or (_ for _ in ()).throw(HTTPException(404,'Customer not found'))
@router.post('/subscriptions',response_model=SubscriptionOut,status_code=201)
def create_subscription(data:SubscriptionCreate,x=Depends(deps)): obj=x[2].create(data); commit(x); return obj
@router.get('/subscriptions',response_model=list[SubscriptionOut])
def list_subscriptions(x=Depends(deps)): return x[5][2].list()
@router.post('/subscriptions/{id}/cancel',response_model=SubscriptionOut)
def cancel_subscription(id:int,x=Depends(deps)): obj=x[2].cancel(id); commit(x); return obj
@router.post('/invoices/generate',response_model=InvoiceOut,status_code=201)
def generate_invoice(data:InvoiceCreate,x=Depends(deps)): obj=x[3].generate(data); commit(x); return obj
@router.get('/invoices',response_model=list[InvoiceOut])
def list_invoices(x=Depends(deps)): return x[5][3].list()
@router.get('/invoices/{id}',response_model=InvoiceOut)
def get_invoice(id:int,x=Depends(deps)): return x[5][3].get(id) or (_ for _ in ()).throw(HTTPException(404,'Invoice not found'))
@router.post('/payments/record',response_model=PaymentResult,status_code=201)
def record_payment(data:PaymentCreate,x=Depends(deps)): payment,invoice=x[4].record(data); commit(x); return {'payment':payment,'invoice':invoice}
@router.get('/ledger/customer/{id}',response_model=list[LedgerOut])
def customer_ledger(id:int,x=Depends(deps)): return x[5][4].for_customer(id)
