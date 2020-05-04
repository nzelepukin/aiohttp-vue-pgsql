import time,redis,os,datetime
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

class Place(Base):
    __tablename__='SwitchPlace'
    id = Column(Integer, primary_key=True)
    lpu = Column( String(50))
    building = Column( String(50))
    room = Column( String(50))

class Switch(Base):
    __tablename__='SwitchBase'
    id = Column(Integer, primary_key=True)
    hostname = Column( String(50))
    serial_n = Column( String(30))
    dev_ios = Column( String(100))
    inv_n = Column( String(30))
    nom_n = Column( String(30))
    project = Column( String(30))
    in_date = Column(DateTime(timezone=True))
    model_id = Column(Integer, ForeignKey("SwitchModel.id"))
    place_id = Column(Integer, ForeignKey("SwitchPlace.id"))
    ip_id = Column(Integer, ForeignKey("SwitchIp.id"))

class Service(Base):
    __tablename__='SwitchService'
    id = Column(Integer, primary_key=True)
    parameter = Column( String(50))
    value = Column( String(100))

