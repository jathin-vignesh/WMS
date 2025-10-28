from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.models import (
    Product, OrderItem, Order, PurchaseOrder, PurchaseOrderItem,
    Supplier, Inventory
)
from schemas.analysis_schema import (
    InventorySummaryItem, InventorySummaryOut,
    LowStockItem, SalesSummaryItem, PurchaseSummaryItem
)
from fastapi import HTTPException,status
def inventory_summary(db: Session) -> InventorySummaryOut:
    """Return stock details per product and total inventory value."""
    try:
        if db is None:
            raise ValueError("Database session not provided.")
        products = db.query(Product).all()
        if not products:
            return InventorySummaryOut(rows=[], total_stock_value=0)
        summary_rows = []
        total_stock_value = 0
 
        for p in products:
            inv = db.query(Inventory).filter(Inventory.product_id == p.id).first()
            available_quantity = inv.quantity if inv else (p.quantity or 0)
            total_value = available_quantity * (p.unit_price or 0)
            total_stock_value += total_value
 
            summary_rows.append(
                InventorySummaryItem(
                    product_id=p.id,
                    product_name=p.name,
                    available_quantity=available_quantity,
                    unit_price=p.unit_price,
                    total_value=total_value,
                )
            )
 
        return InventorySummaryOut(rows=summary_rows, total_stock_value=total_stock_value)
 
    except SQLAlchemyError as e:
        print(f"[DB Error - inventory_summary]: {e}")
        return InventorySummaryOut(rows=[], total_stock_value=0)
 
 
def low_stock(db: Session, threshold: int = 10):
    """Return products whose quantity is below threshold."""
    try:
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database session not provided."
            )
 
        if threshold < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum threshold value should be 10."
            )
 
        products = db.query(Product).all()
        if not products:
            return []
 
        low_stock_items = []
        inventories = db.query(Inventory).all()
        inv_map = {inv.product_id: inv.quantity for inv in inventories}
 
        for p in products:
            qty = inv_map.get(p.id, p.quantity or 0)
 
            if qty <= threshold:
                low_stock_items.append(
                    LowStockItem(
                        product_id=p.id,
                        product_name=p.name,
                        available_quantity=qty,
                        threshold=threshold
                    )
                )
 
        return low_stock_items
 
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred: {str(e)}"
        )
 
    except HTTPException:
        raise
 
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
 
 
def sales_summary(db: Session, limit: int = 50):
    """Return total quantity sold and total revenue per product."""
    try:
        if db is None:
            raise ValueError("Database session not provided.")
 
        products = db.query(Product).all()
        if not products:
            return []
 
        summary = []
 
        for p in products:
            items = (
                db.query(OrderItem)
                .join(Order, Order.id == OrderItem.order_id)
                .filter(OrderItem.product_id == p.id)
                .filter(Order.status.in_(["Shipped", "Delivered", "Shipment started", "received","Pending","accepted"]))
                .all()
            )
 
            if not items:
                continue
 
            total_sold = sum(i.quantity or 0 for i in items)
            total_revenue = sum((i.quantity or 0) * (i.price or 0) for i in items)
 
            if total_sold > 0:
                summary.append(
                    SalesSummaryItem(
                        product_id=p.id,
                        product_name=p.name,
                        total_sold=total_sold,
                        total_revenue=total_revenue
                    )
                )
 
        summary.sort(key=lambda x: x.total_revenue, reverse=True)
        return summary[:limit]
 
    except SQLAlchemyError as e:
        print(f"[DB Error - sales_summary]: {e}")
        return []
    except Exception as e:
        print(f"[Error - sales_summary]: {e}")
        return []
 
 
def purchase_summary(db: Session, only_received: bool = True, limit: int = 50):
    """Return purchase totals per supplier."""
    try:
        if db is None:
            raise ValueError("Database session not provided.")
 
        status_filter = "received" if only_received else "pending"
        suppliers = db.query(Supplier).all()
        if not suppliers:
            return []
 
        summary = []
 
        for s in suppliers:
            orders = (
                db.query(PurchaseOrder)
                .filter(PurchaseOrder.supplier_id == s.id)
                .filter(PurchaseOrder.status == status_filter)
                .all()
            )
 
            total_ordered_quantity = 0
            total_received_quantity = 0
            total_received_value = 0
            purchase_orders_count = len(orders)
 
            for order in orders:
                items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.order_id == order.id).all()
                for item in items:
                    total_ordered_quantity += item.quantity or 0
                    total_received_quantity += getattr(item, "received_quantity", 0)
                    total_received_value += (
                        getattr(item, "received_quantity", 0) * (item.unit_cost or 0)
                    )
 
            summary.append(
                PurchaseSummaryItem(
                    supplier_id=s.id,
                    supplier_name=s.name,
                    total_ordered_quantity=total_ordered_quantity,
                    total_received_quantity=total_received_quantity,
                    total_received_value=total_received_value,
                    purchase_orders_count=purchase_orders_count
                )
            )
 
        summary.sort(key=lambda x: x.total_received_value, reverse=True)
        return summary[:limit]
 
    except SQLAlchemyError as e:
        print(f"[DB Error - purchase_summary]: {e}")
        return []
    except Exception as e:
        print(f"[Error - purchase_summary]: {e}")
        return []
 
 
def total_stock_value(db: Session):
    """Return the total value of all stock items in inventory."""
    try:
        if db is None:
            raise ValueError("Database session not provided.")
 
        products = db.query(Product).all()
        if not products:
            return {"total_stock_value": 0}
 
        total_value = 0
 
        for p in products:
            inv = db.query(Inventory).filter(Inventory.product_id == p.id).first()
            qty = inv.quantity if inv else (p.quantity or 0)
            total_value += qty * (p.unit_price or 0)
 
        return {"total_stock_value": round(float(total_value), 2)}
 
    except SQLAlchemyError as e:
        print(f"[DB Error - total_stock_value]: {e}")
        return {"total_stock_value": 0}
    except Exception as e:
        print(f"[Error - total_stock_value]: {e}")
        return {"total_stock_value": 0}
 