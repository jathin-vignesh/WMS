from pydantic import BaseModel
from typing import Optional, List

class InventorySummaryItem(BaseModel):
    product_id: int
    product_name: str
    available_quantity: int
    unit_price: float
    total_value: float
    total_ordered_quantity: int
    total_received_quantity: int

class InventorySummaryOut(BaseModel):
    rows: List[InventorySummaryItem]
    total_stock_value: float

class LowStockItem(BaseModel):
    product_id: int
    product_name: str
    available_quantity: int
    threshold: Optional[int] = 10

class SalesSummaryItem(BaseModel):
    product_id: int
    product_name: str
    total_sold: int
    total_revenue: float

class SalesSummaryOut(BaseModel):
    rows: List[SalesSummaryItem]
    total_revenue: float

class PurchaseSummaryItem(BaseModel):
    supplier_id: int
    supplier_name: str
    total_ordered_quantity: int
    total_received_quantity: int
    total_received_value: float
    purchase_orders_count: int

class PurchaseSummaryOut(BaseModel):
    status_summary: Optional[List[dict]]
    supplier_summary: List[PurchaseSummaryItem]