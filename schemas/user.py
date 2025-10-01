from typing import Any

from pydantic import Field

from constants.user_role import UserRoles
from schemas.base import MongoModel
from services.password import PasswordService


class User(MongoModel):
    username: str
    password: str = Field(default_factory=lambda: '<not set>', exclude=True)

    role: UserRoles = UserRoles.GUEST

    mongodb_collection = 'users'

    def set_password(self, plain_password: str) -> None:
        password_service = PasswordService()
        self.password = password_service.hash_password(plain_password)

    def verify(self, plain_password: str) -> bool:
        password_service = PasswordService()
        return password_service.verify_password(plain_password=plain_password, hashed_password=self.password)

    def model_dump_mongo(self, *args, **kwargs) -> dict[str, Any]:
        dump_data = super().model_dump_mongo(*args, **kwargs)
        dump_data.update({'password': self.password})
        return dump_data
