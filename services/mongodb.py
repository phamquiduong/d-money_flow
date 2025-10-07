from contextlib import asynccontextmanager
from typing import Any, TypeVar

from bson import ObjectId
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.server_api import ServerApi

from configs.logger import logger
from configs.settings import DB_NAME, MONGO_URI
from constants.mongo import MongoUpdateType
from schemas.base import MongoModel

T = TypeVar('T', bound=MongoModel)


class MongoDBService:
    def __init__(self, mongo_uri: str = MONGO_URI, db_name: str = DB_NAME) -> None:
        self.client = AsyncMongoClient(mongo_uri, server_api=ServerApi('1'))
        self.db = self.client.get_database(db_name)

    async def ping(self) -> None:
        try:
            await self.client.admin.command('ping')
            logger.info('Pinged your deployment. You successfully connected to MongoDB!')
        except Exception:
            logger.exception('Cannot connect to MongoDB with uri: %s', MONGO_URI)

    async def close(self) -> None:
        await self.client.close()

    # ****************************************
    # Indexing
    # ****************************************
    async def create_index(self, model: type[T], keys: list[tuple[str, int]], **kwargs) -> str:
        collection = self.__get_collection(model)
        return await collection.create_index(keys, **kwargs)

    async def drop_index(self, model: type[T], name: str) -> None:
        collection = self.__get_collection(model)
        return await collection.drop_index(name)

    # ****************************************
    # Insert
    # ****************************************
    async def insert_object(self, obj: MongoModel) -> None:
        collection = self.__get_collection(obj.__class__)
        result = await collection.insert_one(obj.model_dump_mongo())
        obj.id = str(result.inserted_id)

    async def insert_objects(self, objs: list[MongoModel]) -> None:
        if not objs:
            return None

        collection = self.__get_collection(objs[0].__class__)
        docs = [data.model_dump_mongo() for data in objs]

        result = await collection.insert_many(docs)
        for model, inserted_id in zip(objs, result.inserted_ids):
            model.id = str(inserted_id)

    # ****************************************
    # Find
    # ****************************************
    async def find_one(self, model: type[T], **queries) -> T | None:
        collection = self.__get_collection(model)
        queries = self.__clean_queries(queries)
        doc = await collection.find_one(queries)
        return model.model_validate(doc) if doc else None

    async def find_many(self, model: type[T], limit: int = 10, offset: int = 0, **queries) -> list[T]:
        collection = self.__get_collection(model)
        queries = self.__clean_queries(queries)
        docs = collection.find(queries).skip(offset).limit(limit)
        return [model.model_validate(doc) async for doc in docs]

    async def find_by_id(self, model: type[T], object_id: str) -> T | None:
        return await self.find_one(model, _id=ObjectId(object_id))

    # ****************************************
    # Update
    # ****************************************
    async def update_one(self, model: type[T], queries: dict[str, Any],
                         update_type: MongoUpdateType = MongoUpdateType.SET, **update_data) -> None:
        collection = self.__get_collection(model)
        await collection.update_one(queries, {update_type.value: update_data})

    async def update_many(self, model: type[T], queries: dict[str, Any],
                          update_type: MongoUpdateType = MongoUpdateType.SET, **update_data) -> None:
        collection = self.__get_collection(model)
        await collection.update_many(queries, {update_type.value: update_data})

    async def update_object(self, obj: MongoModel,
                            update_type: MongoUpdateType = MongoUpdateType.SET, **update_data) -> None:
        await self.update_one(obj.__class__, queries={'_id': ObjectId(obj.id)}, update_type=update_type, **update_data)

    # ****************************************
    # Delete
    # ****************************************
    async def delete_one(self, model: type[T], **queries) -> None:
        collection = self.__get_collection(model)
        await collection.delete_one(queries)

    async def delete_many(self, model: type[T], **queries) -> None:
        collection = self.__get_collection(model)
        await collection.delete_many(queries)

    async def delete_object(self, data: MongoModel):
        await self.delete_one(data.__class__, _id=ObjectId(data.id))

    # ****************************************
    # Utils
    # ****************************************
    def __get_collection(self, model: type[MongoModel]) -> AsyncCollection:
        collection_name = model.get_mongodb_collection()
        return self.db[collection_name]

    @staticmethod
    def __clean_queries(queries: dict):
        return {field: value for field, value in queries.items() if value}


@asynccontextmanager
async def mongodb_service():
    service = MongoDBService()
    try:
        yield service
    except Exception:
        logger.exception('MongoDB Service error')
        raise
    finally:
        await service.close()
