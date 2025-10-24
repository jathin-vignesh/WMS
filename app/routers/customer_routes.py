from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from schemas.customer_schema import CustomerCreate, CustomerResponse
from typing import List
from services.customer_service import create_customer_service
from models.models import Customer

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/", response_model=CustomerResponse | dict)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    return create_customer_service(customer, db)

@router.get("/", response_model=List[CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()
