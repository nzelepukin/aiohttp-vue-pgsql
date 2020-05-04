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
from model import IPbase, Model, Place, Switch, Service
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def pg_init_db()->None:
    ''' Set default values for tables Places, Model, Ip if they doesnt exist'''
    session=Session()
    if not session.query(IPbase).filter(IPbase.ipaddr=='none').scalar():
        db_ip = IPbase( ipaddr='none')
        session.add(db_ip)
    if not session.query(Model).filter(Model.model=='none').scalar():
        db_model = Model(model='none', ios='none')
        session.add(db_model)
    if not session.query(Place).filter(Place.lpu=='none').scalar():    
        db_place =  Place(lpu = 'none', building='none', room='none')
        session.add(db_place) 
    session.commit()
    session.close()

def pg_wipe_db()->None:
    Base.metadata.drop_all(engine)

def pg_add_ip(ip_list:list)->None:
    ''' Add IP addresses to base and create switches with no parameters except ip '''
    session = Session()
    db_place = session.query(Place).filter(Place.lpu=='none').one()
    db_model = session.query(Model).filter(Model.model=='none').one()
    for ip in ip_list:
        session.add(IPbase(ipaddr=ip))
        session.commit 
        db_ip = session.query(IPbase).filter(IPbase.ipaddr==ip).one()
        db_switch = Switch( 
            hostname = 'none',
            serial_n = 'none',
            dev_ios = 'none',
            inv_n = 'none',
            nom_n = 'none',
            project = 'none',
            in_date = time.ctime(),
            model_id = db_model.id,
            place_id = db_place.id,
            ip_id = db_ip.id )
        session.add(db_switch)
        session.commit()
        session.close()

def pg_add_device(device_dict:dict)->str:
    ''' Get dict with parameters of device and create new device record in Postgres DB '''
    session = Session()
    if not session.query(Switch).filter(Switch.serial_n==str(device_dict['serial'])).scalar():
        if not session.query(IPbase).filter(IPbase.ipaddr==device_dict['ip']).scalar():
            session.add(IPbase(ipaddr=str(device_dict['ip'])))
            session.commit 
        db_ip = session.query(IPbase).filter(IPbase.ipaddr==device_dict['ip']).one()
        if not session.query(Model).filter(Model.model==device_dict['model']).scalar():
            session.add(Model(model=str(device_dict['model']), ios=str(device_dict['ios'])))
            session.commit   
        db_model = session.query(Model).filter(Model.model==device_dict['model']).one()
        if not session.query(Place).filter(Place.lpu==device_dict['place'] and Place.building==device_dict['building']).scalar():
            session.add(Place(lpu=str(device_dict['place']), building=str(device_dict['building']), room=str(device_dict['room'])))
            session.commit         
        db_place = session.query(Place).filter(Place.lpu==device_dict['place'] and Place.building==device_dict['building']).one()
        db_switch = Switch( 
            hostname = str(device_dict['hostname']),
            serial_n = str(device_dict['serial']),
            dev_ios = device_dict['ios'],
            inv_n = 'none',
            nom_n = 'none',
            project = 'none',
            in_date = time.ctime(),
            model_id = db_model.id,
            place_id = db_place.id,
            ip_id = db_ip.id )    
        session.add(db_switch)
        session.commit()
        session.close()
        return 'Added new device S/N - {}'.format(device_dict['serial'])
    else:
        return 'Failed to add device S/N {} its allready in base'.format(device_dict['serial'])

def pg_renew_device(device_dict:dict)->None:
    session = Session()
    try:
        if not session.query(IPbase).filter(IPbase.ipaddr==device_dict['ip']).scalar():
            session.add(IPbase(ipaddr=device_dict['ip']))
            session.commit 
        db_ip = session.query(IPbase).filter(IPbase.ipaddr==device_dict['ip']).one()
        if not session.query(Model).filter(Model.model==device_dict['model']).scalar():
            session.add(Model(model=device_dict['model'], ios=device_dict['dev_ios']))
            session.commit   
        db_model = session.query(Model).filter(Model.model==device_dict['model']).one()
        db_switch = session.query(Switch).filter(Switch.ip_id==db_ip.id).one()
        db_switch.hostname = device_dict['hostname']
        db_switch.serial_n = device_dict['serial']
        db_switch.model_id = db_model.id
        db_switch.dev_ios = device_dict['dev_ios']
        session.commit()
        session.close()
        print ('Renew device with serial number - '+device_dict['serial'])
    except:
        print ('Failed to renew device with serial '+device_dict['serial'])
    
      

def pg_select_all()->dict:
    session = Session()
    result=list()
    db = session.query(Switch).all()
    for switch in db:
        db_ip=session.query(IPbase).filter(IPbase.id==switch.ip_id).one()
        db_model = session.query(Model).filter(Model.id==switch.model_id).one()
        db_place = session.query(Place).filter(Place.id==switch.place_id).one()
        switch_dict = {
            "id": str(switch.id),
            "ip": db_ip.ipaddr,
            "hostname": switch.hostname,
            "model": db_model.model,
            "serial": switch.serial_n,
            "dev_ios": switch.dev_ios,
            #"rec_ios": db_model.ios,
            #"inv_n": switch.inv_n,
            #"nom_n": switch.nom_n,
            #"project": switch.project,
            #"in_date": switch.in_date,
            "place": db_place.lpu,
            "building": db_place.building,
            "room": db_place.room            
            }
        result.append(switch_dict) 
    session.close()   
    return result        
    
def pg_set_snmp(com:str)->str:
    session = Session()
    if session.query(Service).filter(Service.parameter=='snmp_community').scalar():
        db_snmp = session.query(Service).filter(Service.parameter=='snmp_community').one()
        db_snmp.value = com
    else:
        session.add(Service(parameter='snmp_community',value=com))
    session.commit()
    session.close()      
    return 'SNMP community changed'     
    
def pg_get_snmp()->str:
    session = Session()
    if session.query(Service).filter(Service.parameter=='snmp_community').scalar():
        db_snmp = session.query(Service).filter(Service.parameter=='snmp_community').one()
        result = db_snmp.value
    else:
        result = ''
    session.commit()
    session.close()      
    return result

