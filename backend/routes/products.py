from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from models.product import Product, Category
from schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    CategoryCreate, CategoryResponse
)
from auth.session_manager import get_current_user

router = APIRouter()

# Category Routes
@router.post("/categories", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_cat = Category(**category.model_dump())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Category).all()

# Product Routes
@router.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_prod = Product(**product.model_dump())
    db.add(db_prod)
    db.commit()
    db.refresh(db_prod)
    return db_prod

@router.get("/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Product).all()

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_prod = db.query(Product).filter(Product.id == product_id).first()
    if not db_prod:
        raise HTTPException(status_code=404, detail="Product not found")
        
    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(db_prod, key, value)
        
    db.commit()
    db.refresh(db_prod)
    return db_prod

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_prod = db.query(Product).filter(Product.id == product_id).first()
    if not db_prod:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_prod)
    db.commit()
    return {"success": True, "message": "Product deleted", "data": {}}
