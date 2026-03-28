from __future__ import annotations
import uuid

from pydantic import BaseModel, Field, field_validator, SecretStr, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=254, description="User's email")

    @field_validator("email")
    @classmethod
    def _normalize(cls, v: EmailStr) -> str:
        return str(v).strip().lower()


class UserCreate(UserBase):
    password: SecretStr = Field(..., max_length=255, description="User's password")


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(None, max_length=254)
    password: SecretStr | None = Field(None, max_length=255)

    @field_validator("email")
    @classmethod
    def _normalize(cls, v: EmailStr | None) -> str | None:
        if v is None:
            return None
        return str(v).strip().lower()


class UserOut(UserBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
