from fastapi import APIRouter, Body, HTTPException, status

from constants.token_type import TokenType
from dependencies.mongodb import MongoDBDep
from dependencies.user import UserDep
from schemas.token import TokenPayload, TokenResponse
from schemas.user import User
from services.token import TokenService

auth_router = APIRouter(prefix='/auth', tags=['Authentication'])


@auth_router.post('/register')
async def register_user(
    mongo: MongoDBDep,
    username: str = Body(),
    password: str = Body(),
) -> User:
    if await mongo.find_one(User, username=username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')

    user = User(username=username)
    user.set_password(plain_password=password)
    await mongo.insert_one_model(user)

    return user


@auth_router.post('/login')
async def login(
    mongo: MongoDBDep,
    username: str = Body(),
    password: str = Body(),
) -> TokenResponse:
    user = await mongo.find_one(User, username=username)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

    if not user.verify(plain_password=password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password')

    token_service = TokenService()
    return token_service.create_token_response(user)


@auth_router.post('/refresh')
async def refresh_token(
    mongo: MongoDBDep,
    token: str = Body()
) -> TokenResponse:
    token_service = TokenService()
    payload = token_service.decode(token=token)
    token_payload = TokenPayload.model_validate(payload)

    if token_payload.type != TokenType.REFRESH:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Refresh token required')

    user = await mongo.find_by_id(User, token_payload.sub)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

    return token_service.create_token_response(user)


@auth_router.post('/change-password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    mongo: MongoDBDep,
    user: UserDep,
    current_password: str = Body(),
    new_password: str = Body(),
):
    if current_password == new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='New password is same as current password')

    if not user.verify(plain_password=current_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Current password incorrect')

    new_password_hash = user.set_password(plain_password=new_password)
    await mongo.update_by_id(user, password=new_password_hash)
