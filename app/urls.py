import os
from aiohttp import web
from database import pg_init_db
from views import multi_console, switchbase, renew_parameters, switch_xls, edit_device, insert_device, delete_device, select_models, delete_model, edit_model
  
urls = [
    web.post('/multiconsole/', multi_console),  # - multi SSH client
    web.post('/snmpinfo/', renew_parameters),   # - SNMP get device info
    web.post('/xlstobase/', switch_xls),        # - import existing xls file
    web.get('/switch/', switchbase),            # - take switches from DB
    web.post('/edit-switch/', edit_device),     # - change existing switch record in DB
    web.post('/switch/', insert_device),        # - insert switch record to DB
    web.delete('/switch/{del_string}', delete_device),  # - delete switch record to DB
    web.get('/model/', select_models),                  # - take models from DB
    web.post('/model/', edit_model),                    # - insert model record to DB
    web.delete('/model/{del_string}', delete_model)     # - delete model record to DB    
]
app = web.Application(client_max_size=1024*1024*10)
app.add_routes(urls)

def start_webapp():                 
    pg_init_db()
    web.run_app(app,port=8080)   

if __name__ == '__main__':
    pg_init_db()
    web.run_app(app,port=8080)