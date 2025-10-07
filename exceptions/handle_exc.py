from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jwt.exceptions import InvalidTokenError

from configs.logger import logger
from constants.header import BEARER_ERROR_HEADER
from exceptions.api_exception import APIException
from schemas.api.error import ErrorResponse, FieldError


async def token_error_handler(request: Request, exc: InvalidTokenError):
    error = ErrorResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                          error_code='token_invalid', message='Token is invalid')
    return JSONResponse(content=error.model_dump(mode='json'), status_code=error.status_code,
                        headers=BEARER_ERROR_HEADER)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []
    for error in exc.errors():
        fields_error = [
            FieldError(field=loc, messages=[error['msg']])
            for loc in error['loc'] if isinstance(loc, str) and loc not in ('body', 'query', 'path')
        ] or [FieldError(field='__all__', messages=[error['msg']])]
        details += fields_error

    error_response = ErrorResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                   error_code='validation_error', message='Validation failed', details=details)
    return JSONResponse(content=error_response.model_dump(mode='json'), status_code=error_response.status_code)


async def api_exception_handler(request: Request, exc: APIException):
    details = [FieldError(field=field, messages=messages) for field, messages in exc.fields.items()]
    error_response = ErrorResponse(status_code=exc.status_code, error_code='api_error',
                                   message=exc.detail, details=details)
    return JSONResponse(content=error_response.model_dump(mode='json'),
                        status_code=exc.status_code, headers=exc.headers)


async def http_exception_handler(request: Request, exc: HTTPException):
    error = ErrorResponse(status_code=exc.status_code, error_code='http_error', message=exc.detail)
    return JSONResponse(content=error.model_dump(mode='json'), status_code=error.status_code, headers=exc.headers)


async def exception_handler(request: Request, exc: Exception):
    logger.exception('Internal server error')
    error = ErrorResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          error_code='internal_error', message='Internal server error')
    return JSONResponse(content=error.model_dump(mode='json'), status_code=error.status_code)


def handle_exc(app: FastAPI):
    app.add_exception_handler(InvalidTokenError, token_error_handler)                   # type: ignore
    app.add_exception_handler(RequestValidationError, validation_exception_handler)     # type: ignore
    app.add_exception_handler(APIException, api_exception_handler)                      # type: ignore
    app.add_exception_handler(HTTPException, http_exception_handler)                    # type: ignore
    app.add_exception_handler(Exception, exception_handler)
