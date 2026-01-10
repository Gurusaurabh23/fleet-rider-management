from app.db.base import Base
from sqlalchemy import Column, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime

class LocationLog(Base):
    __tablename__ = "location_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    rider_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float)
    longitude = Column(Float)
