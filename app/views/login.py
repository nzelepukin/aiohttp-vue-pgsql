import os, logging
from aiohttp.web_exceptions import HTTPNotFound
from http import HTTPStatus
from aiohttp.web_urldispatcher import View
from asyncpgsa import PG
from aiohttp.web_response import Response
from marshmallow.validate import ValidationError
from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import session_middleware, setup, get_session, new_session
from modules.schema import RequestLogin
from modules.auth import login_required
from database import pg_select_user_by_id
from database import pg_add_user, pg_edit_user, pg_delete_user, pg_check_user

class Login(View):
    URL_PATH = r'/login'

    @property
    def pg(self) -> PG:
        return self.request.app['pg']
    
    @request_schema(RequestLogin())
    @docs(summary='Проверка пользователя при логине')
    async def post(self):
        form = self.request['data']
        user_signature={'username': form['username'],'password':form['password']}
        print (user_signature)
        user_id = await pg_check_user(self, user_signature )
        if user_id['status']:
            # Always use `new_session` during login to guard against
            # Session Fixation. See aiohttp-session#281
            session = await new_session(self.request)
            session['user_id'] = user_id['output']
            url='http://{}/index.html'.format(os.environ['NGINXHOST'])
            print(url)
            return web.HTTPFound(url)
        else:
            raise web.HTTPUnauthorized(reason='User not found')
        

class Logout(View):
    URL_PATH = r'/logout'

    @property
    def pg(self) -> PG:
        return self.request.app['pg']

    @docs(summary='Logout')
    @login_required
    async def get(self):
        session = await get_session(self.request)
        logging.info('User {} logged out'.format(session['user_id']))
        del(session['user_id'])
        return web.HTTPFound("http://{}/login.html".format(os.environ['NGINXHOST']))    
            

