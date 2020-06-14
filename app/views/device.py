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
from modules.schema import RequestAddUser, RequestChangePass, RequestDeleteUser
from database import pg_add_model, pg_check_model
from database import pg_add_device , pg_edit_device , pg_delete_device, pg_select_devices
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
        device_dict = await self.check_device_dict(input_dict)
        logging.info(device_dict)
        output = await pg_add_device(self, device_dict )
        return web.json_response(output, content_type='application/json')
    
    @request_schema(RequestEditDevice())
    @docs(summary='Редактировать устройство')
    @admin_required 
    async def patch(self):
        input_dict = await self.request.json()
        full_device_dict = await self.check_device_dict(input_dict)
        device_dict = {param:full_device_dict[param] \
                        for param in full_device_dict \
                        if param in input_dict}
        device_dict['dev_id']=input_dict['dev_id']
        output = await pg_edit_device(self, device_dict )
        return web.json_response(output, content_type='application/json')  

    @docs(summary='Удалить устройства')
    @admin_required 
    async def delete(self):
        devices = self.request.match_info.get('del_string', '0')
        logging.info(devices)
        output = [await pg_delete_device(self,int(id) ) for id in devices.split('+')]
        return web.json_response(output, content_type='application/json') 
    
    async def check_device_dict(self, device_dict):
        def_device={
            'hostname':'none',
            'serial_n':'none',
            'dev_ios':'none',
            'inv_n':'none',
            'nom_n':'none',
            'description':'none',
            'ip':'none',
            'power_type':'не гарантированное',
            'protocol':'none',
            'switch_type':'none',
            'place':'none',
            'building':'none',
            'room':'none',
            'model_id':1, 
            'project':'none', 
            'in_date':'01.01.1900'
            }
        if 'model' in device_dict:
            check = await pg_check_model(self, device_dict['model'])
            if not check['status']:
                new_model={
                    'model':device_dict['model'],
                    'rec_ios':'none',
                    'power':0}
                if 'rec_ios' in device_dict:
                    new_model['rec_ios']=device_dict['rec_ios']
                if 'power' in device_dict:
                    new_model['power']=device_dict['power']
                output = await pg_add_model(self, new_model )
                if output['status']:
                    check= await pg_check_model(self, device_dict['model'])
            try:
                device_dict['model_id']=check['output'][0]
            except:
                logging.error(check)
        for param in device_dict:
            if param in def_device: def_device[param]=device_dict[param]
        def_device['in_date']=datetime.datetime.strptime(def_device['in_date'],"%d.%m.%Y")
        return def_device
