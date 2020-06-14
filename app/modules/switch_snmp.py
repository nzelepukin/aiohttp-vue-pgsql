import asyncio
import aiosnmp


async def snmp_get_info(device: dict, com: str, sem)->dict:
    async with sem:
        manufacturer_oid = '.1.3.6.1.2.1.1.2.0'
        stack_oid='.1.3.6.1.2.1.47.1.3.3.1.1.1'
        oid_dict = {
            '9':{
                'manufacturer':'Cisco',
                'hostname': '.1.3.6.1.2.1.1.5.0',
                'model': '.1.3.6.1.2.1.47.1.1.1.1.13',
                'serial_n': '.1.3.6.1.2.1.47.1.1.1.1.11',
                'dev_ios': '.1.3.6.1.4.1.9.2.1.73.0'
                },
            '25506':{
                'manufacturer':'HP',
                'hostname': '.1.3.6.1.2.1.1.5.0',
                'model': '.1.3.6.1.2.1.47.1.1.1.1.13',
                'serial_n': '.1.3.6.1.2.1.47.1.1.1.1.11',
                'dev_ios': '.1.3.6.1.2.1.1.1.1.10.2'
                },
            '4229':{
                'manufacturer':'Nateks',
                'hostname': '.1.3.6.1.2.1.1.5.0',
                'model': '.1.3.6.1.4.1.4229.21.9.225.1.3.0',
                'serial_n': '.1.3.6.1.4.1.4229.21.9.225.1.2.0',
                'dev_ios': '.1.3.6.1.4.1.4229.21.9.225.1.9.0'
                },
            '14885':{
                'manufacturer':'Polygon',
                'hostname': '.1.3.6.1.2.1.1.5.0',
                'model': '.1.3.6.1.2.1.47.1.1.1.1.13',
                'serial_n': '.1.3.6.1.2.1.47.1.1.1.1.11',
                'dev_ios': '.1.3.6.1.4.1.9.2.1.73.0'
                }
            }
        try:
            with aiosnmp.Snmp(host=device['ip'], port=161, community=com) as snmp:
                result={'dev_id':device['dev_id']}
                manufacturer = await snmp.get(manufacturer_oid)
                manufacturer=manufacturer[0].value.strip().split('.')[7]
                if manufacturer in oid_dict: 
                    result['manufacturer']=oid_dict[manufacturer]['manufacturer']
                    hostname = await snmp.get(oid_dict[manufacturer]['hostname'])
                    hostname = hostname[0].value.decode(encoding='UTF-8').strip()
                    if hostname.find('.')>1: result['hostname']=hostname.split('.')[0]
                    else: result['hostname']=hostname
                    stack = await snmp.bulk_walk(stack_oid)
                    stack = [record.value for record in stack]
                    if not stack[0]:
                        model = await snmp.bulk_walk(oid_dict[manufacturer]['model'])
                        result['model'] = model[0].value.strip().decode(encoding='UTF-8')
                        serial = await snmp.bulk_walk(oid_dict[manufacturer]['serial_n'])
                        result['serial_n'] = serial[0].value.decode(encoding='UTF-8').strip()
                    elif len(stack)<2:
                        serial = await snmp.get('{}.{}'.format(oid_dict[manufacturer]['serial_n'],stack[0]))
                        result['serial_n'] = serial[0].value.decode(encoding='UTF-8').strip()
                        model = await snmp.get('{}.{}'.format(oid_dict[manufacturer]['model'],stack[0]))
                        result['model'] = model[0].value.decode(encoding='UTF-8').strip()
                    else:
                        if result['manufacturer']=='Cisco' and not result['model'].startswith('WS') and not result['model']=='':
                            serial = await snmp.bulk_walk(oid_dict[manufacturer]['serial_n'])
                            result['serial_n'] = serial[0].value.decode(encoding='UTF-8').strip()
                        else: 
                            serials=list()
                            models=list()
                            for record in stack:
                                serial = await snmp.get('{}.{}'.format(oid_dict[manufacturer]['serial_n'],record))
                                print(serial[0].value.decode(encoding='UTF-8').strip())
                                serials.append(serial[0].value.decode(encoding='UTF-8').strip())
                                model = await snmp.get('{}.{}'.format(oid_dict[manufacturer]['model'],record))
                                models.append(model[0].value.decode(encoding='UTF-8').strip())
                            result['serial_n']='-stack-'.join(serials)
                            result['model']='-stack-'.join(models)
                            result['stack']=len(stack)
                    dev_ios = await snmp.get(oid_dict[manufacturer]['dev_ios'])
                    result['dev_ios']=dev_ios[0].value.decode(encoding='UTF-8').strip()
                    if result['manufacturer']=='Cisco': result['dev_ios']=result['dev_ios'][result['dev_ios'].find(':')+1:]
                    return {'status':True,'output':result}
                else: return {'status':False,'output':"No SNMP OIDs for {}".format(device['ip'])}
        except:
            return {'status':False,'output':"Can't get info from {}".format(device['ip'])} 

async def snmp_gathering(device_list:list,com:str)->list:
    '''
    Gather results of async SNMP.
    '''
    sem=asyncio.Semaphore(50)
    coroutines = [snmp_get_info(device,com,sem) for device in device_list]
    tasks= [asyncio.create_task(coroutine) for coroutine in coroutines]
    results = [await task for task in tasks]
    return results

if __name__ == "__main__":
    test_dict=[{'id':1,'ip':'192.168.101.2'}]
    test_com='testme'
    result = asyncio.run(snmp_gathering(test_dict,test_com))
    for each in result:
        print(each)