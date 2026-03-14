import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("'") and DATABASE_URL.endswith("'"):
    DATABASE_URL = DATABASE_URL[1:-1]

# Engine creation with connection pooling for Neon PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True, # Verify connection on checkout
    pool_size=10,       # Number of connections to keep open
    max_overflow=20     # Max number of connections above pool_size
)
