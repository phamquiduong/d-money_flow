from datetime import datetime

from pydantic import BaseModel

from constants.token_type import TokenType


class TokenPayload(BaseModel):
    sub: str
    type: TokenType


class Token(BaseModel):
    token: str
    expired: datetime | None


class TokenResponse(BaseModel):
    access: Token
    refresh: Token
