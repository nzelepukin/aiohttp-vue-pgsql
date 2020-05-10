import json,datetime
from marshmallow import Schema, fields
from marshmallow.validate import Range, Length, ValidationError

class NewSwitchSchema(Schema):
    id =fields.Int(validate=Range(0,100000),required=True)
    hostname = fields.Str(validate=Length(0,50))
    serial_n = fields.Str(validate=Length(1,30))
    dev_ios = fields.Str(validate=Length(0,100))
    inv_n = fields.Str(validate=Length(0,30))
    nom_n = fields.Str(validate=Length(0,30))
    project = fields.Str(validate=Length(0,100))
    in_date = fields.DateTime('%d.%m.%Y')
    model = fields.Str(validate=Length(0,50))
    place = fields.Str(validate=Length(0,50))
    building = fields.Str(validate=Length(0,50))
    room = fields.Str(validate=Length(0,50))
    ip = fields.Str(validate=Length(0,15))
    protocol = fields.Str(validate=Length(0,15))
    description = fields.Str(validate=Length(0,100))
    power_type = fields.Str(validate=Length(0,30))
    device_type = fields.Str(validate=Length(0,30))
    power = fields.Int(validate=Range(0,10000))

def check_params(device):
    try:
        device = check_type(device)
        NewSwitchSchema().loads(json.dumps(device))
        return {'status': True,'output': device}
    except ValidationError as err:
        return {'status': False,'output':[field for field in err.messages]}

def check_type( params ):
    output=dict()
    for param in params:
        if not params[param] in ['none','']:
            if param in ['power','id']: output[param]=int(params[param])
            else: output[param]=str(params[param])
    return output
