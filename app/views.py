import os
from aiohttp import web, MultipartReader
from database import pg_select_all, pg_renew_device, pg_add_device,pg_get_snmp
from modules.lvs_ssh import start_ssh
from modules.switch_snmp import snmp_gathering
from modules.panda_switch import xls_to_base

async def multi_console(request):
    cred_dict = await request.json()
    cred_dict['command'] = cred_dict['command'].split('\n')
    cred_dict['ip'] = cred_dict['ip'].split('\n')
    return web.json_response(await start_ssh(cred_dict['command'],cred_dict['username'],cred_dict['password'],cred_dict['ip']), content_type='application/json')

async def switchbase(request):
    switch_list=pg_select_all()
    return web.json_response(switch_list, content_type='application/json')

async def renew_parameters(request):
    ip_list = await request.json()
    if os.path.exists('/run/secrets/snmp_community'):
        with open('/run/secrets/snmp_community') as snmp_file:
            snmp_community=snmp_file.read().strip()
    if snmp_community:
        info_list = await snmp_gathering(ip_list,snmp_community)
        for info in info_list:
            pg_renew_device(info)
        return web.json_response(info, content_type='application/json')
    else: 
        return web.json_response('No SNMP community', content_type='application/json')
        
async def switch_xls(request):
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
        switch_list = xls_to_base(xls_file_path)
        result = [ pg_add_device(record) for record in switch_list]
        os.remove(xls_file_path)
        return web.json_response(result, content_type='application/json')
    else: 
        return web.json_response('Error: File NOT created' , content_type='application/json')