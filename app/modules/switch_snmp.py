import asyncio
import aiosnmp


async def snmp_get_info(ip: str, com: str, sem)->dict:
    async with sem:
        oid = {
        'hostname': '.1.3.6.1.4.1.9.2.1.3.0',
        'model': '.1.3.6.1.2.1.47.1.1.1.1.13',
        'serial': '.1.3.6.1.2.1.47.1.1.1.1.11',
        'dev_ios': '.1.3.6.1.4.1.9.2.1.73.0'
        }
        with aiosnmp.Snmp(host=ip, port=161, community=com) as snmp:
            result={'ip':ip}
            hostname = await snmp.get(oid['hostname'])
            result['hostname'] = hostname[0].value.decode(encoding='UTF-8')
            model = await snmp.bulk_walk(oid['model'])
            result['model'] = model[0].value.strip().decode(encoding='UTF-8')        
            serial = await snmp.bulk_walk(oid['serial'])
            result['serial'] = serial[0].value.decode(encoding='UTF-8')
            dev_ios = await snmp.get(oid['dev_ios'])
            result['dev_ios']=dev_ios[0].value.decode(encoding='UTF-8').replace('flash:','')
            return result

async def snmp_gathering(ip_list:list,com:str)->list:
    '''
    Gather results of async SNMP.
    '''
    sem=asyncio.Semaphore(50)
    coroutines = [snmp_get_info(ip,com,sem) for ip in ip_list]
    tasks= [asyncio.create_task(coroutine) for coroutine in coroutines]
    results = [await task for task in tasks]
    return results