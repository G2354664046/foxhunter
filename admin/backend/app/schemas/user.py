from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=6)


class UserOut(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
