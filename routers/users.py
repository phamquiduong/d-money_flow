from fastapi import APIRouter, Path, status

import messages
from dependencies.mongodb import MongoDBDep
from dependencies.user import AdminUserDep, CurrentOrAdminUserDep, UserDep
from exceptions.api_exception import APIException
from schemas.api.list_query import ListQueryDep
from schemas.api.update_user import UpdateUserRequest
from schemas.user import User

users_router = APIRouter(prefix='/users', tags=['User'])


@users_router.get('')
async def get_all_users(
    mongo: MongoDBDep,
    current_user: AdminUserDep,
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
    current_user: CurrentOrAdminUserDep,
    user_id: str = Path(),
) -> User:
    user = current_user if current_user.id == user_id else await mongo.find_by_id(User, object_id=user_id)
    if not user:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND,
                           detail=messages.user_not_found, fields={'user_id': messages.user_not_found})
    return user


@users_router.put('/{user_id}')
async def update_user(
    mongo: MongoDBDep,
    current_user: CurrentOrAdminUserDep,
    request: UpdateUserRequest,
    user_id: str = Path(),
) -> User:
    user = current_user if current_user.id == user_id else await mongo.find_by_id(User, object_id=user_id)
    if not user:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND,
                           detail=messages.user_not_found, fields={'user_id': messages.user_not_found})

    if request.username != user.username and await mongo.find_one(User, username=request.username):
        raise APIException(status_code=status.HTTP_409_CONFLICT,
                           detail=messages.user_exists, fields={'username': messages.user_exists})

    user = user.model_copy(update=request.model_dump())
    await mongo.update_object(user)

    return user
