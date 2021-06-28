import time
from tecnologia import *

if __name__ == '__main__':
    while True:
        #find_products_tecnologia_computadoras()
        find_products_tecnologia_televisores()
        time_wait = 1440
        print(f'Waiting {time_wait} minutes...')
        time.sleep(time_wait * 60) #run program every day\