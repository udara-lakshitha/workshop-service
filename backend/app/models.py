import datetime as dt
import enum
from typing import Optional
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
    role: Mapped[Role] = mapped_column(SQLEnum(Role, name="user_role"), nullable=False)

class Workshop(Base):
    __tablename__ = "workshops"
    __table_args__ = (CheckConstraint("capacity > 0", name="ck_workshop_capacity_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    instructor: Mapped[str] = mapped_column(String(100), nullable=False)
    date_time: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    capacity: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[WorkshopStatus] = mapped_column(
        SQLEnum(WorkshopStatus, name="workshop_status"),
        default=WorkshopStatus.SCHEDULED,
        nullable=False,
    )

    registrations: Mapped[list["Registration"]] = relationship(back_populates="workshop")

class Registration(Base):
    """Rows are never deleted. Cancelling only changes the status, so history is permanent."""

    __tablename__ = "registrations"
    __table_args__ = (
        Index(
            "uq_active_attendee_per_workshop",
            "workshop_id",
            "attendee_email",
            unique=True,
            postgresql_where=text("status = 'ACTIVE'"),
        ),
        Index("ix_registrations_workshop_status", "workshop_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    workshop_id: Mapped[int] = mapped_column(ForeignKey("workshops.id"), nullable=False)
    attendee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    attendee_email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[RegistrationStatus] = mapped_column(
        SQLEnum(RegistrationStatus, name="registration_status"),
        default=RegistrationStatus.ACTIVE,
        nullable=False,
    )

    registered_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    registered_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    cancelled_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    cancelled_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    workshop: Mapped["Workshop"] = relationship(back_populates="registrations")
    registered_by: Mapped["User"] = relationship(foreign_keys=[registered_by_id])
    cancelled_by: Mapped[Optional["User"]] = relationship(foreign_keys=[cancelled_by_id])
    