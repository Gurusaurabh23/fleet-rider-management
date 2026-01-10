from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ShiftBase(BaseModel):
    start_time: datetime
    end_time: datetime | None = None


class ShiftCreate(BaseModel):
    rider_id: int
    start_time: datetime
    end_time: datetime | None = None


class ShiftRead(BaseModel):
    id: int
    rider_id: Optional[int]
    start_time: datetime
    end_time: datetime | None = None
    status: str
    hours_worked: float | None = None
    hourly_rate: float | None = None
    payout: float | None = None

    class Config:
        from_attributes = True

