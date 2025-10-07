from typing import Annotated

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer

from constants.header import BEARER_ERROR_HEADER
from constants.token_type import TokenType
from constants.user_role import UserRole
from dependencies.mongodb import MongoDBDep
from exceptions.api_exception import APIException
from schemas.user import User
from services.token import TokenService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(
    mongo: MongoDBDep,
    token: str = Depends(oauth2_scheme),
) -> User:
    token_service = TokenService(mongo=mongo)
    token_payload = await token_service.decode_payload(token)

    if token_payload.type != TokenType.ACCESS:
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail='Access token required', headers=BEARER_ERROR_HEADER)

    user = await mongo.find_by_id(User, token_payload.sub)

    if not user:
        raise APIException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found', headers=BEARER_ERROR_HEADER)

    return user


UserDep = Annotated[User, Depends(get_current_user)]


async def get_admin_user(user: UserDep):
    if user.role != UserRole.ADMIN:
        raise APIException(status_code=status.HTTP_403_FORBIDDEN,
                           detail='Admin access required', headers=BEARER_ERROR_HEADER)

    return user


AdminUserDep = Annotated[User, Depends(get_admin_user)]
