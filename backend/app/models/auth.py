from app.db.base import Base
from sqlalchemy import Column, String, DateTime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.schemas.user import UserCreate, UserRead


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="rider")  # rider or admin
    created_at = Column(DateTime, default=datetime.utcnow)
