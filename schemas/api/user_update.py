from pydantic import BaseModel

from schemas.field.username import UsernameField


class UserUpdateRequest(BaseModel):
    username: UsernameField
