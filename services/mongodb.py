import logging

from bson import ObjectId
from pydantic import BaseModel
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.server_api import ServerApi

from settings import DB_NAME, MONGO_URI

logger = logging.getLogger()


class MongoDBService:
    def __init__(self) -> None:
        self.client = AsyncMongoClient(MONGO_URI, server_api=ServerApi('1'))
        self.db = self.client[DB_NAME]

    async def ping(self):
        try:
            await self.client.admin.command('ping')
            logger.info('Pinged your deployment. You successfully connected to MongoDB!')
        except Exception:
            logger.exception('Can not connect to MongoDB with uri: %s', MONGO_URI)

    async def insert_one_model(self, data: BaseModel) -> str:
        collection = self._get_collection(data.__class__)
        result = await collection.insert_one(data.model_dump())
        return str(result.inserted_id)

    async def insert_many_models(self, list_data: list[BaseModel]) -> list[str]:
        if not list_data:
            return []
        collection = self._get_collection(list_data[0].__class__)
        docs = [data.model_dump() for data in list_data]
        result = await collection.insert_many(docs)
        return [str(inserted_id) for inserted_id in result.inserted_ids]

    async def find_by_id(self, model: type[BaseModel], object_id: str) -> BaseModel | None:
        collection = self._get_collection(model)
        doc = await collection.find_one({'_id': ObjectId(object_id)})
        return model(**doc) if doc else None

    async def find_one(self,  model: type[BaseModel], **query):
        collection = self._get_collection(model)
        doc = await collection.find_one(query)
        return model(**doc) if doc else None

    async def find_many(self, model: type[BaseModel], **query) -> list[BaseModel]:
        collection = self._get_collection(model)
        cursor = collection.find(query)
        return [model(**doc) async for doc in cursor]

    def _get_collection(self, model: type[BaseModel]) -> AsyncCollection:
        name = getattr(
            getattr(model, 'Meta', None),
            'mongodb_collection',
            model.__name__.lower()
        )
        return self.db[name]
