import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_PLACEHOLDER_API_KEYS = frozenset(
    {
        "",
        "yourkey",
        "your_urlhaus_key",
        "your_virustotal_key",
        "changeme",
        "xxx",
    }
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    # SQLAlchemy URL. Example (PyMySQL, recommended on Windows):
    # mysql+pymysql://user:password@localhost:3306/foxhunter?charset=utf8mb4
    mysql_url: str = os.getenv(
        "MYSQL_URL",
        "mysql+pymysql://root:123456cxn@localhost:3306/foxhunter?charset=utf8mb4",
    )

    # Redis / Celery：须由 Field + .env 注入；勿用类体里的 os.getenv，否则易与 pydantic-settings 的 .env 加载顺序不一致。
    # 仅密码时格式为 redis://:密码@host:6379/0（密码前必须有冒号）；错误写成 redis://密码@host 会把密码当成用户名。
    redis_url: str = Field(default="redis://localhost:6379/0")
    celery_broker_url: str = Field(default="redis://localhost:6379/0")
    celery_result_backend: str = Field(default="redis://localhost:6379/0")

    # App
    app_name: str = "FoxHunter"
    debug: bool = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "y", "on"}

    # Security (JWT)
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Uploads
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")

    # 必须由 pydantic 从 .env 读取；os.getenv 在类定义阶段执行，读不到 .env
    urlhaus_api_key: str | None = Field(default=None)
    virustotal_api_key: str | None = Field(default=None)

    @field_validator("urlhaus_api_key", "virustotal_api_key", mode="before")
    @classmethod
    def _normalize_optional_api_key(cls, v: object) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str):
            return None
        s = v.strip()
        if not s or s.lower() in _PLACEHOLDER_API_KEYS:
            return None
        return s


settings = Settings()
