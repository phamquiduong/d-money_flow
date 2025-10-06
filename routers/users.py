from fastapi import APIRouter, HTTPException, Path, Query, status

from constants.user_role import UserRoles
from dependencies.mongodb import MongoDBDep
from dependencies.user import AdminUserDep, UserDep
from schemas.user import User

users_router = APIRouter(prefix='/users', tags=['User'])


@users_router.get('')
async def get_all_users(
    mongo: MongoDBDep,
    admin_user: AdminUserDep,
    limit: int = Query(10, gt=0),
    offset: int = Query(0, ge=0),
) -> list[User]:
    return await mongo.find_many(User, limit=limit, offset=offset)


@users_router.get('/me')
async def get_current_user(current_user: UserDep) -> User:
    return current_user


@users_router.get('/{user_id}')
async def get_user_profile(
    mongo: MongoDBDep,
    current_user: UserDep,
    user_id: str = Path()
) -> User:
    if current_user.id == user_id:
        return current_user

    if current_user.role != UserRoles.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You do not have permission to access this resource.')

    user = await mongo.find_by_id(User, object_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    return user
