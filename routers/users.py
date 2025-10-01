from fastapi import APIRouter

from dependencies.mongodb import MongoDBDep
from dependencies.user import AdminUserDep
from schemas.user import User

users_router = APIRouter(prefix='/users', tags=['User'])


@users_router.get('')
async def get_all_users(
    mongo: MongoDBDep,
    admin_user: AdminUserDep
) -> list[User]:
    return await mongo.find_many(User)
