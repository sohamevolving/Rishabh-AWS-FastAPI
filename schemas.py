from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class ItemCreate(BaseModel):
    key: Optional[str] = None   # auto-generated UUID if omitted
    value: Any


class ItemUpdate(BaseModel):
    value: Any


class ItemResponse(BaseModel):
    key: str
    value: Any
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str