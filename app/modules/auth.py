import os
from aiohttp import web
from aiohttp_session import session_middleware, setup, get_session, new_session
from database import setup_pg, pg_check_user, pg_select_user_by_id
from aiohttp.web_middlewares import middleware

def login_required(fn):
    async def wrapped(view, *args, **kwargs):
        print('authorization started')
        session = await get_session(view.request)
        if 'user_id' not in session:
            print('User_id not in session')
            return web.HTTPFound('http://{}/login.html'.format(os.environ['NGINXHOST']))
        user_id = session['user_id']
        print(user_id)
        # actually load user from your database (e.g. with aiopg)
        user = await pg_select_user_by_id(view.request.app['pg'], user_id)
        view.request.app['user'] = user
        return await fn(view, *args, **kwargs)
    return wrapped

def admin_required(fn):
    async def wrapped(view, *args, **kwargs):
        print('Admin authorization started')
        session = await get_session(view.request)
        if 'user_id' not in session:
            return web.HTTPFound('http://{}/login.html'.format(os.environ['NGINXHOST']))
        user_id = session['user_id']
        # actually load user from your database (e.g. with aiopg)
        user = await pg_select_user_by_id(view.request.app['pg'], user_id)
        print (user)
        if user['role']!='admin' :
            return web.HTTPFound('http://{}/login.html'.format(os.environ['NGINXHOST']))
        view.request.app['user'] = user
        return await fn(view, *args, **kwargs)
    return wrapped