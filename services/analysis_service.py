# app/services/analytics_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.models import Product, OrderItem, Order,PurchaseOrder, PurchaseOrderItem, Supplier, Inventory
from schemas.analysis_schema import InventorySummaryItem, InventorySummaryOut, LowStockItem, SalesSummaryItem, PurchaseSummaryItem

# -----------------------
# 1️⃣ Inventory Summary
# -----------------------
def inventory_summary(db: Session) -> InventorySummaryOut:
    products = db.query(Product).all()
    summary_rows = []
    total_stock_value = 0.0

    for p in products:
        # Inventory quantity (fallback to Product.quantity if Inventory row missing)
        inv = db.query(Inventory).filter(Inventory.product_id == p.id).first()
        available_quantity = inv.quantity if inv else p.quantity

        # Purchase order items for this product
        po_items = db.query(PurchaseOrderItem).filter(PurchaseOrderItem.product_id == p.id).all()
        total_ordered_quantity = sum(item.quantity for item in po_items)
        total_received_quantity = sum(item.received_quantity for item in po_items)

        total_value = available_quantity * p.unit_price
        total_stock_value += total_value

        summary_rows.append(
            InventorySummaryItem(
                product_id=p.id,
                product_name=p.name,
                available_quantity=available_quantity,
                unit_price=p.unit_price,
                total_value=total_value,
                total_ordered_quantity=total_ordered_quantity,
                total_received_quantity=total_received_quantity
            )
        )

    return InventorySummaryOut(
        rows=summary_rows,
        total_stock_value=total_stock_value
    )
# -----------------------
# 2️⃣ Low Stock
# -----------------------
def low_stock(db: Session, threshold: int = 10):
    results = (
        db.query(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            func.coalesce(func.sum(PurchaseOrderItem.received_quantity), 0).label("total_received_quantity")
        )
        .outerjoin(PurchaseOrderItem, PurchaseOrderItem.product_id == Product.id)
        .group_by(Product.id, Product.name)
        .having(func.sum(PurchaseOrderItem.received_quantity) <= threshold)
        .order_by(func.sum(PurchaseOrderItem.received_quantity).asc())
        .all()
    )

    return [
        LowStockItem(
            product_id=r.product_id,
            product_name=r.product_name,
            total_received_quantity=int(r.total_received_quantity or 0),  # <- matches schema
            threshold=threshold
        )
        for r in results
    ]

# -----------------------
# 3️⃣ Sales Summary
# -----------------------
def sales_summary(db: Session, limit: int = 50):
    """
    Returns total quantity sold and total revenue per product (only delivered/shipped orders).
    """
    results = (
        db.query(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            func.coalesce(func.sum(OrderItem.quantity), 0).label("total_sold"),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.price), 0).label("total_revenue")
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(OrderItem.order)  # join Order table
        .filter(OrderItem.order.has(Order.status.in_(["Shipped", "Delivered"])))
        .group_by(Product.id, Product.name)
        .order_by(func.sum(OrderItem.quantity * OrderItem.price).desc())
        .limit(limit)
        .all()
    )

    return [
        SalesSummaryItem(
            product_id=r.product_id,
            product_name=r.product_name,
            total_sold=int(r.total_sold or 0),
            total_revenue=float(r.total_revenue or 0)
        )
        for r in results
    ]


# -----------------------
# 4️⃣ Purchase Summary
# -----------------------
def purchase_summary(db: Session, only_received: bool = True, limit: int = 50):
    """
    Returns total purchase spent per supplier.
    """
    status_filter = "received" if only_received else "pending"

    results = (
        db.query(
            Supplier.id.label("supplier_id"),
            Supplier.name.label("supplier_name"),
            func.coalesce(func.sum(PurchaseOrderItem.quantity), 0).label("total_ordered_quantity"),
            func.coalesce(func.sum(PurchaseOrderItem.received_quantity), 0).label("total_received_quantity"),
            func.coalesce(func.sum(PurchaseOrderItem.received_quantity * PurchaseOrderItem.unit_cost), 0).label("total_received_value"),
            func.count(PurchaseOrderItem.id).label("purchase_orders_count")
        )
        .join(PurchaseOrder, PurchaseOrder.supplier_id == Supplier.id)
        .join(PurchaseOrderItem, PurchaseOrderItem.order_id == PurchaseOrder.id)
        .filter(PurchaseOrder.status == status_filter)
        .group_by(Supplier.id, Supplier.name)
        .order_by(func.sum(PurchaseOrderItem.received_quantity * PurchaseOrderItem.unit_cost).desc())
        .limit(limit)
        .all()
    )

    return [
        PurchaseSummaryItem(
            supplier_id=r.supplier_id,
            supplier_name=r.supplier_name,
            total_ordered_quantity=int(r.total_ordered_quantity or 0),
            total_received_quantity=int(r.total_received_quantity or 0),
            total_received_value=float(r.total_received_value or 0),
            purchase_orders_count=int(r.purchase_orders_count or 0)
        )
        for r in results
    ]


# -----------------------
# 5️⃣ Total Stock Value
# -----------------------
def total_stock_value(db: Session):
    """
    Returns total value of all stock items in inventory.
    """
    results = (
        db.query(
            func.coalesce(func.sum(PurchaseOrderItem.received_quantity * PurchaseOrderItem.unit_cost), 0)
        ).all()
    )
    total_value = results[0][0] if results else 0
    return {"total_stock_value": round(float(total_value), 2)}