from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from constants.token_type import TokenType
from constants.user_role import UserRoles
from dependencies.mongodb import MongoDBDep
from schemas.token import TokenPayload
from schemas.user import User
from services.token import TokenService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(
    mongo: MongoDBDep,
    token: str = Depends(oauth2_scheme),
) -> User:
    token_service = TokenService()
    payload = token_service.decode(token=token)
    token_payload = TokenPayload.model_validate(payload)

    if token_payload.type != TokenType.ACCESS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Access token required')

    user = await mongo.find_by_id(User, token_payload.sub)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    return user

UserDep = Annotated[User, Depends(get_current_user)]


async def get_admin_user(user: UserDep):
    if user.role != UserRoles.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin access required')
    return user

AdminUserDep = Annotated[User, Depends(get_admin_user)]
