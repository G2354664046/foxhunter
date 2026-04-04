from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    username: str
    email: EmailStr
    current_password: str
    new_password: str | None = None


class ProfileUpdateResponse(UserPublic):
    access_token: str | None = None

