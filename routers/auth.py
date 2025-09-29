from fastapi import APIRouter, Body, HTTPException, status

from dependencies.mongodb import MongoDBDep
from schemas.token import Token, TokenPayload, TokenResponse, TokenType
from schemas.user import User, UserResponse
from services.token import TokenService
from settings import ACCESS_EXPIRED, REFRESH_EXPIRED

auth_router = APIRouter(prefix='/auth', tags=['Authentication'])


@auth_router.post('/register')
async def register_user(
    mongo: MongoDBDep,
    username: str = Body(),
    password: str = Body(),
) -> UserResponse:
    if await mongo.find_one(User, username=username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')

    user = User.create(username=username, plain_password=password)
    await mongo.insert_one_model(user)

    return UserResponse.from_model(user)


@auth_router.post('/login')
async def login(
    mongo: MongoDBDep,
    username: str = Body(),
    password: str = Body(),
) -> TokenResponse:
    user: User | None = await mongo.find_one(User, username=username)  # type:ignore

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')

    if not user.verify(plain_password=password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Password is incorrect')

    token_service = TokenService()

    token, expired = \
        token_service.encode(data=TokenPayload(sub=user.id, type=TokenType.ACCESS), exp_delta=ACCESS_EXPIRED)
    access = Token(token=token, expired=expired)

    token, expired = \
        token_service.encode(data=TokenPayload(sub=user.id, type=TokenType.REFRESH), exp_delta=REFRESH_EXPIRED)
    refresh = Token(token=token, expired=expired)

    return TokenResponse(access=access, refresh=refresh)
