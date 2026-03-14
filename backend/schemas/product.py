from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    sku_code: str
    category_id: Optional[int] = None
    unit_of_measure: str
    initial_stock: float = 0.0

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku_code: Optional[str] = None
    category_id: Optional[int] = None
    unit_of_measure: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Location Schemas
class LocationBase(BaseModel):
    name: str
    warehouse_id: int
    is_active: bool = True

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Warehouse Schemas
class WarehouseBase(BaseModel):
    name: str
    address: Optional[str] = None
    is_active: bool = True

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseResponse(WarehouseBase):
    id: int
    created_at: datetime
    locations: List[LocationResponse] = []
    
    class Config:
        from_attributes = True
