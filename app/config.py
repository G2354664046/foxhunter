import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    # SQLAlchemy URL. Example (PyMySQL, recommended on Windows):
    # mysql+pymysql://user:password@localhost:3306/foxhunter?charset=utf8mb4
    mysql_url: str = os.getenv(
        "MYSQL_URL",
        "mysql+pymysql://root:123456@cxn@localhost:3306/foxhunter?charset=utf8mb4",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Celery
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # App
    app_name: str = "FoxHunter"
    debug: bool = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "y", "on"}

    # Security (JWT)
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Uploads
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    # External services
    urlhaus_api_key: str | None = os.getenv("URLHAUS_API_KEY")
    virustotal_api_key: str | None = os.getenv("VIRUSTOTAL_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()