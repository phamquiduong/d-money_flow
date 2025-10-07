from fastapi import APIRouter, status
from jwt import InvalidTokenError

from constants.token_type import TokenType
from dependencies.mongodb import MongoDBDep
from dependencies.user import UserDep
from exceptions.api_exception import APIException
from schemas.api.change_password import ChangePasswordRequest
from schemas.api.login import LoginRequest
from schemas.api.refresh_token import RefreshTokenRequest
from schemas.api.register import RegisterRequest
from schemas.token import TokenResponse
from schemas.user import User
from services.token import TokenService

auth_router = APIRouter(prefix='/auth', tags=['Authentication'])


@auth_router.post('/register', status_code=status.HTTP_201_CREATED)
async def register_user(
    mongo: MongoDBDep,
    request: RegisterRequest,
) -> User:
    if await mongo.find_one(User, username=request.username):
        raise APIException(status_code=status.HTTP_409_CONFLICT, detail='User already exists',
                           fields={'username': 'Username already exists'})

    user = User(username=request.username)
    user.set_password(plain_password=request.password)
    await mongo.insert_object(user)

    return user


@auth_router.post('/login')
async def login(
    mongo: MongoDBDep,
    request: LoginRequest,
) -> TokenResponse:
    user = await mongo.find_one(User, username=request.username)

    if not user:
        raise APIException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found',
                           fields={'username': 'Username not found'})

    if not user.verify(plain_password=request.password):
        raise APIException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Password incorrect',
                           fields={'password': 'Password is incorrect'})

    token_service = TokenService(mongo=mongo)
    return await token_service.create_token_response(user)


@auth_router.post('/refresh')
async def refresh_token(
    mongo: MongoDBDep,
    request: RefreshTokenRequest,
) -> TokenResponse:
    token_service = TokenService(mongo=mongo)

    try:
        token_payload = await token_service.decode_payload(request.token)
    except (InvalidTokenError, APIException) as exc:
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail='Token is invalid', fields={'token': str(exc)}) from exc

    if token_payload.type != TokenType.REFRESH:
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail='Refresh token required', fields={'token': 'Refresh token required'})

    user = await mongo.find_by_id(User, token_payload.sub)

    if not user:
        raise APIException(status_code=status.HTTP_401_UNAUTHORIZED,
                           detail='User not found', fields={'token': 'User in token not found'})

    await token_service.revoke(jti=token_payload.jti)
    return await token_service.create_token_response(user)


@auth_router.post('/change-password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    mongo: MongoDBDep,
    user: UserDep,
    request: ChangePasswordRequest,
):
    if request.current_password == request.new_password:
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail='The new password is the same as the current password',
                           fields={'new_password': 'The new password is the same as the current password'})

    if not user.verify(plain_password=request.current_password):
        raise APIException(status_code=status.HTTP_400_BAD_REQUEST, detail='The current password is incorrect',
                           fields={'current_password': 'The current password is incorrect'})

    new_password_hash = user.set_password(plain_password=request.new_password)
    await mongo.update_object(user, password=new_password_hash)

    token_service = TokenService(mongo=mongo)
    await token_service.revoke_all(user_id=user.id)
