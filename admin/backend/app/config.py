from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 与 FoxHunter 主库相同，仅通过连接串访问，不 import 主项目代码
    database_url: str = "mysql+pymysql://root:123456cxn@127.0.0.1:3306/foxhunter?charset=utf8mb4"

    jwt_secret_key: str = "admin-jwt-change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 720

    # 探测主系统是否可用（HTTP，非 Python 引用）
    foxhunter_api_base: str = "http://127.0.0.1:8000"

    # 首次无管理员时自动创建（生产环境请改密）
    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: str = "admin123"


settings = Settings()
