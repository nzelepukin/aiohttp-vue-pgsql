from urls import start_webapp
import os

os.environ['REDISHOST']='db-redis'
os.environ['POSTGRESHOST']='db-pgsql'
os.environ['NGINXHOST']='localhost'
os.environ['REDISPASS']='secret'
os.environ['POSTGRESUSER']='admin'
os.environ['POSTGRESPASS']='admin'
os.environ['SNMP_COMMUNITY']='testme'
start_webapp()
