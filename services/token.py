import json
import uuid
from datetime import datetime, timedelta
from typing import Any

import jwt
from bson import ObjectId
from pydantic import BaseModel

from settings import ALGORITHM, SECRET_KEY
from utils import timezone


class TokenService:
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
    ) -> tuple[str, datetime | None]:
        to_encode = data.model_dump() if isinstance(data, BaseModel) else data.copy()
        to_encode['jti'] = uuid.uuid4()
        to_encode['iat'] = timezone.now()

        if exp_delta:
            to_encode['exp'] = to_encode['iat'] + exp_delta

        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm, json_encoder=self.Encoder)
        return token, to_encode.get('exp')

    def decode(self, token: str) -> dict:
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
