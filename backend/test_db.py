import sys
from sqlalchemy import text
from database import engine

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"Successfully connected to Neon Database!")
            print(f"PostgreSQL Version: {version}")
            return True
    except Exception as e:
        print(f"Failed to connect to the database. Error: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = test_connection()
    if not success:
        sys.exit(1)
