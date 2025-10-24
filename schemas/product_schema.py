from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re

# ---------------- CATEGORY ----------------
class CategoryBase(BaseModel):
    name: str = Field(..., example="Electronics")

    @field_validator("name")
    def name_must_be_valid(cls, v: str) -> str:
        # Only letters and spaces allowed
        if not re.match(r"^[A-Za-z ]+$", v.strip()):
            raise ValueError("Category name must contain only letters and spaces, cannot be a number")
        return v.strip()

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# ---------------- PRODUCT ----------------
class ProductBase(BaseModel):
    name: str = Field(..., example="Battery Pack")
    sku: str = Field(..., example="BAT-001")
    category_id: Optional[int] = None
    unit_price: float = Field(..., example=100.0)

    @field_validator("unit_price")
    def unit_price_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Unit price must be greater than 0")
        return v

    @field_validator("category_id")
    def category_id_must_be_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("Category ID must be greater than 0")
        return v

class ProductCreate(ProductBase):
    quantity: int = Field(..., example=10)

    @field_validator("quantity")
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    category_id: Optional[int] = None
    unit_price: Optional[float] = None
    quantity: Optional[int] = None

    @field_validator("unit_price")
    def unit_price_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Unit price must be greater than 0")
        return v

    @field_validator("quantity")
    def quantity_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Quantity must be greater than or equal to 0")
        return v

    @field_validator("category_id")
    def category_id_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("Category ID must be greater than 0")
        return v

class Product(ProductBase):
    id: int
    quantity: int
    category: Optional[Category] = None

    class Config:
        from_attributes = True

# ---------------- STOCK ADJUSTMENT ----------------
class StockAdjustment(BaseModel):
    adjustment: int = Field(..., example=-5)
    reason: Optional[str] = Field(None, example="damaged item")

    @field_validator("adjustment")
    def adjustment_nonzero(cls, v: int) -> int:
        if v == 0:
            raise ValueError("Adjustment cannot be 0")
        return v
