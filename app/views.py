import os
from aiohttp import web, MultipartReader
from database import pg_select_all, pg_add_device,pg_edit_device,pg_delete_device
from modules.lvs_ssh import start_ssh
from modules.switch_snmp import snmp_gathering
from modules.panda_switch import xls_to_base
from modules.checkers import check_params

async def multi_console(request):
    ''' Multi SSH client '''
    cred_dict = await request.json()
    cred_dict['command'] = cred_dict['command'].split('\n')
    cred_dict['ip'] = cred_dict['ip'].split('\n')
    return web.json_response(await start_ssh(cred_dict['command'],cred_dict['username'],cred_dict['password'],cred_dict['ip']), content_type='application/json')

async def switchbase(request):
    ''' take switches info from DB '''
    device_list=pg_select_all()
    return web.json_response(device_list, content_type='application/json')

async def renew_parameters(request):
    '''  
    Takes list of IP return device info with SNMP 
    In example - [{"id": 2, "ip":"xxx.xxx.xxx.xxx"}]
    Out example - [{"id": 2, "hostname": str, "model": str, "dev_ios": str, "serial_n": str}]
    '''
    ip_list = await request.json()
    print (ip_list)
    if os.path.exists('/run/secrets/snmp_community'):
        with open('/run/secrets/snmp_community') as snmp_file:
            snmp_community=snmp_file.read().strip()
    if snmp_community:
        info_list = await snmp_gathering(ip_list,snmp_community)
        result = [edit_device_in_db(record) for record in info_list] 
        return web.json_response(result, content_type='application/json')
    else: 
        return web.json_response('No SNMP community', content_type='application/json')

async def switch_xls(request):
    ''' Upload file from frontend to xls_file_path, parse it using Pandas and add to DB '''
    xls_file_path='modules/xls/file.xls'
    reader = MultipartReader.from_response(request)
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
        result= [device_to_db(record) for record in device_list]
        os.remove(xls_file_path)
        return web.json_response(result, content_type='application/json')
    else: 
        return web.json_response('Error: File NOT created' , content_type='application/json')

async def insert_device(request):
    device = await request.json()
    return web.json_response(device_to_db(device), content_type='application/json')

async def edit_device(request):
    devices = await request.json()
    result = [edit_device_in_db(device) for device in devices]
    return web.json_response(result, content_type='application/json')

async def delete_device(request):
    devices = request.match_info.get('del_string', '0')
    result = [delete_device_from_db(id) for id in devices.split('+')]
    return web.json_response(result, content_type='application/json')

def device_to_db(record):
    record['id']=0
    checked_record=check_params(record)
    output=checked_record['output']
    if checked_record['status']:
        del(output['id'])
        return pg_add_device(**output)
    else:
        return 'Found some errors in fields - '+','.join(output)   

def edit_device_in_db(record):
    checked_record=check_params(record)
    if checked_record['status']:
        return pg_edit_device(checked_record['output'])
    else:
        return 'Found some errors in fields - '+','.join(checked_record['output'])  

def delete_device_from_db(id):
    checked_record=check_params({'id':id})
    if checked_record['status']:
        return pg_delete_device(checked_record['output'])
    else:
        return 'Found some errors in fields - '+','.join(checked_record['output']) 
