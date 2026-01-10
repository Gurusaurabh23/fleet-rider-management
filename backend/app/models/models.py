from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="rider")  # admin or rider
    created_at = Column(DateTime(timezone=True), server_default=func.now())
