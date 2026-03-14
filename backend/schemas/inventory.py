from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from schemas.product import ProductResponse
from schemas.user import UserResponse

class StockBase(BaseModel):
    product_id: int
    location_id: int
    quantity: float

class StockResponse(StockBase):
    id: int
    last_updated: datetime
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True

class ReceiptCreate(BaseModel):
    reference: str
    supplier_name: Optional[str] = None
    destination_location_id: int
    product_id: int
    quantity: float

class DeliveryCreate(BaseModel):
    reference: str
    customer_name: Optional[str] = None
    source_location_id: int
    product_id: int
    quantity: float

class TransferCreate(BaseModel):
    reference: str
    source_location_id: int
    destination_location_id: int
    product_id: int
    quantity: float

class AdjustmentCreate(BaseModel):
    reference: str
    location_id: int
    product_id: int
    counted_quantity: float

class StockMoveResponse(BaseModel):
    id: int
    timestamp: datetime
    product_id: int
    operation_type: str
    reference_id: int
    quantity: float
    source_location_id: Optional[int]
    destination_location_id: Optional[int]
    user_id: int
    
    class Config:
        from_attributes = True
