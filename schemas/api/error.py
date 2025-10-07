from datetime import datetime

from fastapi import status
from pydantic import BaseModel, Field

from utils import timezone


class FieldError(BaseModel):
    field: str
    messages: list[str]


class ErrorResponse(BaseModel):
    status_code: int
    message: str
    details: list[FieldError] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=timezone.now)

    def model_dump(self, *args, **kwargs):
        kwargs.setdefault('mode', 'json')
        return super().model_dump(*args, **kwargs)
