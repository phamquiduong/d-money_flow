import logging

from pymongo import MongoClient
from pymongo.server_api import ServerApi

from settings import MONGO_URI

logger = logging.getLogger()


class MongoDBService:
    def __init__(self) -> None:
        self.client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

    def ping(self):
        try:
            self.client.admin.command('ping')
            logger.info('Pinged your deployment. You successfully connected to MongoDB!')
        except Exception:
            logger.exception('Can not connect to MongoDB with uri: %s', MONGO_URI)
