import os,logging, datetime,json
from aiohttp.web_exceptions import HTTPNotFound
from http import HTTPStatus
from modules.lvs_ssh import start_ssh
from modules.switch_snmp import snmp_gathering
from modules.panda_switch import xls_to_base
from aiohttp.web_urldispatcher import View
from asyncpgsa import PG
from aiohttp.web_response import Response
from marshmallow.validate import ValidationError
from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import session_middleware, setup, get_session, new_session
from modules.schema import RequestAddUser, RequestChangePass, RequestDelete
from database import pg_add_model, pg_edit_model,pg_check_model, pg_check_device
from database import pg_add_device , pg_edit_device , pg_delete_device, pg_select_devices
from database import pg_select_user_by_id, pg_add_user, pg_edit_user

async def user_add(view: View,user_dict:dict)->dict:
    user_id = await pg_add_user(view, user_dict )
    return await pg_select_user_by_id (view.pg, user_id)

async def user_edit(view: View,user_dict:dict)->dict:
    if view.request.app['user']['user_id'] == user_dict['user_id'] or view.request.app['user']['role'] == 'admin' :
        if 'columns' in user_dict:
            user_dict['columns']=json.dumps(user_dict['columns'])
        if 'search' in user_dict:
            user_dict['search']=json.dumps(user_dict['search'])
        edit_check = await pg_edit_user(view, user_dict )
        if edit_check:
            return await pg_select_user_by_id (view.pg, user_dict['user_id'])
    else: web.HTTPUnauthorized()

async def model_add(view:View, model_dict:dict)->dict:
    logging.info(model_dict)
    model = await pg_add_model(view, model_dict)
    output =await pg_check_model(view, model)
    return output['output']

async def model_edit(view:View, model_dict: dict)->dict:    
    if 'power' in model_dict: model_dict['power']=int(model_dict['power'])
    edit_check = await pg_edit_model(view, model_dict )
    if edit_check:
        output = await pg_check_model(view, model_dict['model'])
        return output['output']


async def device_add(view: View,input_dict:dict)->dict:
    device_dict = await normalize_device_dict(view,input_dict)
    logging.info(device_dict)
    dev_id = await pg_add_device(view, device_dict )
    output=await pg_check_device(view, 'dev_id', dev_id)
    return output['output']

async def device_edit(view: View,input_dict:dict)->dict:
    full_device_dict = await normalize_device_dict(view,input_dict)
    device_dict = {param:full_device_dict[param] \
                    for param in full_device_dict \
                    if param in input_dict}
    device_dict['dev_id']=input_dict['dev_id']
    edit_check = await pg_edit_device(view, device_dict )
    output = await pg_check_device(view, 'dev_id', input_dict['dev_id'])
    return output['output']

async def normalize_device_dict(view,device_dict):
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
        check = await pg_check_model(view, device_dict['model'])
        model=check['output']
        if not check['status']:
            new_model={
                'model':device_dict['model'],
                'rec_ios':'none',
                'power':0}
            if 'rec_ios' in device_dict:
                new_model['rec_ios']=device_dict['rec_ios']
            if 'power' in device_dict:
                new_model['power']=device_dict['power']
            model= await model_add(view,new_model)
        device_dict['model_id']=model['model_id']
    for param in device_dict:
        if param in def_device: def_device[param]=device_dict[param]
    def_device['in_date']=datetime.datetime.strptime(def_device['in_date'],"%d.%m.%Y")
    return def_device

async def snmp_info(view:View, ip_list):
    '''  
    Takes list of IP return device info with SNMP 
    In example - [{"id": 2, "ip":"xxx.xxx.xxx.xxx"}]
    Out example - [{"id": 2, "hostname": str, "model": str, "dev_ios": str, "serial_n": str}]
    '''
    snmp_community=os.environ['SNMP_COMMUNITY']
    if snmp_community:
        info_list = await snmp_gathering(ip_list,snmp_community)
        output=list()
        for record in info_list:
            if record['status']:
                del (record['output']['manufacturer'])
                if not 'stack' in record['output']:
                    output.append(await device_edit(view,record['output']))
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
                            output.append(await device_edit(view,stack_device))
                        else: 
                            stack_device['ip']='stack'
                            db_device=await pg_check_device(view,'hostname',stack_device['hostname'])
                            if db_device['status']:
                                stack_device['dev_id']=db_device['output']['dev_id']
                                output.append(await device_edit(view,stack_device))
                            else:
                                db_device=await pg_check_device(view,'dev_id',record['output']['dev_id'])
                                for param in stack_device:
                                    db_device['output'][param]=stack_device[param]
                                output.append(await device_edit(view,db_device['output']))
            else: 
                logging.error(record['output'])
                raise web.HTTPBadRequest(record['output'])
        return output
    else: 
        logging.error('No SNMP community')
        raise web.HTTPBadRequest('No SNMP community')
