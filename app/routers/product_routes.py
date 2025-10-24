from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from schemas import product_schema as schemas
from services import product_service as product_crud
from db import get_db

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    return product_crud.create_product(db, product_in)

@router.get("/", response_model=List[schemas.Product])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return product_crud.list_products(db, skip, limit)

@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(get_db)):
    return product_crud.update_product(db, product_id, product_update)

@router.patch("/{product_id}/stock", response_model=schemas.Product)
def adjust_stock(product_id: int, adj: schemas.StockAdjustment, db: Session = Depends(get_db)):
    return product_crud.adjust_stock(db, product_id, adj.adjustment)
