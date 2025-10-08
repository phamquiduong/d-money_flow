from datetime import datetime
from typing import Any

from bson import ObjectId
from pydantic import model_validator

from schemas.base import MongoModel


class WhiteListToken(MongoModel):
    jti: str
    user_id: str
    expired: datetime

    mongodb_collection = 'white_list_tokens'

    def model_dump_mongo(self, *args, **kwargs) -> dict[str, Any]:
        data = super().model_dump_mongo(*args, **kwargs)
        data['_user_id'] = ObjectId(data.pop('user_id'))
        return data

    @model_validator(mode='before')
    @classmethod
    def handle_user_id(cls, data: dict) -> dict:
        if '_user_id' in data and isinstance(data['_user_id'], ObjectId):
            data['user_id'] = str(data.pop('_user_id'))
        return data
