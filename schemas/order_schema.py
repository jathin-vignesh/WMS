from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .order_item_schema import OrderItemCreate, OrderItemResponse

class OrderBase(BaseModel):
    customer_id: int

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    status: str
    total_amount: float
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True

class UpdateOrderStatus(BaseModel):
    status: str
