import logging

from bson import ObjectId
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.server_api import ServerApi

from schemas.base import MongoModel
from settings import DB_NAME, MONGO_URI

logger = logging.getLogger()


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

    async def create_index(
        self, model: type[MongoModel], name: str, keys: list[tuple[str, int]], unique: bool = False
    ) -> str:
        collection = self.__get_collection(model)
        return await collection.create_index(keys, unique=unique, name=name)

    async def drop_index(self, model: type[MongoModel], name: str) -> None:
        collection = self.__get_collection(model)
        return await collection.drop_index(name)

    async def insert_one_model(self, data: MongoModel) -> None:
        collection = self.__get_collection(data.__class__)
        result = await collection.insert_one(data.model_dump(exclude={'id'}))
        data.id = str(result.inserted_id)

    async def insert_many_models(self, list_data: list[MongoModel]) -> None:
        if not list_data:
            return None

        collection = self.__get_collection(list_data[0].__class__)
        docs = [data.model_dump(exclude={'id'}) for data in list_data]

        result = await collection.insert_many(docs)
        for model, inserted_id in zip(list_data, result.inserted_ids):
            model.id = str(inserted_id)

    async def find_by_id(self, model: type[MongoModel], object_id: str) -> MongoModel | None:
        collection = self.__get_collection(model)
        doc = await collection.find_one({'_id': ObjectId(object_id)})
        return model.model_validate(doc) if doc else None

    async def find_one(self, model: type[MongoModel], **queries) -> MongoModel | None:
        collection = self.__get_collection(model)
        doc = await collection.find_one(queries)
        return model.model_validate(doc) if doc else None

    async def find_many(self, model: type[MongoModel], **queries) -> list[MongoModel]:
        collection = self.__get_collection(model)
        cursor = collection.find(queries)
        return [model.model_validate(doc) async for doc in cursor]

    def __get_collection(self, model: type[MongoModel]) -> AsyncCollection:
        collection_name = model.get_mongodb_collection()
        return self.db[collection_name]
