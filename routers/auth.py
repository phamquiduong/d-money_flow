from fastapi import APIRouter, HTTPException, status

from dependencies.mongodb import MongoDBDep
from schemas.token import AccessToken, RefreshToken, TokenResponse
from schemas.user import User, UserModel
from services.token import TokenService
from settings import ACCESS_EXP, REFRESH_EXP
from utils import timezone

auth_router = APIRouter(prefix='/auth', tags=['Authentication'])


@auth_router.post('/register')
async def register_user(
    mongo: MongoDBDep,
    username: str,
    password: str
) -> User:
    if await mongo.find_one(UserModel, username=username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')

    user_model = UserModel(username=username)
    user_model.set_password(plain_password=password)

    await mongo.insert_one_model(user_model)

    return User.from_model(user_model)


@auth_router.post('/login')
async def login(
    mongo: MongoDBDep,
    username: str,
    password: str
) -> TokenResponse:
    user_model: UserModel | None = await mongo.find_one(UserModel, username=username)  # type:ignore

    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')

    if not user_model.verify(plain_password=password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Password is incorrect')

    token_service = TokenService()

    data = {
        'user_id': user_model.id,
    }

    access_exp = timezone.now() + ACCESS_EXP
    access_token = AccessToken(
        token=token_service.encode(data, expired_time=access_exp),
        exp=access_exp
    )

    refresh_exp = timezone.now() + REFRESH_EXP
    refresh_token = RefreshToken(
        token=token_service.encode(data, expired_time=refresh_exp),
        exp=refresh_exp
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )
