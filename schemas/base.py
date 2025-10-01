from typing import Any, ClassVar

from bson import ObjectId
from pydantic import BaseModel, Field, model_validator

from utils.name import camel_to_snake


class MongoModel(BaseModel):
    id: str = Field(default_factory=lambda: '<not created>')
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

    def model_dump_mongo(self, *args, **kwargs) -> dict[str, Any]:
        return super().model_dump(*args, **kwargs, exclude_none=True, exclude={'id'})
