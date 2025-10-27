from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.customer_schema import CustomerCreate, CustomerResponse
from typing import List
from services.customer_service import create_customer_service
from models.models import Customer
from utils.auth_helper import staff_required

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/", response_model=CustomerResponse | dict)
def create_customer(customer: CustomerCreate, db: Session = Depends(staff_required)):
    return create_customer_service(customer, db)

@router.get("/", response_model=List[CustomerResponse])
def get_customers(db: Session = Depends(staff_required)):
    return db.query(Customer).all()
