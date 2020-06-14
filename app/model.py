import time,os,datetime

from sqlalchemy import (
    Column, DateTime, ForeignKey, ForeignKeyConstraint, Integer,
    MetaData, String, Table
)

# SQLAlchemy рекомендует использовать единый формат для генерации названий для
# индексов и внешних ключей.
# https://docs.sqlalchemy.org/en/13/core/constraints.html#configuring-constraint-naming-conventions
convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',
    'pk': 'pk__%(table_name)s'
}

metadata = MetaData(naming_convention=convention)

model_table = Table (
    'device_models',
    metadata,
    Column('model_id', Integer, autoincrement=True, unique=True, primary_key=True),
    Column('model', String, nullable=False, unique=True),
    Column('rec_ios', String, nullable=False),
    Column('power', Integer, nullable=False)
)  

base_table = Table(
    'device_base',
    metadata,
    Column('dev_id', Integer, autoincrement=True, unique=True, primary_key=True),
    Column('hostname', String, nullable=False),
    Column('serial_n', String, nullable=False),
    Column('dev_ios', String, nullable=False),
    Column('inv_n', String, nullable=False),
    Column('nom_n', String, nullable=False),
    Column('description', String, nullable=False),
    Column('ip', String, nullable=False),
    Column('power_type', String, nullable=False),
    Column('protocol', String, nullable=False),
    Column('switch_type', String, nullable=False),
    Column('place', String, nullable=False),
    Column('building', String, nullable=False),
    Column('room', String, nullable=False),
    Column('model_id', Integer, ForeignKey('device_models.model_id')), 
    Column('project', String, nullable=False), 
    Column('in_date', DateTime(timezone=True), nullable=False)
)

user_table = Table(
    'device_user',
    metadata,
    Column('user_id', Integer, autoincrement=True, primary_key=True),
    Column('username', String, nullable=False, unique=True),
    Column('password', String, nullable=False),
    Column('role', String, nullable=False),
    Column('firstname', String),
    Column('lastname', String),
    Column('email', String)
)