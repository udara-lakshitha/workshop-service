from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from app.models import Role, WorkshopStatus, RegistrationStatus

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: Role

class UserOut(BaseModel):
    id: int
    username: str
    role: Role
    class Config:
        from_attributes = True

class WorkshopCreate(BaseModel):
    code: str
    title: str
    instructor: str
    date_time: datetime
    capacity: int

class WorkshopOut(BaseModel):
    id: int
    code: str
    title: str
    instructor: str
    date_time: datetime
    capacity: int
    status: WorkshopStatus
    active_registrations_count: Optional[int] = 0
    class Config:
        from_attributes = True

class RegistrationCreate(BaseModel):
    workshop_id: int
    attendee_name: str
    attendee_email: EmailStr

class RegistrationOut(BaseModel):
    id: int
    workshop_id: int
    attendee_name: str
    attendee_email: str
    status: RegistrationStatus
    registered_at: datetime
    registered_by_id: int
    cancelled_at: Optional[datetime] = None
    cancelled_by_id: Optional[int] = None
    class Config:
        from_attributes = True