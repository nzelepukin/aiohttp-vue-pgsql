from aiohttp.web_exceptions import HTTPNotFound
from http import HTTPStatus
from aiohttp.web_urldispatcher import View
from asyncpgsa import PG
from aiohttp.web_response import Response
from marshmallow.validate import ValidationError
from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import session_middleware, setup, get_session, new_session
from modules.schema import RequestAddUser, RequestChangePass, RequestDeleteUser
from database import pg_select_user_by_id
from database import pg_add_model, pg_edit_model, pg_delete_model, pg_select_models
from modules.auth import login_required, admin_required
from modules.schema import RequestAddModel,RequestEditModel
import logging

class Dev_model(View):
    URL_PATH = r'/model'

    @property
    def pg(self) -> PG:
        return self.request.app['pg']

    @docs(summary='Выбрать модели устройств из базы')
    @login_required 
    async def get(self):
        output = await pg_select_models(self)
        return web.json_response(output['output'], content_type='application/json')

    @request_schema(RequestAddModel())
    @docs(summary='Добавить модель в базу')
    @login_required 
    async def post(self):
        model_dict = await self.request.json()
        logging.info(model_dict)
        output = await pg_add_model(self, model_dict )
        return web.json_response(output, content_type='application/json')
    
    @request_schema(RequestEditModel())
    @docs(summary='Редактировать модели устройств')
    @admin_required 
    async def patch(self):
        model_dict = await self.request.json()
        if 'power' in model_dict: model_dict['power']=int(model_dict['power'])
        output = await pg_edit_model(self, model_dict )
        return web.json_response(output, content_type='application/json')  

    @docs(summary='Удалить модели устройств')
    @admin_required 
    async def delete(self):
        models = self.request.match_info.get('del_string', '0')
        logging.info(models)
        output = [await pg_delete_model(self,int(id) ) for id in models.split('+')]
        return web.json_response(output, content_type='application/json') 
