from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from models.inventory import Stock, StockMove
from schemas.inventory import StockResponse, StockMoveResponse
from auth.session_manager import get_current_user

router = APIRouter()

@router.get("/stock", response_model=List[StockResponse])
def get_current_stock(product_id: int = None, location_id: int = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    query = db.query(Stock)
    if product_id:
        query = query.filter(Stock.product_id == product_id)
    if location_id:
        query = query.filter(Stock.location_id == location_id)
    return query.all()

@router.get("/stock/ledger", response_model=List[StockMoveResponse])
def get_stock_ledger(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Returns all stock moves ordered by newest first
    return db.query(StockMove).order_by(StockMove.timestamp.desc()).all()
