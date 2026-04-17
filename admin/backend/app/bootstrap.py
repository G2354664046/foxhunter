from sqlalchemy.orm import Session

from app.config import settings
from app.models.admin_user import AdminUser
from app.security import hash_password


def ensure_admin_table(engine, AdminUserModel):
    AdminUserModel.__table__.create(bind=engine, checkfirst=True)


def bootstrap_default_admin(db: Session) -> None:
    exists = db.query(AdminUser).first()
    if exists:
        return
    admin = AdminUser(
        username=settings.bootstrap_admin_username,
        password_hash=hash_password(settings.bootstrap_admin_password),
        nickname="系统管理员",
        status=True,
    )
    db.add(admin)
    db.commit()
