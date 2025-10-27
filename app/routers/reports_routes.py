from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from utils.auth_helper import staff_required
from services.analysis_service import inventory_summary, low_stock, sales_summary, purchase_summary, total_stock_value
from schemas import analysis_schema
from pydantic import BaseModel

router = APIRouter(prefix="/reports", tags=["Analytics & Reports"])

# Total Stock Value schema
class TotalStockValue(analysis_schema.BaseModel):
    total_stock_value: float

@router.get("/inventory-summary", response_model=analysis_schema.InventorySummaryOut)
def get_inventory_summary(db: Session = Depends(staff_required)):
    return inventory_summary(db)


@router.get("/low-stock", response_model=List[analysis_schema.LowStockItem])
def get_low_stock(threshold: int = Query(10, gt=0, description="Stock threshold"), db: Session = Depends(staff_required)):
    return low_stock(db, threshold=threshold)


@router.get("/sales-summary", response_model=List[analysis_schema.SalesSummaryItem])
def get_sales_summary(limit: int = Query(50, gt=0, description="Limit number of records"), db: Session = Depends(staff_required)):
    return sales_summary(db, limit=limit)

@router.get("/purchase-summary", response_model=List[analysis_schema.PurchaseSummaryItem])
def get_purchase_summary(only_received: bool = Query(True, description="Include only received orders"), limit: int = Query(50, gt=0), db: Session = Depends(staff_required)):
    return purchase_summary(db, only_received=only_received, limit=limit)

@router.get("/total-stock-value", response_model=TotalStockValue)
def get_total_stock_value(db: Session = Depends(staff_required)):
    return total_stock_value(db)