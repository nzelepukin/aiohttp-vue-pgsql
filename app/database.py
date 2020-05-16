import time,redis,os,datetime
from sqlalchemy import Table, Column,DateTime, Integer, String, Float,LargeBinary, MetaData, ForeignKey, engine, create_engine,Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship

try:
    with open('/run/secrets/postgres_user') as usr_file:
        pg_usr=usr_file.read().strip()
    with open('/run/secrets/postgres_password') as pwd_file:
        pg_pwd=pwd_file.read().strip()
    with open('/run/secrets/postgres_db') as db_file:
        pg_db=db_file.read().strip()
except: 
    raise Exception ('Cant find user, password, db secrets.')
db_url='postgres://{}:{}@db-pgsql:5432/{}'.format(pg_usr,pg_pwd,pg_db)
engine=create_engine(db_url,encoding='UTF8')
Base = declarative_base()
metadata = MetaData()
from model import IPbase, Model, Places, Switch, Service, SwitchType, PowerType, Protocol, Buildings, Rooms, Projects
Session = sessionmaker(bind=engine)

def pg_create_db()->None:
    Base.metadata.create_all(engine)

def pg_wipe_db()->None:
    Base.metadata.drop_all(engine)

def pg_init_db()->None:
    ''' Set default values for tables Places, Model, Ip if they doesnt exist'''
    session=Session()
    if not session.query(IPbase).filter(IPbase.ipaddr=='none').scalar():
        db_ip = IPbase( ipaddr='none')
        session.add(db_ip)
    if not session.query(Model).filter(Model.model=='none').scalar():
        db_model = Model(model='none', ios='none', power=0)
        session.add(db_model)
    if not session.query(Places).filter(Places.place=='none').scalar():    
        db_place =  Places(place = 'none')
        session.add(db_place)
    if not session.query(Buildings).filter(Buildings.building=='none').scalar():    
        db_building =  Buildings(building = 'none')
        session.add(db_building)
    if not session.query(Rooms).filter(Rooms.room=='none').scalar():    
        db_room =  Rooms(room = 'none')
        session.add(db_room) 
    if not session.query(SwitchType).filter(SwitchType.device_type=='none').scalar():
        db_device_type =  SwitchType(device_type = 'none')
        session.add(db_device_type)
    if not session.query(PowerType).filter(PowerType.power_type=='none').scalar():
        db_power_type =  PowerType(power_type = 'none')
        session.add(db_power_type)
    if not session.query(Protocol).filter(Protocol.protocol=='none').scalar():
        db_protocol =  Protocol(protocol = 'none')
        session.add(db_protocol)  
    session.commit()
    session.close()

def pg_add_device( 
            hostname = 'none',
            serial_n = 'none',
            dev_ios = 'none',
            inv_n = 'none',
            nom_n = 'none',
            project = 'none',
            in_date = '01.01.1900',
            model = 'none',
            place = 'none',
            building = 'none',
            room = 'none',
            ip = 'none',
            protocol = 'none',
            description = 'none',
            power_type = 'none',
            device_type = 'none',
            power = 0) ->str:
    ''' Get parameters of device and create new device record in Postgres DB '''
    session = Session() 
    db_model = pg_check_model(model, dev_ios, power,session)
    db_project = pg_check_param('Projects','project',project, session)
    db_place = pg_check_param('Places','place',place, session)
    db_building = pg_check_param('Buildings','building',building, session)
    db_room = pg_check_param('Rooms','room',room, session)
    db_ip = pg_check_param('IPbase','ipaddr',ip, session)
    db_device_type = pg_check_param('SwitchType','device_type',device_type, session)
    db_power_type = pg_check_param('PowerType','power_type',power_type, session)
    db_protocol = pg_check_param('Protocol','protocol',protocol, session)
    db_switch = Switch( 
        hostname = hostname,
        serial_n = serial_n,
        dev_ios = dev_ios,
        inv_n = inv_n,
        nom_n = nom_n,
        project_id = db_project.id,
        in_date = datetime.datetime.strptime(in_date,"%d.%m.%Y"),
        description = description,
        protocol_id = db_protocol.id,
        power_type_id = db_power_type.id,
        type_id = db_device_type.id,
        model_id = db_model.id,
        place_id = db_place.id,
        building_id = db_building.id,
        room_id = db_room.id,
        ip_id = db_ip.id )    
    session.add(db_switch)
    session.commit()
    session.close()
    return 'Added new device S/N - {}'.format(serial_n)

