import json
import uuid
from datetime import timedelta
from typing import Any

import jwt
from bson import ObjectId
from pydantic import BaseModel

from configs.settings import ACCESS_EXPIRED, ALGORITHM, REFRESH_EXPIRED, SECRET_KEY
from constants.token_type import TokenType
from schemas.token import Token, TokenPayload, TokenResponse
from schemas.user import User
from utils import timezone


class JWTService:
    class Encoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, (uuid.UUID, ObjectId)):
                return str(o)
            return super().default(o)

    def __init__(self, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm

    def encode(
        self, data: dict[str, Any] | BaseModel, exp_delta: timedelta | None = None
    ) -> tuple[str, dict[str, Any]]:
        to_encode = data.model_dump() if isinstance(data, BaseModel) else data.copy()
        to_encode['jti'] = uuid.uuid4()
        to_encode['iat'] = timezone.now()

        if exp_delta:
            to_encode['exp'] = to_encode['iat'] + exp_delta

        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm, json_encoder=self.Encoder)
        return token, to_encode

    def decode(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])


class TokenService(JWTService):
    def create_access_token(self, user: User) -> Token:
        token, to_encode = \
            self.encode(data=TokenPayload(sub=user.id, type=TokenType.ACCESS), exp_delta=ACCESS_EXPIRED)
        return Token(token=token, expired=to_encode['exp'])

    def create_refresh_token(self, user: User) -> Token:
        token, to_encode = \
            self.encode(data=TokenPayload(sub=user.id, type=TokenType.REFRESH), exp_delta=REFRESH_EXPIRED)
        return Token(token=token, expired=to_encode['exp'])

    def create_token_response(self, user: User) -> TokenResponse:
        access = self.create_access_token(user)
        refresh = self.create_refresh_token(user)
        return TokenResponse(access=access, refresh=refresh)
