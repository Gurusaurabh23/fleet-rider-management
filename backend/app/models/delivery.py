from app.db.base import Base
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    rider_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    external_order_id = Column(String)  # Uber Eats order id
    timestamp = Column(DateTime, default=datetime.utcnow)
    pay_per_delivery = Column(Integer, default=3)
