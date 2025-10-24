from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from models import models
from schemas import product_schema as schemas

def create_category(db: Session, name: str) -> models.Category:
    category = models.Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def list_categories(db: Session) -> List[models.Category]:
    result = db.execute(select(models.Category))
    return result.scalars().all()

def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    return db.get(models.Category, category_id)
