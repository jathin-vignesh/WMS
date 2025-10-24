from fastapi import APIRouter
from app.routers import (
    auth_routes,
    category_routes,
    product_routes,
    customer_routes,
    order_routes,
    inventory_routes,
    purchase_order_routes,
    suppliers_routes,
    reports_routes
)

router = APIRouter()

router.include_router(auth_routes.router)
router.include_router(category_routes.router)
router.include_router(product_routes.router)
router.include_router(customer_routes.router)
router.include_router(order_routes.router)
router.include_router(inventory_routes.router)
router.include_router(suppliers_routes.router)
router.include_router(purchase_order_routes.router)
router.include_router(reports_routes.router)