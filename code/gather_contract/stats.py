import os 

PATH = "Contracts"

contract_nbr = 0
internal = 0
source = 0
for f in os.listdir(PATH):
    current_path = PATH + "/" +f
    co = open(current_path + "/count.txt")
    count = int(co.read())
    for i in range(1,count):
        cont = open(current_path + f"/{i}/metadata.txt")
        contract_addr = cont.readline().split(': ')[1].strip()
        type = cont.readline().split(': ')[1].strip()
        block = cont.readline().split(': ')[1].strip()
        index = cont.readline().split(': ')[1].strip()
        available = cont.readline().split(': ')[1].strip()
        if type == 'INTERNAL':
            internal += 1
        if available == 'OK':
            source += 1
        contract_nbr +=1
        cont.close()
    
    co.close()

print(f'Contracts: {contract_nbr}')
print(f'Source code: {source}')
print(f'Internal: {internal} Ordinary: {contract_nbr-internal}')

    
