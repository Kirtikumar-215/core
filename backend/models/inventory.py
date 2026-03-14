from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.session import Base
import enum

class OperationStatus(str, enum.Enum):
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    CANCELLED = "CANCELLED"

class Stock(Base):
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    quantity = Column(Float, default=0.0, nullable=False)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    product = relationship("Product", back_populates="stocks")
    location = relationship("Location", back_populates="stocks")

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, index=True, nullable=False)
    supplier_name = Column(String, nullable=True)
    status = Column(String, default=OperationStatus.PENDING.value)
    destination_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    validated_at = Column(DateTime(timezone=True), nullable=True)

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, index=True, nullable=False)
    customer_name = Column(String, nullable=True)
    status = Column(String, default=OperationStatus.PENDING.value)
    source_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    validated_at = Column(DateTime(timezone=True), nullable=True)

class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default=OperationStatus.PENDING.value)
    source_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    destination_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    validated_at = Column(DateTime(timezone=True), nullable=True)

class Adjustment(Base):
    __tablename__ = "adjustments"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default=OperationStatus.PENDING.value)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    validated_at = Column(DateTime(timezone=True), nullable=True)

# Central Stock Ledger Model
class StockMove(Base):
    __tablename__ = "stock_moves"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    operation_type = Column(String, nullable=False) # RECEIPT, DELIVERY, TRANSFER, ADJUSTMENT
    reference_id = Column(Integer, nullable=False) # ID of the Receipt/Delivery/etc
    quantity = Column(Float, nullable=False)
    source_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    destination_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    product = relationship("Product", back_populates="stock_moves")
