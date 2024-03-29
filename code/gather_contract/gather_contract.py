import requests
import json
import os 
import time
from datetime import date
from pathlib import Path

PATH = 'Contracts'

def writeContract(contract_addr,bytecode,path,count,type,block,index):
    os.mkdir(path + f'/{count}')
    f = open(path + f'/{count}/code', 'w')
    f.write(bytecode)
    f.close()

    f = open(path + f'/{count}/metadata.txt', 'w')
    f.write('Contract_address: '+contract_addr+'\n')
    f.write('Creation: '+ type+'\n')
    f.write('Block: '+ block+'\n')
    f.write('Index: '+ index+'\n')
    f.write('Source_code: NOK\n')
    f.close()

    return 


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

def update_count(c,path):
	f = open(path + '/count.txt', 'w')
	f.write(f'{c}')
	f.close()

def folder_management(t_date,path,block):
    day_folder = Path(path + '/' + t_date)
    if not day_folder.is_dir():
        os.mkdir(path + '/' + t_date)
        os.mkdir(path + '/' + t_date +'/logs')
        f = open( path + '/' + t_date + '/count.txt', 'w')
        f.write('1')
        f.close()
        f = open( path + '/' + t_date + '/starting.txt', 'w')
        f.write(block)
        f.close()
    return path + '/' + t_date

def analyze_tx_trace(path,path_w,count,block,index):
    new_contracts = 0
    f = open(path)
    line = f.readline()
    block_trace = []
    while line:
        block_trace.append(json.loads(line))
        line = f.readline()

    # remove last item, it has not the same keys
    block_trace.pop()
    op = 0

    for operation in block_trace:
            if operation['opName'] == 'CREATE2' or operation['opName'] == 'CREATE':
                print('Found new contract by internal call !')
                # get program counter 
                pc = operation['pc']+1
                #find next program counter to find contract addr
                contract_addr = 'NONE'
                for i in range(op,len(block_trace)-1):
                    if block_trace[i]['pc'] == pc:
                         contract_addr = block_trace[i]['stack'][-1]
                         break

                if contract_addr == 'NONE':
                     print('Cannot find result of contract deployment')
                
                try:
                    # get byte code
                    r = request_local('eth_getCode',[contract_addr,'latest'])
                    resp = json.loads(r.content)
                    bytecode = resp['result']
                    # write 
                    writeContract(contract_addr,bytecode,path_w,count+new_contracts,'INTERNAL',block,index)
                    new_contracts += 1
                except:
                    print(f'Faulty contract address: {contract_addr}')
                    f2 = open(path_w + f'/logs/{block}-{index}.txt','w')
                    f2.write(json. dumps(block_trace))
                    f2.close()
            op += 1



    f.close()
    os.remove(path)
    return new_contracts

r = request_local('eth_blockNumber',[])
trans = json.loads(r.content)
lastblock = trans['result']
#lastblock = '0x12560bd'

last_date = str(date.today())
path_writting = folder_management(last_date,PATH,hex(int(lastblock,16)+1))

f = open(path_writting + '/count.txt', 'r')
count = int(f.read())
f.close()



while True:
    r = request_local('eth_blockNumber',[])
    trans = json.loads(r.content)
    print('--------------------------------------')
    print('Last block    : ' + trans['result'])
    print('Last analyzed : ' + lastblock)
    # Last block has changed, verify transaction in next block
    if(trans['result']!=lastblock):
        lastblock = hex(int(lastblock,16)+1)
        if last_date != str(date.today()):
            last_date = str(date.today())
            path_writting = folder_management(last_date,PATH,lastblock)
            count = 1
        # only used as information to display
        r = request_local('eth_getBlockTransactionCountByNumber',[lastblock])
        resp = json.loads(r.content)
        block_transaction_nbr = int(resp['result'],16)
        print(f'Transactions in block: {block_transaction_nbr}')
        # get block and all transaction
        r = request_local('eth_getBlockByNumber',[lastblock,True])
        block = json.loads(r.content)
        i = 0
        # ---------search new contract by ordinary addresses
        for transaction in block['result']['transactions']:
            if (transaction['to'] == None):
                print('Found new contract by ordinary !')
                # Get the bytecode
                r = request_local('eth_getTransactionReceipt',[transaction['hash']])
                trans = json.loads(r.content)
                contract_addr =trans['result']['contractAddress']
                r = request_local('eth_getCode',[contract_addr,'latest'])
                trans = json.loads(r.content)
                bytecode = trans['result']
                # Write
                writeContract(contract_addr,bytecode,path_writting,count,'ORDINARY',lastblock,hex(i))
                count += 1
                update_count(count,path_writting)
            i += 1

        # ---------search new contract by internal call
        block_hash = block['result']['hash']
        # write all transaction trace of the block in temp and get their path
        r = request_local('debug_standardTraceBlockToFile',[block_hash])
        path_trace = json.loads(r.content)
        if block_transaction_nbr:
            try:
                i = 0
                for transaction in path_trace['result']:
                    count += analyze_tx_trace(transaction,path_writting,count,lastblock,hex(i))
                    update_count(count,path_writting)
                    i+=1
            except:
                print('Problem with block trace')
                f2 = open(path_writting + f'/logs/b-{lastblock}.txt','w')
                f2.write(json.dumps(path_trace))
                f2.close()
            
    else:
        time.sleep(5)
