from pydantic import BaseModel

from schemas.field.password import PasswordField
from schemas.field.username import UsernameField


class UserCreateRequest(BaseModel):
    username: UsernameField
    password: PasswordField
