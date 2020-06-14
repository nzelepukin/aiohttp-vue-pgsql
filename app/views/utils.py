import os, logging
from aiohttp import web, MultipartReader, ClientSession
from modules.lvs_ssh import start_ssh
from modules.switch_snmp import snmp_gathering
from modules.panda_switch import xls_to_base
from aiohttp.web_exceptions import HTTPNotFound
from http import HTTPStatus
from aiohttp.web_urldispatcher import View
from asyncpgsa import PG
from aiohttp.web_response import Response
from marshmallow.validate import ValidationError
from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import session_middleware, setup, get_session, new_session
from modules.schema import RequestAddUser, RequestEditUser, RequestDeleteUser
from database import pg_add_user, pg_edit_user, pg_delete_user, pg_check_user
from database import pg_select_users, pg_select_user_by_id
from modules.auth import login_required, admin_required

class Utils(View):

    @property
    def pg(self) -> PG:
        return self.request.app['pg']

    @login_required 
    async def get(self):
        device_list=[{"ip":"192.168.101.10"},{"ip":"192.168.101.11"}]
        async with ClientSession() as client_session:
            output=list()
            login_url='http://nginx/data/login'
            url='http://nginx/data/device'
            logging.info (os.environ['NGINXHOST'])
            async with client_session.post(login_url,data={
                    'username': self.request.app['user']['username'],
                    'password': self.request.app['user']['password']}) as resp:
                logging.info(await resp.text())
            for record in device_list:
                async with client_session.post(url,json=record) as resp:
                    try: output.append(await resp.json())
                    except: output.append({'status':False})
        return web.json_response(output, content_type='application/json')

    @login_required 
    async def patch(self):
        '''  
        Takes list of IP return device info with SNMP 
        In example - [{"id": 2, "ip":"xxx.xxx.xxx.xxx"}]
        Out example - [{"id": 2, "hostname": str, "model": str, "dev_ios": str, "serial_n": str}]
        '''
        ip_list = await self.request.json()
        snmp_community=os.environ['SNMP_COMMUNITY']
        logging.info(snmp_community)
        logging.info(ip_list)
        if snmp_community:
            info_list = await snmp_gathering(ip_list,snmp_community)
            output=list()
            for record in info_list:
                if record['status']:
                    del (record['output']['manufacturer'])
                    if not 'stack' in record['output']:
                        output.append(record['output'])
                    else:
                        for num_in_stack in range(1,record['output']['stack']+1):
                            stack_device= {
                                'hostname': '{} ({})'.format(record['output']['hostname'],num_in_stack),
                                'model':record['output']['model'].split('-stack-')[num_in_stack-1],
                                'serial_n':record['output']['serial_n'].split('-stack-')[num_in_stack-1],
                                'dev_ios':record['output']['dev_ios']
                                }
                            if num_in_stack==1: 
                                stack_device['dev_id']=record['output']['dev_id']
                                output.append(stack_device)
                            else: 
                                stack_device['ip']='stack'
                                db_device=pg_select_one('hostname',stack_device['hostname'])
                                if db_device['status']:
                                    stack_device['dev_id']=db_device['output']['dev_id']
                                    output.append(stack_device)
                                else:
                                    db_device=pg_select_one('dev_id',record['output']['dev_id'])
                                    del (db_device['output']['dev_id'])
                                    for param in stack_device:
                                        db_device['output'][param]=stack_device[param]
                                    output.append(db_device['output'])
                else: output.append(record['output'])
            return web.json_response(output, content_type='application/json')
        else: 
            return web.json_response('No SNMP community', content_type='application/json')

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

