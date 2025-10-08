from typing import Annotated

from fastapi import Depends

from dependencies.mongodb import MongoDBDep
from services.token import TokenService


async def get_token_service(mongo: MongoDBDep):
    return TokenService(mongo=mongo)

TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
