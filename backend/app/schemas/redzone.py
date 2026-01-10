from pydantic import BaseModel
from typing import Optional

class RedZoneBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    radius_meters: int
    is_active: Optional[bool] = True

class RedZoneCreate(RedZoneBase):
    pass

class RedZoneRead(RedZoneBase):
    id: int

    class Config:
        from_attributes = True
