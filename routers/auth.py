from fastapi import APIRouter, status
from jwt import InvalidTokenError

import messages
from constants.token_type import TokenType
from dependencies.token import TokenServiceDep
from dependencies.user import UserServiceDep
from exceptions.api_exception import APIException
from schemas.api.login import LoginRequest
from schemas.api.refresh_token import RefreshTokenRequest
from schemas.token import TokenResponse

auth_router = APIRouter(prefix='/auth', tags=['Authentication'])


@auth_router.post('/login')
async def login(
    user_service: UserServiceDep,
    token_service: TokenServiceDep,
    request: LoginRequest,
) -> TokenResponse:
    user = await user_service.get_by_username(request.username)

    if not user:
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail=messages.user_not_found, fields={'username': messages.user_not_found})

    if not await user_service.is_valid(user):
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail=messages.user_not_valid, fields={'username': messages.user_not_valid})

    if await user_service.verify_password(user=user, password=request.password):
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail=messages.password_incorrect, fields={'password': messages.password_incorrect})

    return await token_service.create_token_response(user)


@auth_router.post('/refresh')
async def refresh_token(
    token_service: TokenServiceDep,
    user_service: UserServiceDep,
    request: RefreshTokenRequest,
) -> TokenResponse:
    try:
        token_payload = await token_service.decode_payload(request.token)
    except InvalidTokenError as exc:
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail=messages.token_invalid, fields={'token': str(exc)}) from exc

    if await token_service.is_revoke(jti=token_payload.jti):
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail=messages.token_invalid, fields={'token': messages.token_revoked})

    if token_payload.type != TokenType.REFRESH:
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail=messages.token_invalid, fields={'token': messages.refresh_required})

    user = await user_service.get_by_id(token_payload.sub)

    if not user:
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail=messages.token_invalid, fields={'token': messages.user_not_found})

    await token_service.revoke(jti=token_payload.jti)

    return await token_service.create_token_response(user)
