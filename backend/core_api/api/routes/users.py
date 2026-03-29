from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from core_api.core.db import get_session
from core_api.api.dependencies import current_user_id
from core_api.core.security import hash_password
from core_api.models.user import User
from core_api.schemas.user import UserCreate, UserUpdate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


# HELPERS
def _get_user(user_id: UUID, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


# CREATE
@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    response: Response,
    db: Session = Depends(get_session),
):
    existing = (
        db.query(User.id).filter(func.lower(User.email) == payload.email).one_or_none()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password.get_secret_value()),
    )

    db.add(user)
    db.flush()
    db.refresh(user)

    response.headers["Location"] = "/users/me"

    return user


# READ
@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
def read_me(
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    return _get_user(user_id, db)


# UPDATE
@router.patch("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
def update_me(
    payload: UserUpdate,
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    user = _get_user(user_id, db)

    data = payload.model_dump(exclude_unset=True, exclude={"password"})
    if not data and payload.password is None:
        return user

    if "email" in data:
        new_email = data["email"]
        existing = (
            db.query(User.id)
            .filter(
                func.lower(User.email) == new_email,
                User.id != user_id,
            )
            .one_or_none()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        user.email = new_email

    if payload.password is not None:
        user.password_hash = hash_password(payload.password.get_secret_value())

    db.flush()
    db.refresh(user)

    return user


# DELETE
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    user_id: UUID = Depends(current_user_id),
    db: Session = Depends(get_session),
):
    user = _get_user(user_id, db)

    db.delete(user)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
