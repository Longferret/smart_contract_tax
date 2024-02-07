import requests
import json
from datetime import date
from datetime import timedelta
from pathlib import Path

PATH = 'Contracts'
ETHERSCAN_KEY = ''

def source_checker(path):
    f = open(path + '/count.txt','r')
    count = int(f.read())
    f.close()
    new_c = 0
    for i in range(1,count):
        print(f'{i}/{count-1}')
        f = open(path + f'/{i}/metadata.txt')
        contract_addr = f.readline().split(': ')[1].strip()
        type = f.readline().split(': ')[1].strip()
        available = f.readline().split(': ')[1].strip()
        if available != 'OK':
            r = request_eth(contract_addr)
            trans = json.loads(r.content)
            SourceCode = trans['result'][0]['SourceCode']
            CompilerVersion = trans['result'][0]['CompilerVersion']
            ContractName = trans['result'][0]['ContractName']
            new_c += writeContract(contract_addr,SourceCode,CompilerVersion,ContractName,path+f'/{i}',type)
    return new_c

def writeContract(contract_addr,SourceCode,CompilerVersion,ContractName,path,type):

    if SourceCode:

        f = open(path + '/metadata.txt', 'w')
        f.write('Contract_address: '+contract_addr+'\n')
        f.write('Creation: '+ type+'\n')
        f.write('Source_code: OK\n')
        f.write('Contract Name: '+ContractName+'\n')
        f.write('Compiler version: '+CompilerVersion+'\n')
        f.close()

        f = open(path + '/code.sol', 'w')
        f.write(SourceCode)
        f.close()
        return 1
    return 0

def request_eth(contract_addr):
    url = f'https://api.etherscan.io/api?module=contract&action=getsourcecode&address={contract_addr}&apikey={ETHERSCAN_KEY}'
    r = requests.get(url)
    return r

#Could be usefull
'''
month = month.zfill(2)
day = day.zfill(2)
print(day)

if(td == year +'-'+month+'-'+ day):
    print('MATCH')

exit()
'''

x = input('Enter a past day (1 for yesterday): ')
today = date.today()
past_day = today - timedelta(days = int(x))

day_folder = Path(PATH + '/' + str(past_day))
if not day_folder.is_dir():
    print(PATH + '/' + str(past_day)+' is not in database')
else:
    print('New contracts sources: ' + str(source_checker(PATH + '/' + str(past_day))))
    
