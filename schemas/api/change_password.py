from pydantic import BaseModel

from schemas.field.password import PasswordField


class ChangePasswordRequest(BaseModel):
    current_password: PasswordField
    new_password: PasswordField
