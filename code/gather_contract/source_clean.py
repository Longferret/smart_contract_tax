import json
import os 
from pathlib import Path

PATH = ""

def writeCode(path,name,code):
    f = open(path + '/' + name, 'w')
    f.write(code)
    f.close()
    return 

def clean_source(path):
    print(path + '/code.sol')
    sol_file = Path(path + '/code.sol')
    if not sol_file.is_file():
        return

    f = open(path + '/code.sol')
    bad_code = f.read()
    f.close()
    if bad_code[:2] == '{{':
        dict = json.loads(bad_code[1:-1])
        if dict['language'] == 'Solidity':
            print("Found solidity file to cleanup !")
            for a in dict['sources']:
                writeCode(path,a.split('/')[-1],dict['sources'][a]['content'])
            
            writeCode(path,"solSettings.txt",str(dict['settings']))
            os.remove(path + "/code.sol")
    return


f = open(PATH + '/count.txt','r')
count = int(f.read())
f.close()
for i in range(1,count):
    clean_source(PATH + f'/{i}')

    
