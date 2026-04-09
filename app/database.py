from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# MySQL
engine = create_engine(settings.mysql_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Ensure models are imported so SQLAlchemy can create tables.
    from app.models import user as _user  # noqa: F401
    from app.models import sample as _sample  # noqa: F401
    from app.models import cnn_detection_result as _cnn_detection_result  # noqa: F401
    Base.metadata.create_all(bind=engine)