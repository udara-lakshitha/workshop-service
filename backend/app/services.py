import datetime as dt

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Registration, RegistrationStatus, Workshop

def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)

def lock_workshop(db: Session, workshop_id: int) -> Workshop:
    workshop = db.scalar(
        select(Workshop)
        .where(Workshop.id == workshop_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if workshop is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Workshop not found")
    return workshop

def count_active(db: Session, workshop_id: int) -> int:
    return (
        db.scalar(
            select(func.count())
            .select_from(Registration)
            .where(
                Registration.workshop_id == workshop_id,
                Registration.status == RegistrationStatus.ACTIVE,
            )
        )or 0)