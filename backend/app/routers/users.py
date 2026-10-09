from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_password_hash, require_roles
from app.database import get_db
from app.models import Role, User
from app.schemas import RoleUpdate, UserCreate, UserOut

router = APIRouter(prefix="/api/users", tags=["Users"])

admin_only = require_roles([Role.ADMIN])

@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), admin: User = Depends(admin_only)):
    return db.scalars(select(User).order_by(User.username)).all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), admin: User = Depends(admin_only)):
    new_user = User(
        username=user_in.username,
        password=get_password_hash(user_in.password),
        role=user_in.role,
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
    db.refresh(new_user)
    return new_user

@router.patch("/{user_id}/role", response_model=UserOut)
def set_role(
    user_id: int,
    body: RoleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(admin_only),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    if user.id == admin.id and body.role != Role.ADMIN:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot remove your own admin access")
    user.role = body.role
    db.commit()
    db.refresh(user)
    return user