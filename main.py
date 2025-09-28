import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from routers.auth import auth_router
from services.mongodb import MongoDBService

# Config log
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] [%(asctime)s] [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# Ping MongoDB
@asynccontextmanager
async def lifespan(app: FastAPI):
    mongodb_service = MongoDBService()
    await mongodb_service.ping()
    await mongodb_service.client.close()
    yield

app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(auth_router)
