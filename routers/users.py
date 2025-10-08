from fastapi import APIRouter, Path, status

import messages
from dependencies.token import TokenServiceDep
from dependencies.user import AdminUserDep, CurrentOrAdminUserDep, UserDep, UserServiceDep
from exceptions.api_exception import APIException
from schemas.api.change_password import ChangePasswordRequest
from schemas.api.list_query import ListQueryDep
from schemas.api.user_create import UserCreateRequest
from schemas.api.user_update import UserUpdateRequest
from schemas.user import User

users_router = APIRouter(prefix='/users', tags=['User'])


@users_router.get('')
async def get_all_users(
    auth_user: AdminUserDep,
    user_service: UserServiceDep,
    list_query: ListQueryDep,
) -> list[User]:
    return await user_service.get_list(limit=list_query.limit, offset=list_query.offset)


@users_router.post('', status_code=status.HTTP_201_CREATED)
async def register_user(
    user_service: UserServiceDep,
    request: UserCreateRequest,
) -> User:
    if await user_service.is_exist_username(request.username):
        raise APIException(status_code=status.HTTP_409_CONFLICT,
                           detail=messages.user_exists, fields={'username': messages.user_exists})
    return await user_service.create(username=request.username, password=request.password)


@users_router.get('/me')
async def get_me(
    auth_user: UserDep,
) -> User:
    return auth_user


@users_router.get('/{user_id}')
async def get_user(
    auth_user: CurrentOrAdminUserDep,
    user_service: UserServiceDep,
    user_id: str = Path(),
) -> User:
    user = auth_user if auth_user.id == user_id else await user_service.get_by_id(user_id)
    if not user:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND,
                           detail=messages.user_not_found, fields={'user_id': messages.user_not_found})
    return user


@users_router.put('/{user_id}')
async def update_user(
    auth_user: CurrentOrAdminUserDep,
    user_service: UserServiceDep,
    request: UserUpdateRequest,
    user_id: str = Path(),
) -> User:
    user = auth_user if auth_user.id == user_id else await user_service.get_by_id(user_id)
    if not user:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND,
                           detail=messages.user_not_found, fields={'user_id': messages.user_not_found})

    if request.username != user.username and await user_service.is_exist_username(request.username):
        raise APIException(status_code=status.HTTP_409_CONFLICT,
                           detail=messages.user_exists, fields={'username': messages.user_exists})

    return await user_service.update(user, update_data=request.model_dump())


@users_router.patch('/change-password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    auth_user: UserDep,
    user_service: UserServiceDep,
    token_service: TokenServiceDep,
    request: ChangePasswordRequest,
) -> None:
    if request.current_password == request.new_password:
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail=messages.new_password_same_current,
                           fields={'new_password': messages.new_password_same_current})

    if not await user_service.verify_password(user=auth_user, password=request.new_password):
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail=messages.password_incorrect, fields={'current_password': messages.password_incorrect})

    await user_service.update_password(auth_user, new_password=request.new_password)

    await token_service.revoke_all(user_id=auth_user.id)
