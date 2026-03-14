from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from models.warehouse import Warehouse, Location
from schemas.product import (
    WarehouseCreate, WarehouseResponse,
    LocationCreate, LocationResponse
)
from auth.session_manager import get_current_user

router = APIRouter()

@router.post("/warehouses", response_model=WarehouseResponse)
def create_warehouse(warehouse: WarehouseCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_wh = Warehouse(**warehouse.model_dump())
    db.add(db_wh)
    db.commit()
    db.refresh(db_wh)
    return db_wh

@router.get("/warehouses", response_model=List[WarehouseResponse])
def get_warehouses(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Warehouse).all()

@router.post("/locations", response_model=LocationResponse)
def create_location(location: LocationCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_loc = Location(**location.model_dump())
    db.add(db_loc)
    db.commit()
    db.refresh(db_loc)
    return db_loc

@router.get("/locations", response_model=List[LocationResponse])
def get_locations(warehouse_id: int = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    query = db.query(Location)
    if warehouse_id:
        query = query.filter(Location.warehouse_id == warehouse_id)
    return query.all()
