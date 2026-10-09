import datetime as dt
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import require_roles
from app.database import get_db
from app.models import Registration, RegistrationStatus, Role, User, Workshop, WorkshopStatus
from app.schemas import WorkshopCreate, WorkshopOut, WorkshopUpdate
from app.services import count_active, lock_workshop, now_utc

router = APIRouter(prefix="/api/workshops", tags=["Workshops"])

viewers = require_roles([Role.MANAGER, Role.STAFF])
managers_only = require_roles([Role.MANAGER])

def to_out(workshop: Workshop, active: int) -> WorkshopOut:
    return WorkshopOut.model_validate(workshop).model_copy(update={"active_registrations_count": active})

def day_start(day: dt.date) -> dt.datetime:
    return dt.datetime.combine(day, dt.time.min, tzinfo=dt.timezone.utc)

@router.get("", response_model=List[WorkshopOut])
def list_workshops(
    workshop_status: Optional[WorkshopStatus] = Query(default=None, alias="status"),
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    only_available: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(viewers),
):
    counts = (
        select(Registration.workshop_id.label("workshop_id"), func.count().label("n"))
        .where(Registration.status == RegistrationStatus.ACTIVE)
        .group_by(Registration.workshop_id)
        .subquery()
    )
    active = func.coalesce(counts.c.n, 0)
    query = select(Workshop, active.label("active")).outerjoin(counts, counts.c.workshop_id == Workshop.id)

    if workshop_status:
        query = query.where(Workshop.status == workshop_status)
    if start_date:
        query = query.where(Workshop.date_time >= day_start(start_date))
    if end_date:
        query = query.where(Workshop.date_time < day_start(end_date + dt.timedelta(days=1)))
    if only_available:
        query = query.where(Workshop.status == WorkshopStatus.SCHEDULED, Workshop.capacity - active > 0)

    rows = db.execute(query.order_by(Workshop.date_time, Workshop.id)).all()
    return [to_out(workshop, n) for workshop, n in rows]

@router.get("/{ws_id}", response_model=WorkshopOut)
def get_workshop(ws_id: int, db: Session = Depends(get_db), user: User = Depends(viewers)):
    workshop = db.get(Workshop, ws_id)
    if workshop is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Workshop not found")
    return to_out(workshop, count_active(db, ws_id))


@router.post("", response_model=WorkshopOut, status_code=status.HTTP_201_CREATED)
def create_workshop(
    ws_in: WorkshopCreate,
    db: Session = Depends(get_db),
    manager: User = Depends(managers_only),
):
    if ws_in.date_time <= now_utc():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A new workshop must start in the future")

    workshop = Workshop(**ws_in.model_dump())
    db.add(workshop)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, f"Workshop code {ws_in.code} already exists")
    db.refresh(workshop)
    return to_out(workshop, 0)

@router.patch("/{ws_id}", response_model=WorkshopOut)
def update_workshop(
    ws_id: int,
    ws_in: WorkshopUpdate,
    db: Session = Depends(get_db),
    manager: User = Depends(managers_only),
):
    workshop = lock_workshop(db, ws_id)
    changes = ws_in.model_dump(exclude_unset=True, exclude_none=True)

    active = count_active(db, ws_id)
    if "capacity" in changes and changes["capacity"] < active:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Capacity cannot be lower than the {active} attendees already registered",
        )

    for field, value in changes.items():
        setattr(workshop, field, value)
    db.commit()
    db.refresh(workshop)
    return to_out(workshop, active)