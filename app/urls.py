import os, json, asyncio, logging
from http import HTTPStatus
from functools import partial
from aiohttp import web
from aiohttp_session import session_middleware, setup, get_session, new_session
from aiohttp_session.redis_storage import RedisStorage
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
import aioredis
from database import setup_pg, pg_check_user, pg_select_user_by_id, pg_add_user
from middleware import error_middleware, handle_validation_error
from views.login import Login, Logout
from views.user import User
from views.dev_model import Dev_model
from views.device import Device
from views.utils import Utils, Multiconsole
from modules.auth import login_required, admin_required
#from views import multi_console, switchbase, renew_parameters, switch_xls, edit_device, insert_device, delete_device, select_models, delete_model, edit_model


MAX_UPLOAD_SIZE=1024*1024*10
logging.basicConfig(filename='app.log', 
                    filemode='w',
                    level=logging.DEBUG ,
                    format='%(asctime)s - %(levelname)s - %(message)s')

'''
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
'''

async def make_redis_pool():
    redis_url='redis://r:{}@{}'.format(os.environ['REDISPASS'],os.environ['REDISHOST'])
    print(redis_url)
    return await aioredis.create_redis_pool(
        redis_url,
        minsize=5, 
        maxsize=10, 
        timeout=1) 

def create_app() -> web.Application:
    """
    Создает экземпляр приложения, готового к запуску.
    """
    loop= asyncio.get_event_loop()
    redis_pool= loop.run_until_complete(make_redis_pool())
    storage = RedisStorage(redis_pool)
    logging.info('Connecting to Redis')
    async def dispose_redis_pool(app):
        redis_pool.close()
        await redis_pool.wait_closed()
        logging.info('Disconnecting from Redis')
    app = web.Application(
        client_max_size=MAX_UPLOAD_SIZE,
        middlewares=[error_middleware, validation_middleware])
    setup(app, storage)
    setup_aiohttp_apispec(
                        app=app, 
                        title='Backend API', 
                        swagger_path='/swagger',
                        error_callback=handle_validation_error )
    # Подключение на старте к postgres и отключение при остановке
    app.cleanup_ctx.append(partial(setup_pg))
    app.on_cleanup.append(dispose_redis_pool)
    app.router.add_route('*','/device', Device)
    app.router.add_delete('/device/{del_string}', Device)
    app.router.add_route('*','/model', Dev_model)
    app.router.add_delete('/model/{del_string}', Dev_model)
    app.router.add_post('/login', Login, name='login')
    app.router.add_post('/multiconsole', Multiconsole)
    app.router.add_patch('/snmpinfo', Utils)
    app.router.add_post('/xlstobase', Utils)
    app.router.add_get('/test', Utils)
    app.router.add_get('/logout', Logout)
    app.router.add_route('*','/user', User)
    
    return app

def start_webapp():         
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    start_webapp()
