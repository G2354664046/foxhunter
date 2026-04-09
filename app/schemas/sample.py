from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class SampleResponse(BaseModel):
    id: int
    filename: str
    sample_type: str = "file"
    status: str
    result: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

