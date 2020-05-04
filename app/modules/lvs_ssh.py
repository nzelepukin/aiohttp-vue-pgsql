import netdev,time,asyncio,socket,os
from getpass import getpass


def TCP_connect(ip:str, port:int, delay:float):
    '''
    Checks if port is open return True else False
    '''
    TCPsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPsock.settimeout(delay)
    try:
        TCPsock.connect((ip,port))
        return True
    except:
        print('Port {} closed on {}'.format(port,ip))
        return False


async def sshing(ip:str,user:str,passwd:str,cmd_list:list,sem)->list:
    '''
    SSH to IP with USER and PASSWORD uses transform to give IP and MASK VLAN 50
    '''
    async with sem:
        try:

            async with netdev.create(host=ip,device_type='cisco_ios',username=user,password=passwd) as ios:
                output =[await ios.send_command(cmd, strip_command=True) for cmd in cmd_list]
            result = [[string for string in command.split('\n') if not string.strip()==''] for command in output]
            return {'ip':ip,'output':result}
        except:
            print ('-=WARNING=- Cant connect to device. PLEASE CHECK USERNAME,HOSTNAME,COMMAND '+ip) 
            return {'ip':ip,'output':['Device reachable, 22 port opened but cant connect. Probably wrong username or password']}

async def ssh_gathering(ip_list:list, user:str, passwd:str, ssh_cmd:list)->list:
    '''
    Gather results of async SSHing.
    '''
    sem=asyncio.Semaphore(50)
    coroutines = [sshing(ip,user,passwd,ssh_cmd,sem) for ip in ip_list]
    tasks= [asyncio.create_task(coroutine) for coroutine in coroutines]
    results = [await task for task in tasks]
    return results

async def start_ssh(cmd_list:list,user: str, passwd:str, ip_list:str)->list:
    '''
    Starts gather info from IPs in inventory file via SSH.
    '''
    ip_dict={'unreachable':[],'ssh':[],'telnet':[]}
    ip_list=[ip for ip in ip_list if ip.rstrip()!='']
    for ip in ip_list:
        if TCP_connect(ip,22,0.7): ip_dict['ssh'].append(ip)
        elif TCP_connect(ip,23,0.7): ip_dict['telnet'].append({'ip':ip, 'output':[['Cant work, only telnet enabled']]})
        else: ip_dict['unreachable'].append({'ip':ip, 'output':[['Cant work, no telnet or ssh']]})
    print ('Getting information from hosts via SSH - STARTED')
    results = await ssh_gathering(ip_dict['ssh'], user, passwd,cmd_list)
    print ('Getting information from hosts via SSH - DONE')
    return results+ip_dict['telnet']+ip_dict['unreachable'] 
