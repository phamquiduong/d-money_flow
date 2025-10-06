from pydantic import BaseModel


class RefreshTokenRequest(BaseModel):
    token: str
