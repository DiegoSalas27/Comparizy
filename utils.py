from typing import Any

def scrolldown(number,driver=Any): #improve performance for falabella
    for i in range(0, 13520, 100):
        number = i
        driver.execute_script("window.scrollTo(0, "+str(number)+")")
        time.sleep(0.1)

    