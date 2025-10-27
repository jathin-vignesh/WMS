from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.auth_helper import staff_required
from schemas import supplier_schema as schemas
from services import supplier_service

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@router.post("/", response_model=schemas.SupplierOut)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(staff_required)):
    return supplier_service.create_supplier(db, supplier)

@router.get("/", response_model=list[schemas.SupplierOut])
def get_suppliers(db: Session = Depends(staff_required)):
    return supplier_service.get_suppliers(db)

@router.get("/{supplier_id}/summary")
def get_supplier_order_summary(supplier_id: int, db: Session = Depends(staff_required)):
    try:
        return supplier_service.get_supplier_order_summary(db, supplier_id)
    except HTTPException as e:
        raise e