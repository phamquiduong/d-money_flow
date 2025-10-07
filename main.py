from fastapi import FastAPI

from configs.logger import config_logging
from exceptions.handle_exc import handle_exc
from routers.auth import auth_router
from routers.users import users_router

# Config logging
config_logging()

app = FastAPI()
handle_exc(app)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
