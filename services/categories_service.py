from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from models import models
from schemas import product_schema as schemas
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

def create_category(db: Session, name: str) -> models.Category:
    try:
        existing_categories = db.query(models.Category).all()
        for category in existing_categories:
            if category.name.lower() == name.lower():
                raise HTTPException(
                    status_code=400,
                    detail=f"Category with name '{name}' already exists."
                )
 
        category = models.Category(name=name)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
 
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Category with name '{name}' already exists."
        )

def list_categories(db: Session) -> List[models.Category]:
    result = db.execute(select(models.Category))
    return result.scalars().all()

def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    return db.get(models.Category, category_id)
