from fastapi import APIRouter, HTTPException, status

from dependencies.mongodb import MongoDBDep
from schemas.user import User, UserModel

auth_router = APIRouter(prefix='/auth', tags=['Authentication'])


@auth_router.post('/register')
async def register_user(
    mongo: MongoDBDep,
    username: str,
    password: str
) -> User:
    if await mongo.find_one(model=UserModel, username=username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')

    user_model = UserModel(username=username)
    user_model.set_password(plain_password=password)

    await mongo.insert_one_model(user_model)

    return User.from_model(user_model)
