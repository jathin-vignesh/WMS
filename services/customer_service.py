from sqlalchemy.orm import Session
from models.models import Customer
from schemas.customer_schema import CustomerCreate

def create_customer_service(customer_data: CustomerCreate, db: Session):
    existing_customer = db.query(Customer).filter(Customer.phone == customer_data.phone).first()
    if existing_customer:
        return {"message": f"{existing_customer.name} already exists with id {existing_customer.id}"}
    new_customer = Customer(**customer_data.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer
