import datetime as dt
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.auth import require_roles
from app.database import get_db
from app.models import Registration, RegistrationStatus, Role, User, Workshop, WorkshopStatus
from app.schemas import RegistrationCreate, RegistrationOut

from app.services import lock_workshop, now_utc

router = APIRouter(prefix="/api", tags=["Registrations"])

front_desk = require_roles([Role.MANAGER, Role.STAFF])

def load_registration(db: Session, registration_id: int) -> Registration:
    return db.scalar(
        select(Registration)
        .where(Registration.id == registration_id)
        .options(selectinload(Registration.registered_by), selectinload(Registration.cancelled_by))
        .execution_options(populate_existing=True)
    )

@router.post("/registrations", response_model=RegistrationOut, status_code=status.HTTP_201_CREATED)
def register_attendee(
    reg_in: RegistrationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(front_desk),
):
    workshop = lock_workshop(db, reg_in.workshop_id)

    if workshop.status != WorkshopStatus.SCHEDULED:
        raise HTTPException(status.HTTP_409_CONFLICT, "This workshop is not open for registration")

    starts_at = workshop.date_time
    if starts_at.tzinfo is None:  # a column without timezone returns naive datetimes
        starts_at = starts_at.replace(tzinfo=dt.timezone.utc)
    if starts_at <= now_utc():
        raise HTTPException(status.HTTP_409_CONFLICT, "This workshop has already started")

    email = reg_in.attendee_email.lower()

    already = db.scalar(
        select(Registration.id).where(
            Registration.workshop_id == workshop.id,
            Registration.attendee_email == email,
            Registration.status == RegistrationStatus.ACTIVE,
        )
    )
    if already:
        raise HTTPException(status.HTTP_409_CONFLICT, "This attendee is already registered for this workshop")

    active_count = db.scalar(
        select(func.count())
        .select_from(Registration)
        .where(
            Registration.workshop_id == workshop.id,
            Registration.status == RegistrationStatus.ACTIVE,
        )
    )
    if active_count >= workshop.capacity:
        raise HTTPException(status.HTTP_409_CONFLICT, "Workshop capacity reached. Cannot register.")

    registration = Registration(
        workshop_id=workshop.id,
        attendee_name=reg_in.attendee_name,
        attendee_email=email,
        status=RegistrationStatus.ACTIVE,
        registered_by_id=user.id,
        registered_at=now_utc(),
    )
    db.add(registration)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "This attendee is already registered for this workshop")
    return load_registration(db, registration.id)


@router.post("/registrations/{reg_id}/cancel", response_model=RegistrationOut)
def cancel_registration(
    reg_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(front_desk),
):
    registration = db.get(Registration, reg_id)
    if registration is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Registration not found")

    lock_workshop(db, registration.workshop_id)
    db.refresh(registration)

    if registration.status == RegistrationStatus.CANCELLED:
        raise HTTPException(status.HTTP_409_CONFLICT, "Registration is already cancelled")

    registration.status = RegistrationStatus.CANCELLED
    registration.cancelled_by_id = user.id
    registration.cancelled_at = now_utc()
    db.commit()
    return load_registration(db, reg_id)


@router.get("/workshops/{ws_id}/registrations", response_model=List[RegistrationOut])
def get_workshop_registrations(
    ws_id: int,
    status_filter: Optional[RegistrationStatus] = None,
    db: Session = Depends(get_db),
    user: User = Depends(front_desk),
):
    if db.get(Workshop, ws_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Workshop not found")
    query = (
        select(Registration)
        .where(Registration.workshop_id == ws_id)
        .options(selectinload(Registration.registered_by), selectinload(Registration.cancelled_by))
        .order_by(Registration.registered_at, Registration.id)
    )
    if status_filter:
        query = query.where(Registration.status == status_filter)
    return db.scalars(query).all()