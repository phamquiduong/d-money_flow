from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class TokenType(StrEnum):
    ACCESS = 'access'
    REFRESH = 'refresh'


class TokenPayload(BaseModel):
    sub: str
    type: TokenType


class Token(BaseModel):
    token: str
    expired: datetime | None


class TokenResponse(BaseModel):
    access: Token
    refresh: Token
