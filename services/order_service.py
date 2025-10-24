from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.models import Order
from models.models import OrderItem
from models.models import Customer
from models.models import Product
from schemas.order_schema import OrderCreate

# Create a new Order
def create_order(db: Session, order_data: OrderCreate):
    # Step 1: Validate Customer
    customer = db.query(Customer).filter(Customer.id == order_data.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {order_data.customer_id} not found"
        )

    # Step 2: Validate Products and Calculate Total
    total = 0
    valid_items = []

    for item in order_data.items:
        # Check for invalid quantity
        if item.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quantity for product ID {item.product_id} must be greater than 0"
            )

        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )

        # Check stock availability
        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for product {product.name}"
            )

        price = item.quantity * product.unit_price
        total += price
        valid_items.append((product, item, price))

    # Step 3: Create Order
    order = Order(customer_id=order_data.customer_id, total_amount=total)
    db.add(order)
    db.commit()
    db.refresh(order)

    # Step 4: Create Order Items & Update Inventory
    for product, item, price in valid_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=price
        )
        db.add(order_item)
        product.quantity -= item.quantity  # Reduce stock

    db.commit()
    db.refresh(order)
    return order


# Trigger Shipment for an Order
def trigger_shipment(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order ID not found")
    if order.status == "Shipment started":
        raise HTTPException(status_code=400, detail="Status already updated")

    order.status = "Shipment started"
    db.commit()
    db.refresh(order)
    return order



# List Orders (Not Yet Shipped)
def list_orders(db: Session):
    return db.query(Order).filter(Order.status != "Shipment started").all()



# List Shipped Orders
def list_shipped_orders(db: Session):
    return db.query(Order).filter(Order.status == "Shipment started").all()



# Update Order Status
def update_order_status(db: Session, order_id: int, status: str):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status
    db.commit()
    db.refresh(order)
    return order