def pg_edit_device(params_dict:dict )->None:
    session = Session()
    if session.query(Switch).filter(Switch.id==params_dict['id']).scalar():
        db_switch=session.query(Switch).filter(Switch.id==params_dict['id']).one()
        for param in params_dict:
            if param == 'id': pass
            elif param in ['hostname', 'serial_n', 'dev_ios', 'inv_n', 'nom_n', 'description']:
                setattr(db_switch,param,params_dict[param])
            elif param == 'ip': 
                db_switch.ip_id = pg_check_param('IPbase','ipaddr',params_dict['ip'], session).id
            elif 'model' in params_dict :
                db_switch.model_id = pg_check_model(params_dict['model'], 'none', 0,session).id
            elif param == 'place':
                db_switch.place_id = pg_check_param('Places','place',params_dict['place'], session).id
            elif param == 'building':
                db_switch.building_id = pg_check_param('Buildings','building',params_dict['building'], session).id
            elif param == 'room':
                db_switch.room_id = pg_check_param('Rooms','room',params_dict['room'], session).id
            elif param == 'protocol':
                db_switch.protocol_id = pg_check_param('Protocol','protocol',params_dict['protocol'], session).id
            elif param == 'project':
                db_switch.project_id = pg_check_param('Projects','project',params_dict['project'], session).id
            elif param == 'power_type':
                db_switch.power_type_id = pg_check_param('PowerType','power_type',params_dict['power_type'], session).id
            elif param == 'device_type':
                db_switch.type_id = pg_check_param('SwitchType','device_type',params_dict['device_type'], session).id
        session.commit()
        session.close()
        print ('Renew device with id - {}'.format(params_dict['id']))
    else:
        print ('Failed to renew device, no such id')

def pg_delete_device(params_dict:dict )->None:
    session = Session()
    if session.query(Switch).filter(Switch.id==params_dict['id']).scalar():
        db_switch=session.query(Switch).filter(Switch.id==params_dict['id']).one()
        session.delete(db_switch)
        output = "Device deleted"
    else:
        output = "Can't find this device in base"
    session.commit()
    session.close()
    return output

def pg_select_all()->list:
    session = Session()
    result=list()
    db = session.query(Switch).all()
    for switch in db:
        db_ip=session.query(IPbase).filter(IPbase.id==switch.ip_id).one()
        db_model = session.query(Model).filter(Model.id==switch.model_id).one()
        db_project = session.query(Projects).filter(Projects.id==switch.project_id).one()
        db_place = session.query(Places).filter(Places.id==switch.place_id).one()
        db_building = session.query(Buildings).filter(Buildings.id==switch.building_id).one()
        db_room = session.query(Rooms).filter(Rooms.id==switch.room_id).one()
        db_protocol = session.query(Protocol).filter(Protocol.id==switch.protocol_id).one()
        db_device_type = session.query(SwitchType).filter(SwitchType.id==switch.type_id).one()
        db_power_type = session.query(PowerType).filter(PowerType.id==switch.power_type_id).one()        
        switch_dict = {
            'id': switch.id,
            'protocol': db_protocol.protocol,
            'ip': db_ip.ipaddr,
            'hostname': switch.hostname,
            'model': db_model.model,
            'serial': switch.serial_n,
            'dev_ios': switch.dev_ios,
            'rec_ios': db_model.ios,
            'inv_n': switch.inv_n,
            'nom_n': switch.nom_n,
            'project': db_project.project,
            'in_date': switch.in_date.strftime('%d.%m.%Y'),
            'description': switch.description,
            'power': db_model.power,
            'power_type': db_power_type.power_type,
            'type':db_device_type.device_type,
            'place': db_place.place,
            'building': db_building.building,
            'room': db_room.room            
            }
        result.append(switch_dict) 
    session.close()   
    return result        

