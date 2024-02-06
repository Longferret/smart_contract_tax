import requests
import json
import os 
import time
from datetime import date
from pathlib import Path

PATH = 'Contrats'
ETHERSCAN_KEY = ''
API_KEY = ''

def writeContract(contract_addr,block,index,bytecode,number,path):
    os.mkdir(path + f'/{number}')
    f = open(path + f'/{number}/code', 'w')
    f.write(bytecode)
    f.close()

    f = open(path + f'/{number}/metadata.txt', 'w')
    f.write('contract address: '+contract_addr+'\n')
    f.write('block number: '+block+'\n')
    f.write('block index: '+index+'\n')
    f.close()

    return 

# Send a request to infura API's
def request_inf(method,params):
    content = {
    'jsonrpc':'2.0',
    'method': method,
    'params': params,
    'id':1
    }
    url = 'https://mainnet.infura.io/v3/' + API_KEY
    payload = json.dumps(content)
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=payload, headers=headers)
    return r

# Send a request to a local ethereum node
def request_local(method,params):
    content = {
    'jsonrpc':'2.0',
    'method': method,
    'params': params,
    'id':1
    }
    url = 'http://localhost:8545'
    payload = json.dumps(content)
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=payload, headers=headers)
    return r

# Send a request to etherscan API's to get source code
def request_eth(contract_addr):
    url = f'https://api.etherscan.io/api?module=contract&action=getsourcecode&address={contract_addr}&apikey={ETHERSCAN_KEY}'
    r = requests.get(url)
    return r

def update_count(c,path):
	f = open(path + '/count.txt', 'w')
	f.write(f'{c}')
	f.close()

def folder_management(t_date):
    day_folder = Path(PATH + '/' + t_date)
    if not day_folder.is_dir():
        os.mkdir(PATH + '/' + t_date)
        f = open( PATH + '/' + t_date + '/count.txt', 'w')
        f.write('1')
        f.close()
    return PATH + '/' + t_date

last_date = str(date.today())
current_path = folder_management(last_date)

f = open(current_path + '/count.txt', 'r')
count = int(f.read())
f.close()

r = request_local('eth_blockNumber',[])
trans = json.loads(r.content)
lastblock = trans['result']

while True:
    r = request_local('eth_blockNumber',[])
    trans = json.loads(r.content)
    print('--------------------------------------')
    print('Last block    : ' + trans['result'])
    print('Last analyzed : ' + lastblock)
    # Last block has changed, verify transaction in next block
    if(trans['result']!=lastblock):
        lastblock = hex(int(lastblock,16)+1)
        r = request_local('eth_getBlockTransactionCountByNumber',[lastblock])
        trans = json.loads(r.content)
        block_transaction_nbr = int(trans['result'],16)
        print(f'Transactions in block: {block_transaction_nbr}')
        for i in range(block_transaction_nbr):
            r = request_local('eth_getTransactionByBlockNumberAndIndex',[lastblock,hex(i)])
            trans = json.loads(r.content)

            # Contract creation transaction found
            if (trans['result']['to'] == None):
                print('Found new contract !')
                # Get the bytecode
                r = request_local('eth_getTransactionReceipt',[trans['result']['hash']])
                trans = json.loads(r.content)
                contract_addr =trans['result']['contractAddress']
                r = request_local('eth_getCode',[contract_addr,'latest'])
                trans = json.loads(r.content)
                ByteCode = trans['result']

                # Verify if day has changed
                if last_date != str(date.today()):
                    last_date = str(date.today())
                    current_path = folder_management(last_date)

                # Write
                writeContract(contract_addr,lastblock,hex(i),ByteCode,count,current_path)
                count += 1
                update_count(count,current_path)
    else:
        time.sleep(5)
