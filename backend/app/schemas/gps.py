from pydantic import BaseModel

class GPSCreate(BaseModel):
    latitude: float
    longitude: float

class GPSRead(BaseModel):
    id: int
    rider_id: int
    latitude: float
    longitude: float

    class Config:
        from_attributes = True
