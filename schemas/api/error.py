from datetime import datetime

from fastapi import status
from pydantic import BaseModel, Field

from utils import timezone


class FieldError(BaseModel):
    field: str
    messages: list[str]


class ErrorResponse(BaseModel):
    status_code: int = status.HTTP_400_BAD_REQUEST
    error_code: str = 'invalid'
    message: str = 'Bad Request'
    details: list[FieldError] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=timezone.now)
