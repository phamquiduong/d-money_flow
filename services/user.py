from typing import Any

from schemas.user import User
from services.mongodb import MongoDBService


class UserService:
    def __init__(self, mongo: MongoDBService) -> None:
        self.mongo = mongo
        self.model = User

    async def get_by_id(self, user_id: str) -> User | None:
        return await self.mongo.find_by_id(self.model, user_id)

    async def get_by_username(self, username: str) -> User | None:
        return await self.mongo.find_one(self.model, username=username)

    async def is_valid(self, user: User) -> bool:
        return True

    async def verify_password(self, user: User, password: str) -> bool:
        return user.verify(plain_password=password)

    async def is_exist_id(self, user_id: str) -> bool:
        user = self.get_by_id(user_id)
        return user is not None

    async def is_exist_username(self, username: str) -> bool:
        user = self.get_by_username(username)
        return user is not None

    async def get_list(self, limit: int, offset: int) -> list[User]:
        return await self.mongo.find_many(self.model, limit=limit, offset=offset)

    async def create(self, username: str, password: str) -> User:
        user = User(username=username)
        user.set_password(plain_password=password)
        await self.mongo.insert_object(user)
        return user

    async def update(self, user: User, update_data: dict[str, Any]) -> User:
        user = user.model_copy(update=update_data)
        await self.mongo.update_object(user)
        return user

    async def update_password(self, user: User, new_password: str) -> User:
        user.set_password(plain_password=new_password)
        await self.mongo.update_object(user)
        return user
