from pydantic import Field

from schemas.base import MongoModel
from services.password import PasswordService


class User(MongoModel):
    username: str
    password: str

    mongodb_collection = 'users'

    @staticmethod
    def create_password(plain_password: str) -> str:
        password_service = PasswordService()
        return password_service.hash_password(plain_password)

    def verify(self, plain_password: str) -> bool:
        password_service = PasswordService()
        return password_service.verify_password(plain_password=plain_password, hashed_password=self.password)

    @classmethod
    def create(cls, username: str, plain_password: str):
        password = cls.create_password(plain_password)
        return cls(username=username, password=password)


class UserResponse(User):
    password: str = Field(exclude=True)

    @classmethod
    def from_model(cls, user: User):
        return cls.model_validate(user.model_dump())
