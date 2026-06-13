from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Update the database URL to point to a local persistent DuckDB file.
# Format: "duckdb:///filename.duckdb"
SQLALCHEMY_DATABASE_URL = "duckdb:///./app.duckdb"

# Initialize the engine.
# DuckDB-engine automatically handles thread pooling and configurations.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Keep standard SQLAlchemy session handling intact
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get the database session in your routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
