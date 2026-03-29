from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID

from core_api.api.dependencies import current_user_id
from core_api.core.db import get_session
from core_api.core.security import verify_password, create_access_token
from core_api.schemas.auth import LoginRequest, TokenOut
from core_api.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut, status_code=status.HTTP_200_OK)
def login(body: LoginRequest, db: Session = Depends(get_session)):
    user: User | None = (
        db.query(User)
        .filter(func.lower(User.email) == func.lower(body.email))
        .one_or_none()
    )
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )

    token = create_access_token(sub=str(user.id))
    return TokenOut(access_token=token)


@router.get("/me", status_code=status.HTTP_200_OK)
def me(user_id: UUID = Depends(current_user_id), db: Session = Depends(get_session)):
    user: User | None = db.query(User).filter(User.id == user_id).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )
    return {"user_id": str(user.id), "email": user.email}
