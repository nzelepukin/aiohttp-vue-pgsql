import time,os,datetime
from database import Base
from sqlalchemy import Table, Column,DateTime, Integer, String, Float,LargeBinary, MetaData, ForeignKey, engine, create_engine,Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship

class IPbase(Base):
    __tablename__='SwitchIp'
    id = Column(Integer, primary_key=True)
    ipaddr = Column( String(15))

class Model(Base):
    __tablename__='SwitchModel'
    id = Column(Integer, primary_key=True)
    model = Column( String(50))
    ios = Column( String(100)) 
    power = Column(Integer)   

class Places(Base):
    __tablename__='SwitchPlaces'
    id = Column(Integer, primary_key=True)
    place = Column( String(50))

class Buildings(Base):
    __tablename__='SwitchBuildings'
    id = Column(Integer, primary_key=True)
    building = Column( String(50))

class Rooms(Base):
    __tablename__='SwitchRooms'
    id = Column(Integer, primary_key=True)
    room = Column( String(50))

class SwitchType(Base):
    __tablename__='SwitchType'
    id = Column(Integer, primary_key=True)
    device_type = Column( String(30))

class PowerType(Base):
    __tablename__='SwitchPowerType'
    id = Column(Integer, primary_key=True)
    power_type = Column( String(30))

class Protocol(Base):
    __tablename__='SwitchProtocol'
    id = Column(Integer, primary_key=True)
    protocol = Column( String(10))

class Projects(Base):
    __tablename__='SwitchProjects'
    id = Column(Integer, primary_key=True)
    project = Column( String(100))

class Switch(Base):
    __tablename__='SwitchBase'
    id = Column(Integer, primary_key=True)
    hostname = Column( String(50))
    serial_n = Column( String(30))
    dev_ios = Column( String(100))
    inv_n = Column( String(30))
    nom_n = Column( String(30))
    project_id = Column(Integer, ForeignKey("SwitchProjects.id"))
    in_date = Column(DateTime(timezone=True))
    description = Column( String(100))
    protocol_id = Column(Integer, ForeignKey("SwitchProtocol.id"))
    power_type_id = Column(Integer, ForeignKey("SwitchPowerType.id"))
    type_id = Column(Integer, ForeignKey("SwitchType.id"))
    model_id = Column(Integer, ForeignKey("SwitchModel.id"))
    place_id = Column(Integer, ForeignKey("SwitchPlaces.id"))
    building_id = Column(Integer, ForeignKey("SwitchBuildings.id"))
    room_id = Column(Integer, ForeignKey("SwitchRooms.id"))
    ip_id = Column(Integer, ForeignKey("SwitchIp.id"))

class Service(Base):
    __tablename__='SwitchService'
    id = Column(Integer, primary_key=True)
    parameter = Column( String(50))
    value = Column( String(100))

