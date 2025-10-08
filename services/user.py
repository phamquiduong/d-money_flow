from typing import Any

from models.user import User
from services.mongodb import MongoDBService


class UserService:
    def __init__(self, mongo: MongoDBService) -> None:
        self.mongo = mongo

    async def get_by_id(self, user_id: str) -> User | None:
        return await self.mongo.find_by_id(User, user_id)

    async def get_by_username(self, username: str) -> User | None:
        return await self.mongo.find_one(User, username=username)

    async def is_valid(self, user: User) -> bool:
        return True

    async def verify_password(self, user: User, password: str) -> bool:
        return user.verify(plain_password=password)

    async def is_exist_id(self, user_id: str) -> bool:
        user = await self.get_by_id(user_id)
        return user is not None

    async def is_exist_username(self, username: str) -> bool:
        user = await self.get_by_username(username)
        return user is not None

    async def get_list(self, limit: int, offset: int, order_by: str | None = None) -> list[User]:
        return await self.mongo.find_many(User, limit=limit, offset=offset, order_by=order_by)

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

    async def delete(self, user: User):
        await self.mongo.delete_object(user)
