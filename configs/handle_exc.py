from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from jwt.exceptions import InvalidTokenError

from configs.logger import logger


async def token_error_handler(request: Request, exc: InvalidTokenError):
    return JSONResponse(
        {'detail': 'Token is invalid'},
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={'WWW-Authenticate': 'Bearer'}
    )


async def exception_handler(request: Request, exc: Exception):
    logger.exception(exc)
    return JSONResponse({'detail': 'Internal server error'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def handle_exc(app: FastAPI):
    app.add_exception_handler(InvalidTokenError, token_error_handler)  # type: ignore
    app.add_exception_handler(Exception, exception_handler)
