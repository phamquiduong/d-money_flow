from typing import Annotated

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

import messages
from constants.header import BEARER_ERROR_HEADER
from constants.token_type import TokenType
from constants.user_role import UserRole
from dependencies.mongodb import MongoDBDep
from dependencies.token import TokenServiceDep
from exceptions.api_exception import APIException
from schemas.user import User
from services.user import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_user_service(mongo: MongoDBDep):
    return UserService(mongo=mongo)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
    user_service: UserServiceDep,
    token_service: TokenServiceDep,
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        token_payload = await token_service.decode_payload(token)
    except InvalidTokenError as exc:
        raise APIException(status_code=status.HTTP_401_UNAUTHORIZED, headers=BEARER_ERROR_HEADER,
                           detail=messages.token_invalid, fields={'bearer_token': str(exc)}) from exc

    if token_payload.type != TokenType.ACCESS:
        raise APIException(status_code=status.HTTP_401_UNAUTHORIZED, headers=BEARER_ERROR_HEADER,
                           detail=messages.access_required, fields={'bearer_token': messages.access_required})

    user = await user_service.get_by_id(token_payload.sub)

    if not user:
        raise APIException(status_code=status.HTTP_401_UNAUTHORIZED, headers=BEARER_ERROR_HEADER,
                           detail=messages.user_not_found, fields={'bearer_token': messages.user_not_found})
    return user

UserDep = Annotated[User, Depends(get_current_user)]


async def get_admin_user(user: UserDep):
    if user.role != UserRole.ADMIN:
        raise APIException(status_code=status.HTTP_403_FORBIDDEN, headers=BEARER_ERROR_HEADER,
                           detail=messages.admin_required, fields={'bearer_token': messages.admin_required})
    return user

AdminUserDep = Annotated[User, Depends(get_admin_user)]


async def get_current_or_admin_user(user: UserDep, user_id: str):
    if user.role != UserRole.ADMIN and user.id != user_id:
        raise APIException(status_code=status.HTTP_403_FORBIDDEN,  headers=BEARER_ERROR_HEADER,
                           detail=messages.current_or_admin_required,
                           fields={'bearer_token': messages.current_or_admin_required})
    return user

CurrentOrAdminUserDep = Annotated[User, Depends(get_current_or_admin_user)]
