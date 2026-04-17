from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class CnnDetectionResult(Base):
    __tablename__ = "cnn_detection_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sample_id = Column(Integer, ForeignKey("samples.id", ondelete="CASCADE"), nullable=False, index=True)
    image_name = Column(String(255), nullable=False)
    image_path = Column(String(512), nullable=False)
    predicted_index = Column(Integer, nullable=False)
    predicted_label = Column(String(64), nullable=False)
    probability = Column(Float, nullable=False)
    is_malware = Column(Boolean, nullable=False, default=True)
    weights_path = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
