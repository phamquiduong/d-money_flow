from typing import Annotated

from fastapi import Depends

from services.mongodb import MongoDBService


async def get_mongo_service():
    service = MongoDBService()

    try:
        yield service
    finally:
        await service.client.close()


MongoDBDep = Annotated[MongoDBService, Depends(get_mongo_service)]
