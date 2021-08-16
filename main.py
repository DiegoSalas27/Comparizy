import time
from tecnologia import *

if __name__ == '__main__':
    while True:

        find_products_tecnologia_computadoras_saga()
        #find_products_tecnologia_tablets_saga() No lo vamos usar pero lo dejamos por si acaso
        find_products_tecnologia_televisoresOLED_Saga()
        find_products_tecnologia_televisoresQLED_Saga()
        find_products_electrohogar_refigeradoras_saga()
        find_products_electrohogar_lavadoras_saga()
        find_products_electrohogar_secadoras_saga()
        find_products_electrohogar_cocinadepie_saga()
        find_products_tecnologia_computadoras_ripley()
        #find_products_tecnologia_tablets_ripley()
        find_products_tecnologia_televisoresOLED_Ripley()
        find_products_tecnologia_televisoresQLED_Ripley()
        find_products_electrohogar_refigeradoras_Ripley()
        find_products_electrohogar_lavadoras_Ripley()
        find_products_electrohogar_secadoras_Ripley()
        find_products_electrohogar_cocinadepie_Ripley()
        find_products_tecnologia_computadoras_oeschle()
        #find_products_tecnologia_tablets_oeschle()
        find_products_tecnologia_televisoresOLED_oeschle()
        find_products_tecnologia_televisoresQLED_oeschle()
        find_products_electrohogar_refigeradoras_oeschle()
        find_products_electrohogar_lavadoras_oeschle()
        find_products_electrohogar_secadoras_oeschle()
        find_products_electrohogar_cocinadepie_oeschle()
        time_wait = 1440
        print(f'Waiting {time_wait} minutes...')
        time.sleep(time_wait * 60) #run program every day\