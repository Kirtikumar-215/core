from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from database.session import get_db
from models.inventory import Stock, Receipt, Delivery, Transfer, Adjustment, StockMove, OperationStatus
from models.product import Product
from models.warehouse import Location
from schemas.inventory import (
    ReceiptCreate, DeliveryCreate, TransferCreate, 
    AdjustmentCreate
)
from auth.session_manager import get_current_user

router = APIRouter()

def get_or_create_stock(db: Session, product_id: int, location_id: int) -> Stock:
    stock = db.query(Stock).filter(
        Stock.product_id == product_id,
        Stock.location_id == location_id
    ).first()
    
    if not stock:
        # Verify product and location exist
        if not db.query(Product).filter(Product.id == product_id).first():
            raise HTTPException(status_code=404, detail="Product not found")
        if not db.query(Location).filter(Location.id == location_id).first():
            raise HTTPException(status_code=404, detail="Location not found")
            
        stock = Stock(product_id=product_id, location_id=location_id, quantity=0)
        db.add(stock)
        db.flush() # Get ID without committing
    
    return stock

def create_stock_move(db: Session, product_id: int, operation_type: str, reference_id: int, 
                      quantity: float, source_id: int, dest_id: int, user_id: int):
    move = StockMove(
        product_id=product_id,
        operation_type=operation_type,
        reference_id=reference_id,
        quantity=quantity,
        source_location_id=source_id,
        destination_location_id=dest_id,
        user_id=user_id
    )
    db.add(move)

@router.post("/receipts")
def create_receipt(receipt: ReceiptCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Create Receipt Record
    db_receipt = Receipt(
        reference=receipt.reference,
        supplier_name=receipt.supplier_name,
        destination_location_id=receipt.destination_location_id,
        created_by_id=current_user.id,
        status=OperationStatus.VALIDATED.value, # Auto-validated based on requirement "Validation must increase stock"
        validated_at=datetime.utcnow()
    )
    db.add(db_receipt)
    db.flush()
    
    # Update Stock
    stock = get_or_create_stock(db, receipt.product_id, receipt.destination_location_id)
    stock.quantity += receipt.quantity
    
    # Create Ledger Entry
    create_stock_move(
        db=db, product_id=receipt.product_id, operation_type="RECEIPT",
        reference_id=db_receipt.id, quantity=receipt.quantity,
        source_id=None, dest_id=receipt.destination_location_id, user_id=current_user.id
    )
    
    db.commit()
    return {"success": True, "message": "Receipt created and stock updated", "data": {"id": db_receipt.id}}

@router.post("/deliveries")
def create_delivery(delivery: DeliveryCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Check Stock
    stock = get_or_create_stock(db, delivery.product_id, delivery.source_location_id)
    if stock.quantity < delivery.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock in the source location")
        
    # Create Delivery Record
    db_delivery = Delivery(
        reference=delivery.reference,
        customer_name=delivery.customer_name,
        source_location_id=delivery.source_location_id,
        created_by_id=current_user.id,
        status=OperationStatus.VALIDATED.value,
        validated_at=datetime.utcnow()
    )
    db.add(db_delivery)
    db.flush()
    
    # Update Stock
    stock.quantity -= delivery.quantity
    
    # Create Ledger Entry
    create_stock_move(
        db=db, product_id=delivery.product_id, operation_type="DELIVERY",
        reference_id=db_delivery.id, quantity=delivery.quantity,
        source_id=delivery.source_location_id, dest_id=None, user_id=current_user.id
    )
    
    db.commit()
    return {"success": True, "message": "Delivery created and stock updated", "data": {"id": db_delivery.id}}

@router.post("/transfers")
def create_transfer(transfer: TransferCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if transfer.source_location_id == transfer.destination_location_id:
        raise HTTPException(status_code=400, detail="Source and destination locations cannot be the same")
        
    source_stock = get_or_create_stock(db, transfer.product_id, transfer.source_location_id)
    if source_stock.quantity < transfer.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock in the source location")
        
    dest_stock = get_or_create_stock(db, transfer.product_id, transfer.destination_location_id)
    
    # Create Transfer Record
    db_transfer = Transfer(
        reference=transfer.reference,
        source_location_id=transfer.source_location_id,
        destination_location_id=transfer.destination_location_id,
        created_by_id=current_user.id,
        status=OperationStatus.VALIDATED.value,
        validated_at=datetime.utcnow()
    )
    db.add(db_transfer)
    db.flush()
    
    # Update Stock
    source_stock.quantity -= transfer.quantity
    dest_stock.quantity += transfer.quantity
    
    # Create Ledger Entry
    create_stock_move(
        db=db, product_id=transfer.product_id, operation_type="TRANSFER",
        reference_id=db_transfer.id, quantity=transfer.quantity,
        source_id=transfer.source_location_id, dest_id=transfer.destination_location_id, user_id=current_user.id
    )
    
    db.commit()
    return {"success": True, "message": "Stock transferred successfully", "data": {"id": db_transfer.id}}

@router.post("/adjustments")
def create_adjustment(adjustment: AdjustmentCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    stock = get_or_create_stock(db, adjustment.product_id, adjustment.location_id)
    
    difference = adjustment.counted_quantity - stock.quantity
    
    # Create Adjustment Record
    db_adjustment = Adjustment(
        reference=adjustment.reference,
        location_id=adjustment.location_id,
        created_by_id=current_user.id,
        status=OperationStatus.VALIDATED.value,
        validated_at=datetime.utcnow()
    )
    db.add(db_adjustment)
    db.flush()
    
    # Create Ledger Entry (only if there is a difference)
    if difference != 0:
        create_stock_move(
            db=db, product_id=adjustment.product_id, operation_type="ADJUSTMENT",
            reference_id=db_adjustment.id, quantity=difference,
            source_id=adjustment.location_id if difference < 0 else None,
            dest_id=adjustment.location_id if difference > 0 else None,
            user_id=current_user.id
        )
        
    # Update Stock
    stock.quantity = adjustment.counted_quantity
    
    db.commit()
    return {"success": True, "message": "Stock adjusted successfully", "data": {"id": db_adjustment.id, "difference": difference}}
