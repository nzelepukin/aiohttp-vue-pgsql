import time,aioredis,os,datetime, logging
from asyncpgsa import PG 
from asyncpg import UniqueViolationError
from aiohttp.web_urldispatcher import View
from sqlalchemy import Table, Column,DateTime, Integer, String, Float, LargeBinary, join
from sqlalchemy import exists, select, update, delete, MetaData, ForeignKey, engine, create_engine,Unicode
from sqlalchemy.sql import and_
from model import user_table, base_table, model_table
import logging




async def setup_pg(app) -> PG:
    db_url='postgresql://{}:{}@{}/devices'.format(
        os.environ['POSTGRESUSER'], 
        os.environ['POSTGRESPASS'],
        os.environ['POSTGRESHOST'])
    logging.info('Connecting to POSTGRES database')

    app['pg'] = PG()
    await app['pg'].init(
        str(db_url),
        min_size=1,
        max_size=30
    )
    await app['pg'].fetchval('SELECT 1')
    logging.info('Connected to POSTGRES database')

    try:
        yield
    finally:
        logging.info('Disconnecting from POSTGRES database')
        await app['pg'].pool.close()
        logging.info('Disconnected from POSTGRES database')

async def pg_add_user(view: View, user: dict) ->dict:
    logging.info('BEGIN: Add user '+user['username'])
    try:
        query_insert = user_table.insert().values(**user)
        async with view.pg.transaction() as conn:
            await conn.execute(query_insert) 
        logging.info('FINISH: Add user '+user['username'])
        return {'status':True,'output':'User {} added'.format(user['username'])}
    except UniqueViolationError:
        return {'status':False,'output':'User {} already in base'.format(user['username'])}

async def pg_edit_user(view: View, user):
    id=user['username']
    logging.info('BEGIN: Edit user '+user['username'])
    query = user_table.update().values(
        **user).where( user_table.c.username == id)
    async with view.pg.transaction() as conn:
        await conn.execute(query) 
    logging.info('FINISH: Edit user '+user['username'])
    return {'status':True,'output':'User successfully edited'}

async def pg_delete_user(view: View, username):
    logging.info('BEGIN: Delete user '+username)
    query = user_table.delete().where( user_table.c.username == username)
    query_select = select([user_table]).where(user_table.c.username == username)
    if await view.pg.fetchval(query_select):
        await view.pg.execute(query)
        logging.info('FINISH: Delete user '+username)
        return {'status':True,'output':'User deleted'}
    else: return {'status':False,'output':'No such user in database'}

async def pg_check_user(view:View,user)->dict:
    query = select([
            exists().where(and_(user_table.c.username == user['username'], 
            user_table.c.password == user['password']))
        ])
    query2= select([user_table]).where(
        and_(
            user_table.c.username == user['username'], 
            user_table.c.password == user['password']))
    diag=await view.pg.fetchval(query)
    if not diag: 
        return {'status':False}
    else: 
        output=await view.pg.fetchrow(query2)
        return {'status':True,'output':output[0]}

async def pg_select_user_by_id(pg,user_id):
    query = select([
            exists().where(user_table.c.user_id == user_id)
        ])
    query2= select([user_table]).where(user_table.c.user_id == user_id)
    if not await pg.fetchval(query): output={'status':False}
    else: 
        output=await pg.fetchrow(query2)
        return {'username': output['username'],
                'password': output['password'],
                'role': output['role'],
                'firstname':output['firstname'],
                'lastname':output['lastname'],
                'email':output['email']
                }

async def pg_select_users(view:View)->dict:
    query= select([user_table])
    records=await view.pg.fetch(query)
    output=[ {
        'user_id':record[0],
        'username':record[1],
        'role':record[3],
        'firstname':record[4],
        'lastname':record[5],
        'email':record[6]} for record in records]
    return {'status':True,'output':output}


async def pg_add_model(view: View, model: dict) ->dict:
    logging.info('BEGIN: Add model '+model['model'])
    try:
        query_insert = model_table.insert().values(**model)
        async with view.pg.transaction() as conn:
            await conn.execute(query_insert) 
        logging.info('FINISH: Add model '+model['model'])
        return {'status':True,'output':'Model {} added'.format(model['model'])}
    except UniqueViolationError:
        return {'status':False,'output':'Model {} already in base'.format(model['model'])}

