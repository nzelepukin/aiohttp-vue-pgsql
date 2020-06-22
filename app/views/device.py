import logging, datetime
from aiohttp.web_exceptions import HTTPNotFound
from http import HTTPStatus
from aiohttp.web_urldispatcher import View
from asyncpgsa import PG
from aiohttp.web_response import Response
from marshmallow.validate import ValidationError
from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import session_middleware, setup, get_session, new_session
from devbase_logic import device_add,device_edit
from database import pg_delete_device, pg_select_devices
from modules.auth import login_required, admin_required
from modules.schema import RequestAddDevice ,RequestEditDevice

class Device(View):
    URL_PATH = r'/device'

    @property
    def pg(self) -> PG:
        return self.request.app['pg']

    @docs(summary='Выбрать устройства из базы')
    @login_required 
    async def get(self):
        output = await pg_select_devices(self)
        return web.json_response(output['output'], content_type='application/json')

    @request_schema(RequestAddDevice())
    @docs(summary='Добавить устройство в базу')
    @login_required 
    async def post(self):
        input_dict = await self.request.json()
        return web.json_response(
            await device_add(self, input_dict), 
            content_type='application/json')
    
    @request_schema(RequestEditDevice())
    @docs(summary='Редактировать устройство')
    @admin_required 
    async def patch(self):
        input_dict = await self.request.json()
        return web.json_response(
            await device_edit(self, input_dict), 
            content_type='application/json')

    @docs(summary='Удалить устройства')
    @admin_required 
    async def delete(self):
        devices = self.request.match_info.get('del_string', '0')
        logging.info(devices)
        output = [await pg_delete_device(self,int(id) ) for id in devices.split('+')]
        return web.json_response(output, content_type='application/json') 
