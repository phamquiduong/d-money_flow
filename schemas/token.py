import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from configs.settings import ACCESS_EXPIRED, REFRESH_EXPIRED
from constants.token_type import TokenType
from models.user import User
from utils import timezone


class TokenPayload(BaseModel):
    sub: str
    type: TokenType
    jti: str = Field(default_factory=lambda: str(uuid.uuid4()))
    iat: datetime = Field(default_factory=timezone.now)
    exp: datetime

    @classmethod
    def access(cls, user: User):
        now = timezone.now()
        return cls(sub=user.id, type=TokenType.ACCESS, iat=now, exp=now+ACCESS_EXPIRED)

    @classmethod
    def refresh(cls, user: User):
        now = timezone.now()
        return cls(sub=user.id, type=TokenType.REFRESH, iat=now, exp=now+REFRESH_EXPIRED)


class Token(BaseModel):
    token: str
    expired: datetime


class TokenResponse(BaseModel):
    access: Token
    refresh: Token
