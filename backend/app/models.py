import enum
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime, Enum as SQLEnum
import datetime as dt

from app.database import Base

class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    STAFF = "STAFF"

class WorkshopStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class RegistrationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(SQLEnum(Role), nullable=False)

class Workshop(Base):
    __tablename__ = "workshops"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    instructor: Mapped[str] = mapped_column(String(100), nullable=False)
    date_time: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)
    capacity: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[WorkshopStatus] = mapped_column(SQLEnum(WorkshopStatus), default=WorkshopStatus.SCHEDULED)

    registrations = relationship("Registration", back_populates="workshop")

class Registration(Base):
    __tablename__ = "registrations"

    id: Mapped[int] = mapped_column(primary_key=True)
    workshop_id: Mapped[int] = mapped_column(ForeignKey("workshops.id"), nullable=False)
    attendee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    attendee_email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[RegistrationStatus] = mapped_column(SQLEnum(RegistrationStatus), default=RegistrationStatus.ACTIVE)

    registered_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    registered_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    
    cancelled_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    cancelled_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime, nullable=True)

    workshop = relationship("Workshop", back_populates="registrations")
    registered_by = relationship("User", foreign_keys=[registered_by_id])
    cancelled_by = relationship("User", foreign_keys=[cancelled_by_id])