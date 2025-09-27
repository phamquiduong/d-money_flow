from pydantic import BaseModel, Field

from services.password import PasswordService


class UserModel(BaseModel):
    username: str
    password: str = 'not set'

    def set_password(self, plain_password: str) -> None:
        password_service = PasswordService()
        self.password = password_service.hash_password(plain_password)

    def verify(self, plain_password: str) -> bool:
        password_service = PasswordService()
        return password_service.verify_password(plain_password=plain_password, hashed_password=self.password)

    class Meta:
        mongodb_collection = 'users'


class User(UserModel):
    username: str
    password: str = Field(default='not set', exclude=True)

    @classmethod
    def from_model(cls, user_model: UserModel):
        return cls(**user_model.model_dump())
