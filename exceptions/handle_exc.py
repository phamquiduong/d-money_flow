from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import messages
from configs.logger import logger
from exceptions.api_exception import APIException
from schemas.api.error import ErrorResponse, FieldError


async def validation_error_handler(request: Request, exc: RequestValidationError):
    details = []
    for error in exc.errors():
        messages_list = [error['msg']]
        fields_error = [
            FieldError(field=loc, messages=messages_list)
            for loc in error['loc'] if isinstance(loc, str) and loc not in ('body', 'query', 'path')
        ]
        details += fields_error or [FieldError(field='__all__', messages=messages_list)]

    err_res = ErrorResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            message=messages.validation_failed, details=details)
    return JSONResponse(err_res.model_dump(), status_code=err_res.status_code)


async def api_exception_handler(request: Request, exc: APIException):
    details = [FieldError(field=field, messages=messages) for field, messages in exc.fields.items()]
    err_res = ErrorResponse(status_code=exc.status_code, message=exc.detail, details=details)
    return JSONResponse(err_res.model_dump(), status_code=err_res.status_code, headers=exc.headers)


async def http_exception_handler(request: Request, exc: HTTPException):
    err_res = ErrorResponse(status_code=exc.status_code, message=exc.detail)
    return JSONResponse(err_res.model_dump(), status_code=err_res.status_code, headers=exc.headers)


async def exception_handler(request: Request, exc: Exception):
    logger.exception('Internal server error')
    err_res = ErrorResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=messages.internal_server_error)
    return JSONResponse(err_res.model_dump(), status_code=err_res.status_code)


def handle_exc(app: FastAPI):
    app.add_exception_handler(RequestValidationError, validation_error_handler)         # type: ignore
    app.add_exception_handler(APIException, api_exception_handler)                      # type: ignore
    app.add_exception_handler(HTTPException, http_exception_handler)                    # type: ignore
    app.add_exception_handler(Exception, exception_handler)
