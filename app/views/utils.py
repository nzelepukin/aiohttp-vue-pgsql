import os, logging
from aiohttp import web, MultipartReader, ClientSession
from aiohttp.web_exceptions import HTTPNotFound
from http import HTTPStatus
from aiohttp.web_urldispatcher import View
from asyncpgsa import PG
from aiohttp.web_response import Response
from marshmallow.validate import ValidationError
from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import session_middleware, setup, get_session, new_session
from modules.schema import RequestAddUser, RequestEditUser, RequestDelete
from devbase_logic import snmp_info
from modules.auth import login_required, admin_required
from modules.lvs_ssh import start_ssh

class Utils(View):

    @property
    def pg(self) -> PG:
        return self.request.app['pg']

    @login_required 
    async def patch(self):
        ip_list = await self.request.json()
        return web.json_response(await snmp_info(self, ip_list), content_type='application/json')

    async def post(self):
        ''' Upload file from frontend to xls_file_path, parse it using Pandas and add to DB '''
        xls_file_path='modules/file.xls'
        reader = MultipartReader.from_response(self.request)
        client_file=list()
        while True:
            part = await reader.next()
            if part is None:
                break
            client_file.append(await part.read(decode=False))
        with open(xls_file_path,'wb') as xls_file:
            for part in client_file:
                xls_file.write(part)
        if os.path.exists(xls_file_path):
            device_list = xls_to_base(xls_file_path)
            os.remove(xls_file_path)
            return web.json_response(device_list, content_type='application/json')
        else: 
            return web.json_response('Error: File NOT created' , content_type='application/json')

class Multiconsole(View):

    @property
    def pg(self) -> PG:
        return self.request.app['pg']

    @login_required 
    async def post(self):
        ''' Multi SSH client '''
        cred_dict = await self.request.json()
        cred_dict['command'] = cred_dict['command'].split('\n')
        cred_dict['ip'] = cred_dict['ip'].split('\n')
        return web.json_response(await start_ssh(cred_dict['command'],cred_dict['username'],cred_dict['password'],cred_dict['ip']), content_type='application/json')

