from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from schemas import product_schema as schemas
from services import categories_service as categories_crud
from utils.auth_helper import staff_required

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(category_in: schemas.CategoryCreate, db: Session = Depends(staff_required)):
    return categories_crud.create_category(db, category_in.name)

@router.get("/", response_model=List[schemas.Category])
def list_categories(db: Session = Depends(staff_required)):
    return categories_crud.list_categories(db)

@router.get("/{category_id}", response_model=schemas.Category)
def get_category(category_id: int, db: Session = Depends(staff_required)):
    category = categories_crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
