from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    login_id: str

class UserCreate(UserBase):
    password: str
    role: str
    job_type: str
    hourly_rate: Optional[float] = None  # add here

class UserRead(UserBase):
    id: int
    role: str
    job_type: str
    is_active: bool
    hourly_rate: Optional[float] = None  # <-- THIS FIX

    class Config:
        from_attributes = True
