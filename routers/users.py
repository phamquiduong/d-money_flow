from fastapi import APIRouter, Path, status

import messages
from constants.header import BEARER_ERROR_HEADER
from constants.user_role import UserRole
from dependencies.mongodb import MongoDBDep
from dependencies.user import AdminUserDep, UserDep
from exceptions.api_exception import APIException
from schemas.api.list_query import ListQueryDep
from schemas.user import User

users_router = APIRouter(prefix='/users', tags=['User'])


@users_router.get('')
async def get_all_users(
    mongo: MongoDBDep,
    admin_user: AdminUserDep,
    list_query: ListQueryDep,
) -> list[User]:
    return await mongo.find_many(User, limit=list_query.limit, offset=list_query.offset)


@users_router.get('/me')
async def get_current_user(
    current_user: UserDep,
) -> User:
    return current_user


@users_router.get('/{user_id}')
async def get_user_profile(
    mongo: MongoDBDep,
    current_user: UserDep,
    user_id: str = Path(),
) -> User:
    if current_user.id == user_id:
        return current_user

    if current_user.role != UserRole.ADMIN:
        raise APIException(status_code=status.HTTP_403_FORBIDDEN,
                           detail=messages.current_or_admin_required, headers=BEARER_ERROR_HEADER)

    user = await mongo.find_by_id(User, object_id=user_id)
    if not user:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND,
                           detail=messages.user_not_found, headers=BEARER_ERROR_HEADER)

    return user
