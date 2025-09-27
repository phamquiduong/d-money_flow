from typing import ClassVar

from bson import ObjectId
from pydantic import BaseModel, Field, model_validator

from utils.name import camel_to_snake


class MongoModel(BaseModel):
    id: str = Field(default='not set', exclude=True)

    mongodb_collection: ClassVar[str | None] = None

    @model_validator(mode='before')
    @classmethod
    def handle_objectid(cls, data: dict) -> dict:
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['id'] = str(data.pop('_id'))

        return data

    @classmethod
    def get_mongodb_collection(cls) -> str:
        return cls.mongodb_collection or camel_to_snake(cls.__name__)