def pg_check_param(table,fieldname,value,session):
    if not session.query(eval(table)).filter(eval(table+'.'+fieldname)==value).scalar():
        session.add(eval('{}({}="{}")'.format(table,fieldname,value)))
        session.commit 
    return session.query(eval(table)).filter(eval(table+'.'+fieldname)==value).one()

def pg_check_model(model, dev_ios, power,session):
    if not session.query(Model).filter(Model.model==model).scalar():
        session.add(Model(model=model, ios=dev_ios, power=power))
        session.commit   
    return session.query(Model).filter(Model.model==model).one()

def pg_select_models()->list:
    session = Session()
    db_models = session.query(Model).all()
    output = [{'id':db_model.id, 'model':db_model.model, 'ios':db_model.ios, 'power':db_model.power} for db_model in db_models]
    session.close
    return output


def pg_delete_model(params_dict:dict)->str:
    session = Session()
    if session.query(Model).filter(Model.id==params_dict['id']).scalar():
        db_model=session.query(Model).filter(Model.id==params_dict['id']).one()
        session.delete(db_model)
        output = "Model deleted"
    else:
        output = "Can't find this model in base"
    session.commit()
    session.close()
    return output

def pg_edit_model(params_dict:dict)->str:
    session = Session()
    if session.query(Model).filter(Model.id==params_dict['id']).scalar():
        db_model=session.query(Model).filter(Model.id==params_dict['id']).one()
        for param in params_dict:
            if param== 'model' : db_model.model=params_dict['model']
            if param==  'power': db_model.power=params_dict['power']
            if param == 'ios': db_model.ios=params_dict['ios']
        output = "Model {} {} {} edited".format(db_model.model,db_model.ios,db_model.power)
    else:
        output = "Can't find this model in base"
    session.commit()
    session.close()
    return output

def pg_select_one(param:str,value:str)->dict:
    session = Session()
    if session.query(Switch).filter(eval('Switch.'+param)==value).scalar():
        switch = session.query(Switch).filter(eval('Switch.'+param)==value).one()
        db_ip=session.query(IPbase).filter(IPbase.id==switch.ip_id).one()
        db_model = session.query(Model).filter(Model.id==switch.model_id).one()
        db_project = session.query(Projects).filter(Projects.id==switch.project_id).one()
        db_place = session.query(Places).filter(Places.id==switch.place_id).one()
        db_building = session.query(Buildings).filter(Buildings.id==switch.building_id).one()
        db_room = session.query(Rooms).filter(Rooms.id==switch.room_id).one()
        db_protocol = session.query(Protocol).filter(Protocol.id==switch.protocol_id).one()
        db_device_type = session.query(SwitchType).filter(SwitchType.id==switch.type_id).one()
        db_power_type = session.query(PowerType).filter(PowerType.id==switch.power_type_id).one()        
        switch_dict = {
            'id': switch.id,
            'protocol': db_protocol.protocol,
            'ip': db_ip.ipaddr,
            'hostname': switch.hostname,
            'model': db_model.model,
            'serial_n': switch.serial_n,
            'dev_ios': switch.dev_ios,
            'rec_ios': db_model.ios,
            'inv_n': switch.inv_n,
            'nom_n': switch.nom_n,
            'project': db_project.project,
            'in_date': switch.in_date.strftime('%d.%m.%Y'),
            'description': switch.description,
            'power': db_model.power,
            'power_type': db_power_type.power_type,
            'type':db_device_type.device_type,
            'place': db_place.place,
            'building': db_building.building,
            'room': db_room.room            
            } 
        output={'status':True, 'output':switch_dict}
    else:
        output={'status':False}
    session.close()   
    return output





