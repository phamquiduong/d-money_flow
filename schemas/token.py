from datetime import datetime
from enum import StrEnum

from pydantic import UUID4, BaseModel


class TokenType(StrEnum):
    ACCESS = 'access'
    REFRESH = 'refresh'


class TokenPayload(BaseModel):
    sub: UUID4
    type: TokenType


class Token(BaseModel):
    token: str
    expired: datetime | None


class TokenResponse(BaseModel):
    access: Token
    refresh: Token
