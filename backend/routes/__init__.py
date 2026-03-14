from routes.products import router as products_router
from routes.warehouse import router as warehouse_router
from routes.inventory import router as inventory_router
from routes.ledger import router as ledger_router

__all__ = [
    "products_router",
    "warehouse_router",
    "inventory_router",
    "ledger_router"
]
