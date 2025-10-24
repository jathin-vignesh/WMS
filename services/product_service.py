from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException,status
from typing import List, Optional
from models import models
from schemas import product_schema as schemas

# --------- PRODUCTS ---------
def create_product(db: Session, product_in: schemas.ProductCreate) -> models.Product:
    # Check if category exists
    category = db.query(models.Category).filter(models.Category.id == product_in.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {product_in.category_id} not found"
        )

    # Create product
    product = models.Product(**product_in.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def list_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
    return db.query(models.Product).offset(skip).limit(limit).all()

def update_product(db: Session, product_id: int, patch: schemas.ProductUpdate) -> models.Product:
    product = get_product(db, product_id)
    update_data = patch.dict(exclude_unset=True)

    # Validate category
    if "category_id" in update_data and update_data["category_id"] is not None:
        category = db.query(models.Category).filter(models.Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=400, detail=f"Category ID {update_data['category_id']} not found")

    # Validate unit price
    if "unit_price" in update_data and update_data["unit_price"] is not None and update_data["unit_price"] <= 0:
        raise HTTPException(status_code=400, detail="Unit price must be greater than 0")

    # Validate quantity
    if "quantity" in update_data and update_data["quantity"] is not None and update_data["quantity"] <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    # Apply updates
    for field, value in update_data.items():
        setattr(product, field, value)

    db.add(product)
    db.commit()
    db.refresh(product)

    return product

def adjust_stock(db: Session, product_id: int, adjustment: int) -> models.Product:
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_qty = product.quantity + adjustment
    if new_qty < 0:
        raise HTTPException(status_code=400, detail="Quantity cannot go below zero")

    product.quantity = new_qty
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
