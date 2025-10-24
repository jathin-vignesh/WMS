from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import re
from models import models  # All models are here
from schemas import supplier_schema as schemas  # Your Pydantic schemas

# ----------------- Supplier Functions ----------------- #
def create_supplier(db: Session, supplier: schemas.SupplierCreate):
    name = supplier.name.strip() if supplier.name else ""
    address = supplier.address.strip() if supplier.address else ""
    contact = supplier.contact.strip() if supplier.contact else ""

    if name.lower() == "string" and address.lower() == "string" and contact.lower() == "string":
        raise HTTPException(
            status_code=400,
            detail="Please enter valid supplier information before submitting."
        )

    if not name:
        raise HTTPException(status_code=400, detail="Supplier name is required.")
    if not address:
        raise HTTPException(status_code=400, detail="Supplier address is required.")
    if not contact:
        raise HTTPException(status_code=400, detail="Supplier contact number is required.")
    if not re.match(r"^[6-9]\d{9}$", contact):
        raise HTTPException(
            status_code=400,
            detail="Enter a valid 10-digit mobile number starting with 6, 7, 8, or 9."
        )

    existing = db.query(models.Supplier).filter(models.Supplier.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Supplier with name '{name}' already exists.")

    new_supplier = models.Supplier(
        name=name,
        contact=contact,
        address=address,
    )
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)
    return new_supplier


def get_suppliers(db: Session):
    suppliers = db.query(models.Supplier).all()
    if not suppliers:
        raise HTTPException(status_code=404, detail="No suppliers found. Please create a supplier first.")
    return suppliers

# ----------------- Purchase Order Functions ----------------- #
def create_purchase_order(db: Session, po_data: schemas.PurchaseOrderCreate):
    # Basic empty form validation
    if (
        (not po_data.supplier_id or po_data.supplier_id == 0)
        and len(po_data.items) == 1
        and po_data.items[0].product_id == 0
        and po_data.items[0].quantity == 0
        and po_data.items[0].unit_cost == 0
    ):
        raise HTTPException(status_code=400, detail="Please enter valid purchase order information before submitting.")

    # Validate supplier ID
    if not po_data.supplier_id or po_data.supplier_id <= 0:
        raise HTTPException(status_code=400, detail="Enter a valid Supplier ID (must be a positive number).")

    supplier_exists = db.query(models.Supplier).filter(models.Supplier.id == po_data.supplier_id).first()
    if not supplier_exists:
        raise HTTPException(status_code=404, detail=f"Supplier with ID {po_data.supplier_id} does not exist.")

    # Validate items
    if not po_data.items or len(po_data.items) == 0:
        raise HTTPException(status_code=400, detail="Please enter at least one product item for the purchase order.")

    for i, item in enumerate(po_data.items, start=1):
        if not item.product_id or item.product_id <= 0:
            raise HTTPException(status_code=400, detail=f"Item {i}: Enter a valid Product ID.")
        product_exists = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product_exists:
            raise HTTPException(status_code=404, detail=f"Item {i}: Product with ID {item.product_id} not found.")
        if not item.quantity or item.quantity <= 0:
            raise HTTPException(status_code=400, detail=f"Item {i}: Quantity must be greater than 0.")
        if not item.unit_cost or item.unit_cost <= 0:
            raise HTTPException(status_code=400, detail=f"Item {i}: Unit cost must be greater than 0.")

    # Create Purchase Order
    po = models.PurchaseOrder(supplier_id=po_data.supplier_id, status="pending")
    db.add(po)
    db.commit()
    db.refresh(po)

    # Add PurchaseOrderItems
    for item in po_data.items:
        po_item = models.PurchaseOrderItem(
            order_id=po.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_cost=item.unit_cost,
            received_quantity=0
        )
        db.add(po_item)
    db.commit()
    db.refresh(po)
    return po


def mark_order_received(db: Session, order_id: int, received_items: list):
    po = db.query(models.PurchaseOrder).filter(models.PurchaseOrder.id == order_id).first()
    if not po:
        raise HTTPException(status_code=404, detail=f"Purchase order {order_id} not found.")

    received_count = 0

    for received_item in received_items:
        product_id = received_item.product_id
        received_qty = received_item.received_quantity

        if received_qty <= 0:
            raise HTTPException(status_code=400, detail=f"Received quantity must be greater than 0 for product {product_id}.")

        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} does not exist.")

        item = db.query(models.PurchaseOrderItem).filter(
            models.PurchaseOrderItem.order_id == order_id,
            models.PurchaseOrderItem.product_id == product_id
        ).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Product {product_id} is not part of this purchase order.")

        if received_qty + item.received_quantity > item.quantity:
            raise HTTPException(status_code=400, detail=f"Received quantity cannot exceed ordered quantity for product {product_id}.")

        # Update received quantity
        item.received_quantity += received_qty
        received_count += 1

        # Update Inventory
        inv = db.query(models.Inventory).filter(models.Inventory.product_id == product_id).first()
        if inv:
            inv.quantity += received_qty
            inv.last_updated = datetime.utcnow()
        else:
            new_inv = models.Inventory(product_id=product_id, quantity=received_qty, last_updated=datetime.utcnow())
            db.add(new_inv)

        # Update product quantity
        product.quantity += received_qty

    # Update Purchase Order status
    all_items = po.items
    if all(i.received_quantity == i.quantity for i in all_items):
        po.status = "received"
    elif any(i.received_quantity > 0 for i in all_items):
        po.status = "partial"
    else:
        po.status = "pending"

    db.commit()
    db.refresh(po)

    if received_count == 0:
        raise HTTPException(status_code=400, detail="No valid items were updated.")

    return {
        "order_id": po.id,
        "status": po.status,
        "updated_items": received_count,
        "message": "Selected items successfully marked as received."
    }


# ----------------- Inventory & Summary Functions ----------------- #
def get_inventory(db: Session):
    return db.query(models.Inventory).all()


def get_supplier_order_summary(db: Session, supplier_id: int):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    orders = db.query(models.PurchaseOrder).filter(models.PurchaseOrder.supplier_id == supplier_id).all()

    total_pending_qty = total_received_qty = 0
    total_pending_value = total_received_value = 0.0

    for order in orders:
        for item in order.items:
            pending_qty = item.quantity - item.received_quantity
            received_qty = item.received_quantity
            pending_value = pending_qty * item.unit_cost
            received_value = received_qty * item.unit_cost

            total_pending_qty += pending_qty
            total_received_qty += received_qty
            total_pending_value += pending_value
            total_received_value += received_value

    return {
        "supplier_id": supplier.id,
        "supplier_name": supplier.name,
        "total_pending_quantity": total_pending_qty,
        "total_received_quantity": total_received_qty,
        "total_pending_value": total_pending_value,
        "total_received_value": total_received_value,
        "grand_total_value": total_pending_value + total_received_value
    }
