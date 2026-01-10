from sqlalchemy import Column, Integer, DateTime, Float, func, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class MovementNotification(Base):
    __tablename__ = "movement_notifications"

    id = Column(Integer, primary_key=True)
    rider_id = Column(Integer, ForeignKey("users.id"))
    last_lat = Column(Float, nullable=False)
    last_lng = Column(Float, nullable=False)
    minutes_stopped = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    rider = relationship("User")
