from pydantic import BaseModel

from schemas.field.username import UsernameField


class UpdateUserRequest(BaseModel):
    username: UsernameField
