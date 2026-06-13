from sqlalchemy import Column, Integer, String, Boolean, Sequence  # 1. Import Sequence
from app.database.duckdb_database import Base
from pydantic import BaseModel


class User(Base):
    __tablename__ = "users"

    # Add an explicit sequence mapping for DuckDB to auto-increment rows safely.
    id = Column(Integer, Sequence("user_id_seq"), primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)


class UserCreate(BaseModel):
    username: str
    password: str
    email: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_verified: bool

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models
