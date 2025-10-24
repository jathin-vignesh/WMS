from pydantic import BaseModel

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderItemCreate(BaseModel):
    product_id: int
    quantity : int

class OrderItemResponse(OrderItemBase):
    id: int

    class Config:
        from_attributes = True
