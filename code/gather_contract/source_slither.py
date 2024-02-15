import os
from pathlib import Path
import time

PATH = 'Contracts'


def slither_check(path):
    f = open(path + '/count.txt', 'r')
    count = int(f.read())
    f.close()
    new_c = 0
    for i in range(1, count):
        print(f'{i}/{count-1}')
        f = open(path + f'/{i}/metadata.txt', 'r')
        contract_addr = f.readline().split(': ')[1].strip()
        type = f.readline().split(': ')[1].strip()
        block = f.readline().split(': ')[1].strip()
        index = f.readline().split(': ')[1].strip()
        available = f.readline().split(': ')[1].strip()
        f.close()
        if available != 'OK':
            os.chdir(path + f'/{i}')
            os.system(f'slither {contract_addr} --etherscan-only-source-code --etherscan-apikey 7YMUE7AGVFN1YHDYJ991GFHMJ26UAIIX2B --json slither.txt --json-types detectors --exclude-optimization --exclude-informational --exclude-dependencies --exclude-low')
            os.chdir('..')
            os.chdir('..')
            os.chdir('..')
            slither_fold = Path(path + f'/{i}/crytic-export')
            if slither_fold.is_dir():
                new_c += 1
                f = open(path + f'/{i}/metadata.txt', 'w')
                f.write('Contract_address: '+contract_addr+'\n')
                f.write('Creation: ' + type+'\n')
                f.write('Block: ' + block+'\n')
                f.write('Index: ' + index+'\n')
                f.write('Source_code: OK\n')
                f.close()
            time.sleep(1)
                
    return new_c


x = input('Enter a folder to analyze: ')

day_folder = Path(PATH + '/' + str(x))
if not day_folder.is_dir():
    print(PATH + '/' + str(x)+' is not in database')
else:
    print('New contracts sources: ' + str(slither_check(PATH + '/' + str(x))))
