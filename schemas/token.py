import uuid
from datetime import datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, Field, model_validator

from configs.settings import ACCESS_EXPIRED, REFRESH_EXPIRED
from constants.token_type import TokenType
from schemas.base import MongoModel
from schemas.user import User
from utils import timezone


class WhiteListToken(MongoModel):
    jti: str
    user_id: str
    expired: datetime

    mongodb_collection = 'white_list_tokens'

    def model_dump_mongo(self, *args, **kwargs) -> dict[str, Any]:
        data = super().model_dump_mongo(*args, **kwargs)
        data['_user_id'] = ObjectId(data.pop('user_id'))
        return data

    @model_validator(mode='before')
    @classmethod
    def handle_user_id(cls, data: dict) -> dict:
        if '_user_id' in data and isinstance(data['_user_id'], ObjectId):
            data['user_id'] = str(data.pop('_user_id'))
        return data


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