async def pg_edit_model(view: View, model):
    id=model['model_id']
    logging.info('BEGIN: Edit model {}'.format(id)) 
    query = model_table.update().values(
        **model
        ).where( model_table.c.model_id == id)
    async with view.pg.transaction() as conn:
        await conn.execute(query) 
    logging.info('FINISH: Edit model {}'.format(id))
    return {'status':True,'output':'Model successfully edited'}

async def pg_delete_model(view: View, model):
    logging.info('BEGIN: Delete model ()'.format(model))
    query = model_table.delete().where( model_table.c.model_id == model)
    query_select = select([model_table]).where(model_table.c.model_id == model)
    if await view.pg.fetchval(query_select):
        await view.pg.execute(query)
        logging.info('FINISH: Delete model {}'.format(model))
        return {'status':True,'output':'model deleted'}
    else: return {'status':False,'output':'No such model in database'}

async def pg_check_model(view:View,model)->dict:
    query = select([exists().where(model_table.c.model == model)])
    query2= select([model_table]).where(model_table.c.model == model)
    diag=await view.pg.fetchval(query)
    if not diag: 
        return {'status':False}
    else: 
        output=await view.pg.fetchrow(query2)
        return {'status':True,'output':output}

async def pg_select_models(view:View)->dict:
    query= select([model_table])
    records=await view.pg.fetch(query)
    output=[ {
        'model_id':record[0],
        'model':record[1],
        'rec_ios':record[2],
        'power':record[3]} for record in records]
    return {'status':True,'output':output}


async def pg_add_device(view: View, device: dict) ->dict:
    if device['hostname']=='none': device['hostname'] = device['ip']
    logging.info('BEGIN: Add device '+device['hostname'])
    try:
        query_insert = base_table.insert().values(**device)
        async with view.pg.transaction() as conn:
            await conn.execute(query_insert) 
        logging.info('FINISH: Add device '+device['hostname'])
        return {'status':True,'output':'Device {} added'.format(device['hostname'])}
    except:
        return {'status':False,'output':'Device {} already in base'.format(device['hostname'])}

async def pg_edit_device(view: View, device):
    id=device['dev_id']
    logging.info('BEGIN: Edit device {}'.format(id)) 
    query = base_table.update().values(
        **device
        ).where( base_table.c.dev_id == id)
    async with view.pg.transaction() as conn:
        await conn.execute(query) 
    logging.info('FINISH: Edit device {}'.format(id))
    return {'status':True,'output':'Device successfully edited'}

async def pg_delete_device(view: View, device):
    logging.info('BEGIN: Delete device {}'.format(device))
    query = base_table.delete().where( base_table.c.dev_id == device)
    query_select = select([base_table]).where(base_table.c.dev_id == device)
    if await view.pg.fetchval(query_select):
        await view.pg.execute(query)
        logging.info('FINISH: Delete device {}'.format(device))
        return {'status':True,'output':'device deleted'}
    else: return {'status':False,'output':'No such device in database'}

async def pg_check_device(view:View,device)->dict:
    query = select([exists().where(base_table.c.device == device)])
    query2= select([base_table]).where(base_table.c.device == device)
    diag=await view.pg.fetchval(query)
    if not diag: 
        return {'status':False}
    else: 
        output=await view.pg.fetchrow(query2)
        return {'status':True,'output':output}

async def pg_select_devices(view:View)->dict:
    query= select([base_table.join(model_table, base_table.c.model_id == model_table.c.model_id)])
    records=await view.pg.fetch(query)
    output=[ 
        {
            'dev_id':record[0],
            'hostname':record[1],
            'serial_n':record[2],
            'dev_ios':record[3],
            'inv_n':record[4],
            'nom_n':record[5],
            'description':record[6],
            'ip':record[7],
            'power_type':record[8],
            'protocol':record[9],
            'switch_type':record[10],
            'place':record[11],
            'building':record[12],
            'room':record[13],
            'model':record[18],
            'rec_ios':record[19],
            'power':record[20],
            'project':record[15], 
            'in_date':record[16].strftime('%d.%m.%Y')
            } for record in records]
    return {'status':True,'output':output}



