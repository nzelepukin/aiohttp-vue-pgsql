import json,datetime
from marshmallow import Schema, fields
from marshmallow.validate import Range, Length, ValidationError

class RequestLogin(Schema):
    username = fields.Str(validate=Length(1,256),required=True)
    password = fields.Str(validate=Length(1,256),required=True)

class RequestAddUser(Schema):
    username = fields.Str(validate=Length(1,256),required=True)
    password = fields.Str(validate=Length(1,256),required=True)
    role = fields.Str(validate=Length(1,256),required=True)


class RequestEditUser(Schema):
    password = fields.Str(validate=Length(1,256),required=False)
    role = fields.Str(validate=Length(1,256),required=False)
    firstname = fields.Str(validate=Length(1,256),required=False)
    lastname = fields.Str(validate=Length(1,256),required=False)
    email = fields.Str(validate=Length(1,256),required=False)

class RequestChangePass(Schema):
    password = fields.Str(validate=Length(1,256),required=True)

class RequestDeleteUser(Schema):
    username = fields.Str(validate=Length(1,256),required=True)

class RequestAddModel(Schema):
    model = fields.Str(validate=Length(1,256),required=True)
    rec_ios = fields.Str(validate=Length(1,256),required=True)
    power = fields.Int(validate=Range(0,2000),required=True)    

class RequestEditModel(Schema):
    model_id = fields.Int(validate=Range(0,1000000),required=True)
    model = fields.Str(validate=Length(1,256),required=False)
    rec_ios = fields.Str(validate=Length(1,256),required=False)
    power = fields.Int(validate=Range(0,2000),required=False) 

class RequestAddDevice(Schema):
    hostname = fields.Str(validate=Length(1,256),required=False)
    serial_n = fields.Str(validate=Length(1,256),required=False)
    dev_ios = fields.Str(validate=Length(1,256),required=False)
    inv_n = fields.Str(validate=Length(1,256),required=False)
    nom_n = fields.Str(validate=Length(1,256),required=False)
    description = fields.Str(validate=Length(1,256),required=False)
    ip = fields.Str(validate=Length(1,256),required=False)
    power_type = fields.Str(validate=Length(1,256),required=False)
    protocol = fields.Str(validate=Length(1,256),required=False)
    switch_type = fields.Str(validate=Length(1,256),required=False)
    place = fields.Str(validate=Length(1,256),required=False)
    building = fields.Str(validate=Length(1,256),required=False)
    room = fields.Str(validate=Length(1,256),required=False)
    model_id = fields.Str(validate=Length(1,256),required=False) 
    project = fields.Str(validate=Length(1,256),required=False) 
    in_date = fields.Str(validate=Length(1,256),required=False)
    model = fields.Str(validate=Length(1,256),required=False)
    rec_ios = fields.Str(validate=Length(1,256),required=False)
    power = fields.Int(validate=Range(0,2000),required=False)    

class RequestEditDevice(Schema):
    dev_id = fields.Int(validate=Range(0,1000000),required=True)
    hostname= fields.Str(validate=Length(1,256),required=False)
    serial_n= fields.Str(validate=Length(1,256),required=False)
    dev_ios= fields.Str(validate=Length(1,256),required=False)
    inv_n= fields.Str(validate=Length(1,256),required=False)
    nom_n= fields.Str(validate=Length(1,256),required=False)
    description= fields.Str(validate=Length(1,256),required=False)
    ip= fields.Str(validate=Length(1,256),required=False)
    power_type= fields.Str(validate=Length(1,256),required=False)
    protocol= fields.Str(validate=Length(1,256),required=False)
    switch_type= fields.Str(validate=Length(1,256),required=False)
    place= fields.Str(validate=Length(1,256),required=False)
    building= fields.Str(validate=Length(1,256),required=False)
    room= fields.Str(validate=Length(1,256),required=False)
    model_id= fields.Str(validate=Length(1,256),required=False) 
    project= fields.Str(validate=Length(1,256),required=False) 
    in_date= fields.Str(validate=Length(1,256),required=False)
    model = fields.Str(validate=Length(1,256),required=False)
    rec_ios = fields.Str(validate=Length(1,256),required=False)
    power = fields.Int(validate=Range(0,2000),required=False)  
