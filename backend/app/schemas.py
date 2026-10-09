import datetime as dt
from typing import Annotated, Optional

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    computed_field,
)

from app.models import RegistrationStatus, Role, WorkshopStatus

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserCreate(BaseModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=100)]
    password: str = Field(min_length=8, max_length=72)
    role: Role

class RoleUpdate(BaseModel):
    role: Role
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: Role

Text255 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]

class WorkshopCreate(BaseModel):
    code: Annotated[str, StringConstraints(strip_whitespace=True, to_upper=True, min_length=2, max_length=100)]
    title: Text255
    instructor: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    date_time: AwareDatetime
    capacity: int = Field(ge=1, le=1000)

class WorkshopUpdate(BaseModel):
    """All fields optional: a manager can change just one thing."""

    title: Optional[Text255] = None
    instructor: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]] = None
    date_time: Optional[AwareDatetime] = None
    capacity: Optional[int] = Field(default=None, ge=1, le=1000)
    status: Optional[WorkshopStatus] = None

class WorkshopOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    title: str
    instructor: str
    date_time: dt.datetime
    capacity: int
    status: WorkshopStatus
    active_registrations_count: int = 0

    @computed_field
    @property
    def seats_left(self) -> int:
        return max(self.capacity - self.active_registrations_count, 0)

class RegistrationCreate(BaseModel):
    workshop_id: int = Field(gt=0)
    attendee_name: Text255
    attendee_email: EmailStr
class RegistrationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workshop_id: int
    attendee_name: str
    attendee_email: str
    status: RegistrationStatus
    registered_at: dt.datetime
    registered_by_id: int
    registered_by: UserOut
    cancelled_at: Optional[dt.datetime] = None
    cancelled_by_id: Optional[int] = None
    cancelled_by: Optional[UserOut] = None