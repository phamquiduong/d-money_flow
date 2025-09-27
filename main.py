from fastapi import FastAPI

from services.mongodb import MongoDBService

app = FastAPI()

mongodb_service = MongoDBService()
mongodb_service.ping()
