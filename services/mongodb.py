from contextlib import asynccontextmanager
from typing import Any, Literal, TypeVar

from bson import ObjectId
from fastapi import status
from pymongo import ASCENDING, DESCENDING, AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.server_api import ServerApi

import messages
from configs.logger import logger
from configs.settings import DB_NAME, MONGO_URI
from constants.mongo import MongoUpdateType
from exceptions.api_exception import APIException
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

    async def find_many(
        self, model: type[T], limit: int = 10, offset: int = 0, order_by: str | None = None, **queries
    ) -> list[T]:
        collection = self.__get_collection(model)
        queries = self.__clean_queries(queries)
        sort_params = self.__convert_order_by(model.allowed_order_fields, order_by)
        docs = collection.find(queries).skip(offset).limit(limit).sort(sort_params)
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

    async def update_object(self, obj: MongoModel) -> None:
        await self.update_one(obj.__class__, queries={'_id': ObjectId(obj.id)}, **obj.model_dump_mongo())

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

    @staticmethod
    def __convert_order_by(
        allow_order: list | tuple | set, order_by: str | None = None, raise_exc: bool = True
    ) -> list[tuple[str, Literal[1, -1]]]:
        if not order_by:
            return []

        order_fields = order_by.split(',')
        order_params = []

        for order_field in order_fields:
            order_field = order_field.strip()

            if order_field.startswith('-'):
                order_field = order_field[1:]
                direction = DESCENDING
            else:
                direction = ASCENDING

            if order_field not in allow_order and raise_exc:
                message = messages.not_allowed_order_by.format(field=order_field)
                raise APIException(status_code=status.HTTP_400_BAD_REQUEST,
                                   detail=message, fields={'order_by': message})

            if order_field == 'id':
                order_field = '_id'

            order_params.append((order_field, direction))

        return order_params


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
