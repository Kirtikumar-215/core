from database.session import Base
from models.user import User, Session, OTPRequest
from models.product import Product, Category
from models.warehouse import Warehouse, Location
from models.inventory import Stock, Receipt, Delivery, Transfer, Adjustment, StockMove

# Ensures all models are imported so SQLAlchemy knows about them for Base.metadata.create_all()
__all__ = [
    "Base", "User", "Session", "OTPRequest",
    "Product", "Category", 
    "Warehouse", "Location", 
    "Stock", "Receipt", "Delivery", "Transfer", "Adjustment", "StockMove"
]
