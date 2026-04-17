from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SampleBase(BaseModel):
    user_id: int
    filename: str = Field(..., max_length=255)
    sample_type: str = Field(default="file", max_length=20)
    hash: str = Field(..., max_length=64)
    status: str = Field(default="pending", max_length=50)
    result: str | None = None
    result_json: dict[str, Any] | list[Any] | None = None
    task_id: str | None = Field(None, max_length=128)


class SampleCreate(SampleBase):
    pass


class SampleUpdate(BaseModel):
    user_id: int | None = None
    filename: str | None = Field(None, max_length=255)
    sample_type: str | None = Field(None, max_length=20)
    hash: str | None = Field(None, max_length=64)
    status: str | None = Field(None, max_length=50)
    result: str | None = None
    result_json: dict[str, Any] | list[Any] | None = None
    task_id: str | None = Field(None, max_length=128)


class SampleOut(SampleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
