from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password, get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    ProfileUpdateRequest,
    ProfileUpdateResponse,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)


router = APIRouter()


@router.post("/auth/register", response_model=UserPublic)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = (
        db.query(User)
        .filter((User.username == payload.username) | (User.email == payload.email))
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = User(username=payload.username, email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    token = create_access_token(subject=user.username)
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)):
    return user


@router.patch("/auth/me", response_model=ProfileUpdateResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码不正确")

    new_token: str | None = None
    username_clean = payload.username.strip()
    if not username_clean:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名不能为空")

    if username_clean != user.username:
        taken = db.query(User).filter(User.username == username_clean, User.id != user.id).first()
        if taken:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已被占用")
        user.username = username_clean
        new_token = create_access_token(subject=user.username)

    if str(payload.email) != user.email:
        taken = db.query(User).filter(User.email == str(payload.email), User.id != user.id).first()
        if taken:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被占用")
        user.email = str(payload.email)

    new_pw = (payload.new_password or "").strip()
    if new_pw:
        if len(new_pw) < 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="新密码至少 6 位")
        user.password_hash = hash_password(new_pw)

    db.commit()
    db.refresh(user)
    return ProfileUpdateResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        access_token=new_token,
    )

