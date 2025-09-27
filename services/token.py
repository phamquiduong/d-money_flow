import uuid
from datetime import datetime

import jwt

from settings import ALGORITHM, SECRET_KEY


class TokenService:
    def __init__(self, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm

    def encode(self, data: dict, expired_time: datetime | None = None) -> str:
        to_encode = data.copy()

        to_encode['jti'] = str(uuid.uuid4())

        if expired_time:
            to_encode['exp'] = expired_time

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
