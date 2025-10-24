from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from schemas.order_schema import OrderCreate, OrderResponse, UpdateOrderStatus
from services.order_service import create_order, list_orders, update_order_status,list_shipped_orders
from services.order_service import trigger_shipment

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse)
def create_new_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    order = create_order(db, order_data)
    return order

@router.get("/", response_model=List[OrderResponse])
def get_all_orders(db: Session = Depends(get_db)):
    return list_orders(db)

@router.put("/{id}/status", response_model=OrderResponse)
def change_order_status(id: int, status_data: UpdateOrderStatus, db: Session = Depends(get_db)):
    order = update_order_status(db, id, status_data.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/{id}/ship", response_model=OrderResponse)
def ship_order(id: int, db: Session = Depends(get_db)):
    order = trigger_shipment(db, id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/shipped", response_model=List[OrderResponse])
def get_shipped_orders(db: Session = Depends(get_db)):
    orders = list_shipped_orders(db)
    if not orders:
        raise HTTPException(status_code=404, detail="No shipped orders found")
    return orders