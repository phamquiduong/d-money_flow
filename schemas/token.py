from datetime import datetime

from pydantic import BaseModel


class Token(BaseModel):
    token: str
    exp: datetime
    type: str


class AccessToken(Token):
    type: str = 'access'


class RefreshToken(Token):
    type: str = 'refresh'


class TokenResponse(BaseModel):
    access_token: AccessToken
    refresh_token: RefreshToken
