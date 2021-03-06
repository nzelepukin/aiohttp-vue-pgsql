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
from devbase_logic import user_add, user_edit
from database import pg_add_user, pg_edit_user, pg_delete_user, pg_check_user
from database import pg_select_users, pg_select_user_by_id
from modules.auth import login_required, admin_required

class User(View):
    URL_PATH = r'/user'

    @property
    def pg(self) -> PG:
        return self.request.app['pg']

    @login_required 
    async def get(self):
        session = await get_session(self.request)
        output={param:self.request.app['user'][param] for param in self.request.app['user'] if not param=='password'}
        return web.json_response(output, content_type='application/json')
    
    @request_schema(RequestEditUser())
    @login_required 
    async def patch(self):
        user_dict = await self.request.json()
        return web.json_response(
            await user_edit(self, user_dict ), 
            content_type='application/json') 


class UserBase(View):
    URL_PATH = r'/userbase'

    @property
    def pg(self) -> PG:
        return self.request.app['pg']

    @admin_required 
    async def get(self):
        return web.json_response(await pg_select_users(self), content_type='application/json')
    
    @request_schema(RequestAddUser())
    @admin_required 
    async def post(self):
        user_signature = await self.request.json()
        return web.json_response(
            await user_add(self, user_signature ), 
            content_type='application/json')

    @request_schema(RequestEditUser())
    @admin_required 
    async def patch(self):
        user_dict = await self.request.json()
        return web.json_response(
            await user_edit(self, user_dict ), 
            content_type='application/json') 

    @admin_required 
    async def delete(self):
        user_id = self.request.match_info.get('del_string', '0')
        output = await pg_delete_user(self, int(user_id) )
        return web.json_response(output, content_type='application/json') 
    