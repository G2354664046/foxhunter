from datetime import datetime

from pydantic import BaseModel, Field


class CnnResultBase(BaseModel):
    sample_id: int
    image_name: str = Field(..., max_length=255)
    image_path: str = Field(..., max_length=512)
    predicted_index: int
    predicted_label: str = Field(..., max_length=64)
    probability: float = Field(..., ge=0, le=1)
    is_malware: bool = True
    weights_path: str | None = Field(None, max_length=512)


class CnnResultCreate(CnnResultBase):
    pass


class CnnResultUpdate(BaseModel):
    sample_id: int | None = None
    image_name: str | None = Field(None, max_length=255)
    image_path: str | None = Field(None, max_length=512)
    predicted_index: int | None = None
    predicted_label: str | None = Field(None, max_length=64)
    probability: float | None = Field(None, ge=0, le=1)
    is_malware: bool | None = None
    weights_path: str | None = Field(None, max_length=512)


class CnnResultOut(CnnResultBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
