import json
import uuid
from typing import Any

import jwt
from bson import ObjectId
from fastapi import HTTPException, status
from pydantic import BaseModel

from configs.settings import ALGORITHM, SECRET_KEY
from constants.token_type import TokenType
from schemas.token import Token, TokenPayload, TokenResponse, WhiteListToken
from schemas.user import User
from services.mongodb import MongoDBService


class JWTService:
    class Encoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, (uuid.UUID, ObjectId)):
                return str(o)
            return super().default(o)

    def __init__(self, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm

    def encode(self, data: dict[str, Any] | BaseModel) -> str:
        to_encode = data.model_dump(exclude_none=True) if isinstance(data, BaseModel) else data.copy()
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm, json_encoder=self.Encoder)

    def decode(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])


class TokenService(JWTService):
    def __init__(self, mongo: MongoDBService, *args, **kwargs) -> None:
        self.mongo = mongo
        super().__init__(*args, **kwargs)

    def create_access_token(self, user: User) -> Token:
        payload = TokenPayload.access(user)
        token = self.encode(payload)
        return Token(token=token, expired=payload.exp)

    async def create_refresh_token(self, user: User) -> Token:
        payload = TokenPayload.refresh(user)
        token = self.encode(payload)

        await self.mongo.insert_object(WhiteListToken(jti=payload.jti, user_id=user.id, expired=payload.exp))

        return Token(token=token, expired=payload.exp)

    async def create_token_response(self, user: User) -> TokenResponse:
        access = self.create_access_token(user)
        refresh = await self.create_refresh_token(user)
        return TokenResponse(access=access, refresh=refresh)

    async def decode_payload(self, token: str) -> TokenPayload:
        payload = self.decode(token)
        token_payload = TokenPayload.model_validate(payload)

        if (
            token_payload.type == TokenType.REFRESH
            and not await self.mongo.find_one(WhiteListToken, jti=token_payload.jti)
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is revoked')

        return token_payload

    async def revoke(self, jti: str) -> None:
        await self.mongo.delete_one(WhiteListToken, jti=jti)

    async def revoke_all(self, user_id: str) -> None:
        await self.mongo.delete_many(WhiteListToken, _user_id=ObjectId(user_id))
