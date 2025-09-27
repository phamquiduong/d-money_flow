import logging

from fastapi import FastAPI

from routers.auth import auth_router
from services.mongodb import MongoDBService

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI()

mongodb_service = MongoDBService()
mongodb_service.ping()

app.include_router(auth_router)
