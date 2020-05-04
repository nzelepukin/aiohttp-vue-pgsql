import os
from aiohttp import web
from database import pg_init_db,pg_set_snmp
from views import multi_console, switchbase, renew_parameters, switch_xls
  
urls = [
    web.post('/multiconsole/', multi_console),
    web.get('/switch/', switchbase),
    web.post('/snmpinfo/', renew_parameters),
    web.post('/xlstobase/', switch_xls)
]
app = web.Application(client_max_size=1024*1024*10)
app.add_routes(urls)

def start_webapp():
    pg_init_db()
    web.run_app(app,port=8080)   

if __name__ == '__main__':
    pg_init_db()
    web.run_app(app,port=8080)