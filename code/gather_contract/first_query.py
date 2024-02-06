from web3 import Web3, HTTPProvider
import requests
import json
import pandas as pd

API_KEY = ""


def request_inf(method,params):
    content = {
    "jsonrpc":"2.0",
    "method": method,
    "params": params,
    "id":1
    }
    url = "https://mainnet.infura.io/v3/" + API_KEY
    payload = json.dumps(content)
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=payload, headers=headers)
    return r


connection = Web3(HTTPProvider('https://mainnet.infura.io/v3/'+ API_KEY))
last_b = hex(connection.eth.block_number)
print ("Latest Ethereum block number", last_b)


first_block = "0x123f1ff"
current_block = first_block
indexes = []
contract_addr = []

while True:
    print("Current block " + current_block)
    r = request_inf("eth_getBlockTransactionCountByNumber",[current_block])
    bnbr = json.loads(r.content)
    indexes.clear()
    contract_addr.clear()

    block_transaction_nbr = int(bnbr['result'],16)

    for i in range(block_transaction_nbr):
        r = request_inf("eth_getTransactionByBlockNumberAndIndex",[current_block,hex(i)])
        trans = json.loads(r.content)
        print(f"index {i} on {block_transaction_nbr}")
        if (trans['result']['to'] == None):
            indexes.append(hex(i))
            r = request_inf("eth_getTransactionReceipt",[trans['result']['hash']])
            trans = json.loads(r.content)
            contract_addr.append(trans["result"]["contractAddress"])
    if indexes:
        dict = {'index': indexes, 'contract_addr': contract_addr} 
        df = pd.DataFrame(dict)
        df.to_csv(f"ETH-{current_block}.csv")
    current_block = hex(int(current_block,16)-1)