import time
from typing import Any

def scrolldown(number,driver=Any): #improve performance for falabella
    for i in range(0, 13520, 1):
        number = i
        driver.execute_script("window.scrollTo(0, "+str(number)+")")
        time.sleep(0.01)

def scrolldownDepreceted(number,driver=Any):
    driver.execute_script("window.scrollTo(0, "+str(number)+")")
    time.sleep(0.1)
    if int(number) >= 13520:
        return
    scrolldownDepreceted(int(number)+100,driver)
