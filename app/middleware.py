from http import HTTPStatus
from aiohttp import web
from aiohttp.web_exceptions import (
    HTTPBadRequest, HTTPException, HTTPInternalServerError,
)
from aiohttp.web_middlewares import middleware
from aiohttp.web_request import Request
from marshmallow import ValidationError

def handle_validation_error(error: ValidationError, *_):
    """
    Представляет ошибку валидации данных в виде HTTP ответа.
    """
    raise web.HTTPUnauthorized(reason='Request validation has failed')

@middleware
async def error_middleware(request: Request, handler):
    try:
        return await handler(request)
    except ValidationError:
        # Ошибки валидации, брошенные в обработчиках
        raise web.HTTPUnauthorized(reason='Request validation has failed')


