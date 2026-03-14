import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.session import engine, Base, SessionLocal
from models.user import User
from auth.password_service import get_password_hash

# Import routers
from auth.auth_routes import router as auth_router
from routes.products import router as products_router
from routes.warehouse import router as warehouse_router
from routes.inventory import router as inventory_router
from routes.ledger import router as ledger_router

# Ensure tables are created
Base.metadata.create_all(bind=engine)

def create_admin_user():
    db = SessionLocal()
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@coreinventory.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "securepassword")
        
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            print(f"Bootstrapping default Admin User: {admin_email}")
            user = User(
                name="System Admin",
                email=admin_email,
                role="Admin",
                hashed_password=get_password_hash(admin_password)
            )
            db.add(user)
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create admin user if it doesn't exist
    create_admin_user()
    yield
    # Shutdown logic (if any)
    pass

app = FastAPI(title="CoreInventory API", lifespan=lifespan)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include modules
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(products_router, prefix="/api", tags=["Product Management"])
app.include_router(warehouse_router, prefix="/api", tags=["Warehouse & Locations"])
app.include_router(inventory_router, prefix="/api", tags=["Inventory Operations"])
app.include_router(ledger_router, prefix="/api", tags=["Stock Ledger"])

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
