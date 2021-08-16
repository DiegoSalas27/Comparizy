
from typing import final
from utils import *
from constants import *
from firebase import firebase
from bs4 import BeautifulSoup
import re
import requests
from selenium import webdriver
import time
from datetime import date
import traceback
import sys
import re

firebase = firebase.FirebaseApplication("https://comparizy-test-default-rtdb.firebaseio.com/", None) #test

def find_products_tecnologia_computadoras_saga():
    #procesador, disco duro, memoria y marca. (en vez del modelo)

    #eg: products/grupo-categoria/categoria/subcategoria
    #Trabajamos con constantes (MAYUSCULAS) para evitar problemas de tipado
        
    #Analizar el siguiente detalle de producto como referencia 
    #https://www.falabella.com.pe/falabella-pe/product/882222620/Laptop-Lenovo-81WD00U9US-14-FHD-Core-i5-1035G1,8GB,512GB-SSD,-Platinium-Grey,-Teclado-en-ingles/882222620
    #Se recomienda probar linea por linea haciendo print de cada variable si se necesita comprender el código

    #firebase.delete("/comparizy-test-default-rtdb/products/tecnologia/computadoras/", None)

    #Find saga's products
    #Laptops
    print('Saga products!!!')
    print()

    driver = webdriver.Chrome()
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.falabella.com.pe/falabella-pe/category/cat40712/Laptops')
        scrolldownSaga("0",driver)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')
    # html_text = requests.get('https://www.falabella.com.pe/falabella-pe/category/cat40712/Laptops',timeout=(3.05, 27)).text
    # soup = BeautifulSoup(html_text, 'lxml')
    prueba = soup.find('ol', class_='jsx-1794558402 jsx-1490357007').find_all('li') #Obtener páginas 
    print ('prueba',prueba)
    primerapagina = prueba[0].text  
    ultimapagina = prueba[len(prueba)-1].text 
    print('primera',primerapagina)
    print ('ultima',ultimapagina)
    
    for i in range (int(primerapagina), int(ultimapagina)):
        driver = webdriver.Chrome()
        driver.get("about:blank")
        driver.maximize_window()
        try:
            driver.get('https://www.falabella.com.pe/falabella-pe/category/cat40712/Laptops?page='+ str(i))
            scrolldownSaga("0",driver)
            html = driver.execute_script("return document.body.innerHTML;")
            print("Pagina mostrada")
        except Exception as e:
            print(e)
        finally:
            driver.quit()   
        soup = BeautifulSoup(html,'lxml')

        product_cards = soup.find_all('div', class_='jsx-4221770651 pod') #Obtener todas las filas de productos
        count = 0
        product_name = ''
        for product_card in product_cards: #Iterar todas las filas de productos
            try:
                count += 1
                product_detail_link = product_card.find('a', class_='jsx-3128226947')['href'] #Obtener link detalle
                html_text_desc = requests.get(product_detail_link).text #Obtenemos HTML de pagina detalle 
                detail_link = BeautifulSoup(html_text_desc, 'lxml')

                #Extraccion de datos

                product_model = ''
                product_procesador = ''
                product_ram= ''
                product_disco_duro = ''
                product_model = ''

                #Esto puede seer muy parecido para todas la e-commerces
                for row in detail_link.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                    row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                    if row_text[0] == "Procesador": #Encontramos el modelo y los asignamos a product_model
                        product_procesador = row_text[1]
                    if row_text[0] == "Memoria RAM":   
                        product_ram = row_text[1]
                    if row_text[0] == "Disco duro sólido":
                        product_disco_duro = row_text[1]
                    if row_text[0] == "Unidad de estado sólido SSD":
                        product_disco_duro = row_text[1]
                    if row_text [0] == 'Modelo':
                        product_model = row_text[1]
                          

                if product_disco_duro ==  "No aplica":
                    for row in detail_link.select('tbody tr'):  
                        row_text = [x.text for x in row.find_all('td')]     
                        if row_text[0] == "Disco duro": 
                            product_disco_duro = row_text[1]
                        if row_text[0] ==  "Disco duro HDD":
                            product_disco_duro = row_text[1]  

                print ('Validar disco duro', product_disco_duro)  

                if product_disco_duro ==  "No tiene":
                    product_disco_duro =  0       
                
                if product_disco_duro ==  "-":
                    product_disco_duro = 0

                if len(product_procesador) != 0 and len (product_disco_duro) != 0 and len(product_ram) != 0:

                    product_image = detail_link.find('img', class_='jsx-2487856160')['src']
                    product_discount = detail_link.find_all('span', class_='jsx-4284799404') #Hay dos elementos con clases iguales en este caso

                    #Obtenemos el que nos interesa del arreglo y extraemos solo los digitos
                    product_discount = re.findall(r'\d+', product_discount[len(product_discount) - 1].text)[0] 
                    product_brand = detail_link.find('a', class_='jsx-3572928369').text
                    product_name = detail_link.find('div', class_='jsx-3686231685').text
                    has_icon = detail_link.find('li', class_='jsx-3342506598 price-0').div.i
                    if has_icon:
                        product_price = detail_link.find('li', class_='jsx-3342506598 price-1').div.span.text.split()[1] #Obtener solo los numeros no caracteres
                    else:
                        product_price = detail_link.find('li', class_='jsx-3342506598 price-0').div.span.text.split()[1] #Obtener solo los numeros no caracteres

                    product_description = detail_link.find('div', class_='jsx-734470688 specifications-container fa--product-characteristic-features').text #Podemos agregar clases separadas por un solo espacio para mayor especificidad y evitar conflictos con otros elementos


                    #saveprocesadorConverted = product_procesador.replace("¿", " ") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                    #savediscoConverted = product_disco_duro.replace ("SSD" , " ")
                    savemodelConverte = product_model.replace ("/", " ")

                    data = {
                        'product_detail': product_detail_link,
                        'product_image': product_image,
                        'product_discount': product_discount,
                        'product_name': product_name,
                        'product_price': product_price,
                        'product_description': product_description,
                        'store': SAGA_STORE,
                        'category_group': TECNOLOGIA_GROUP_CATEGORY,
                        'category': COMPUTADORAS_CATEGORY,
                        'sub_category': LAPTOPS_SUBCATEGORY,
                        'brand': product_brand,
                        'model': product_model, #Para poder hacer la comparación con el mismo producto en otras tiendas
                        'model_store_unique_identifier':  SAGA_STORE + '_' + product_brand+ '_' + product_procesador + '_' + product_ram + '_' + product_disco_duro, #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                        'pricekey': product_price + '_' +  SAGA_STORE + '_' + savemodelConverte #Para poder hacer paginación ordenada por precio en el app
                    }

                    recorte = (data['model_store_unique_identifier']).find("SSD")
                    cambio = (data['model_store_unique_identifier'])

                    print ('recorte',recorte)

                    if recorte > 0:
                        size = len(cambio)
                        cambio = cambio[:size - 4]
                        print ('cambio',cambio)            

                    #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                    #eg: products/grupo-categoria/categoria/subcategoria
                    path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, COMPUTADORAS_CATEGORY, LAPTOPS_SUBCATEGORY, cambio)
                    result = firebase.patch(path, data) #creamos o actualizamos
                    today = date.today()
                    price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                    if price_history:
                        price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                        result['price_history'] = price_history
                    else:
                        result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                    result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion

            except:
                print("Producto no creado, error en el web scraping")
                print(product_name)
                traceback.print_exc() #podemos ver en donde estuvo el error
                continue #poner break en vez de continue para debuggear

#def find_products_tecnologia_tablets_saga():
#
#    firebase.delete("/comparizy-test-default-rtdb/products/tecnologia/computadoras/tablets", None) # Eliminamos los datos del realtimedatabase firebase 
#    
#    #Find saga products 
#    print('Saga Tablets products!!!')
#    print 
#
#    option = webdriver.ChromeOptions()
#    option.add_argument('disable-infobars')
#    
#    driver = webdriver.Chrome()
#    driver.get("about:blank")
#    driver.maximize_window()
#    try:
#        driver.get('https://www.falabella.com.pe/falabella-pe/category/cat270476/Tablets')
#        scrolldownSaga("0",driver)
#        html = driver.execute_script("return document.body.innerHTML;")
#        print("Pagina mostrada")
#    except Exception as e:
#        print(e)
#    finally:
#        driver.quit()
#    soup = BeautifulSoup(html,'lxml')
#
#    prueba = soup.find('ol', class_='jsx-2760063687').find_all('li') #Obtener el número de páginas 
#    print ('prueba',prueba)
#    primerapagina = prueba[0].text  
#    ultimapagina = prueba[len(prueba)-1].text 
#    print('primera',primerapagina)
#    print ('ultima',ultimapagina)
#
#    for i in range (int(primerapagina),int(ultimapagina)):
#
#        driver = webdriver.Chrome()
#        driver.get("about:blank")
#        driver.maximize_window()
#        try:
#            driver.get('https://www.falabella.com.pe/falabella-pe/category/cat270476/Tablets?page='+str(i))
#            scrolldownSaga("0",driver)
#            html = driver.execute_script("return document.body.innerHTML;")
#            print("Pagina mostrada")
#        except Exception as e:
#            print(e)
#        finally:
#            driver.quit()
#        soup = BeautifulSoup(html,'lxml')
#
#        product_cards = soup.find_all('div', class_='jsx-1802348960 jsx-3886284353 pod pod-3_GRID')
#        count = 0
#        product_name = ''
#        for product_card in product_cards: #Iterar todas las filas de productos
#            try:
#                count += 1          
#                product_detail_link = product_card.find('a', class_='jsx-1802348960 jsx-3886284353 pod-link')['href'] #Obtener link detalle
#                html_text_desc = requests.get(product_detail_link).text #Obtenemos HTML de pagina detalle 
#                detail_link = BeautifulSoup(html_text_desc, 'lxml')
#
#                product_procesador  = ''
#                product_memoria = ''
#                product_ram = ''
#                product_model = ''
#
#                #Esto puede seer muy parecido para todas la e-commerces
#                for row in detail_link.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
#                    row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
#                    if row_text[0] == "Procesador": #Encontramos el modelo y los asignamos a product_model
#                        product_procesador = row_text[1]
#                    if row_text[0] == "Memoria total":
#                        product_memoria = row_text[1]
#                    if row_text[0] == "Memoria interna":
#                        product_memoria = row_text[1]  
#                    if row_text[0] == "Memoria RAM":   
#                        product_ram = row_text[1]  
#                
#                if product_procesador == "No aplica":
#                    product_procesador = ""
#                if product_memoria == "No aplica":
#                    product_memoria = ""
#                if product_ram == "No aplica":
#                    product_ram = ""
#
#
#                if len(product_procesador) != 0 and len(product_memoria) != 0 and len(product_ram) !=0:        
#
#                    #Extraccion de datos
#
#                    product_image = detail_link.find('img', class_='jsx-2487856160')['src']
#                    product_discount = detail_link.find_all('span', class_='jsx-51363394') #Hay dos elementos con clases iguales en este caso
#
#                    #product_discount = re.findall(r'\d+', product_discount[len(product_discount) - 1].text)[0]
#                    product_brand = detail_link.find('a', class_='jsx-3572928369').text
#                    product_name = detail_link.find('div', class_='jsx-3686231685').text
#                    has_icon = detail_link.find('li', class_='jsx-3342506598 price-0').div.i
#                    if has_icon:
#                        product_price = detail_link.find('li', class_='jsx-3342506598 price-1').div.span.text.split()[1] #Obtener solo los numeros no caracteres
#                    else:
#                        product_price = detail_link.find('li', class_='jsx-3342506598 price-0').div.span.text.split()[1] #Obtener solo los numeros no caracteres
#
#                    product_description = detail_link.find('div', class_='jsx-3624412160 specifications-list').text #Podemos agregar clases separadas por un solo espacio para mayor especificidad y evitar conflictos con otros elementos
#
#
#                    saveModelConverted = product_model.replace("/", "A") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
#
#                    data = {
#                        'product_detail': product_detail_link,
#                        'product_image': product_image,
#                        'product_discount': product_discount,
#                        'product_name': product_name,
#                        'product_price': product_price,
#                        'product_description': product_description,
#                        'store': SAGA_STORE,
#                        'category_group': TECNOLOGIA_GROUP_CATEGORY,
#                        'category': COMPUTADORAS_CATEGORY,
#                        'sub_category': TABLETS_SUBCATEGORY,
#                        'brand': product_brand,
#                        'model': product_model, #Para poder hacer la comparación con el mismo producto en otras tiendas
#                        'model_store_unique_identifier':  SAGA_STORE + '_' + product_brand + '_' + product_procesador + '_' + product_memoria + '_' + product_ram, #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
#                        'pricekey': product_price + '_' +  SAGA_STORE + '_' + saveModelConverted #Para poder hacer paginación ordenada por precio en el app
#                    }
#
#                    #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
#                    #eg: products/grupo-categoria/categoria/subcategoria
#                    path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, COMPUTADORAS_CATEGORY, TABLETS_SUBCATEGORY, data['model_store_unique_identifier'])
#                    result = firebase.patch(path, data) #creamos o actualizamos
#                    today = date.today()
#                    price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
#                    if price_history:
#                        price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
#                        result['price_history'] = price_history
#                    else:
#                        result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
#                    result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
#            except:
#                print("Producto no creado, error en el web scraping")
#                print(product_name)
#                traceback.print_exc() #podemos ver en donde estuvo el error
#                continue #poner break en vez de continue para debuggear

def find_products_tecnologia_televisoresOLED_Saga():

    #firebase.delete("/comparizy-test-default-rtdb/products/tecnologia/televisores/oled", None)

    #Find saga's products
    #Laptops
    print('Saga products!!!')
    print()

    driver = webdriver.Chrome()
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.falabella.com.pe/falabella-pe/category/cat6370553/Televisores-OLED')
        scrolldownSaga("0",driver)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')
    # html_text = requests.get('https://www.falabella.com.pe/falabella-pe/category/cat40712/Laptops',timeout=(3.05, 27)).text
    # soup = BeautifulSoup(html_text, 'lxml')

    product_cards = soup.find_all('div', class_='jsx-4221770651 pod') #Obtener todas las filas de productos
    count = 0
    product_name = ''
    for product_card in product_cards: #Iterar todas las filas de productos
        try:
            count += 1
            product_detail_link = product_card.find('a', class_='jsx-3128226947')['href'] #Obtener link detalle
            html_text_desc = requests.get(product_detail_link).text #Obtenemos HTML de pagina detalle 
            detail_link = BeautifulSoup(html_text_desc, 'lxml')
            #Extraccion de datos
            product_model = ''
            
            #Esto puede seer muy parecido para todas la e-commerces
            for row in detail_link.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                if row_text[0] == "Modelo": #Encontramos el modelo y los asignamos a product_model
                    product_model = row_text[1] 

            #print ('modelo',product_model)    
           
            product_image = detail_link.find('img', class_='jsx-2487856160')['src']
            #product_discount = detail_link.find_all('span', class_='jsx-4284799404 copy8 primary jsx-340449923 bold pod-badges-item-PDP pod-badges-item') #Hay dos elementos con clases iguales en este caso
            #Obtenemos el que nos interesa del arreglo y extraemos solo los digitos
            #product_discount = re.findall(r'\d+', product_discount[len(product_discount) - 1].text)[0] 
            product_brand = detail_link.find('a', class_='jsx-3572928369').text
            product_name = detail_link.find('div', class_='jsx-3686231685').text
            has_icon = detail_link.find('li', class_='jsx-3342506598 price-0').div.i
            if has_icon:
                product_price = detail_link.find('li', class_='jsx-3342506598 price-1').div.span.text.split()[1] #Obtener solo los numeros no caracteres
            else:
                product_price = detail_link.find('li', class_='jsx-3342506598 price-0').div.span.text.split()[1] #Obtener solo los numeros no caracteres
            #product_description = detail_link.find('div', class_='jsx-3624412160 specifications-list').text #Podemos agregar clases separadas por un solo espacio para mayor especificidad y evitar conflictos con otros elementos
            
            #saveModelConverted = product_model.replace("/", "A")

            data = {
                'product_detail': product_detail_link,
                'product_image': product_image,
                #'product_discount': product_discount,
                'product_name': product_name,
                'product_price': product_price,
                'store': SAGA_STORE,
                'category_group': TECNOLOGIA_GROUP_CATEGORY,
                'category': TELEVISORES_CATEGORY,
                'sub_category': OLED_SUBCATEGORY,
                'brand': product_brand,
                'model': product_model, #Para poder hacer la comparación con el mismo producto en otras tiendas
                'model_store_unique_identifier':  SAGA_STORE + '_' + product_brand + '_' + product_model, #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                'pricekey': product_price + '_' +  SAGA_STORE + '_' + product_model #Para poder hacer paginación ordenada por precio en el app
            }
            #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
            #eg: products/grupo-categoria/categoria/subcategoria
            recorte = (data['model_store_unique_identifier']).find(".AWF")
            cambio = (data['model_store_unique_identifier'])
            print ('recorte',recorte)
            if recorte > 0:
                size =len(cambio)
                cambio = cambio[:size - 4]
                print ('cambio',cambio)
            path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, TELEVISORES_CATEGORY, OLED_SUBCATEGORY, cambio)
            result = firebase.patch(path, data) #creamos o actualizamos
            today = date.today()
            price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
            if price_history:
                price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                result['price_history'] = price_history
            else:
                result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
            result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
            print('TODO CORRECTO!!!')
        except Exception:
            print("Producto no creado, error en el web scraping")
            print(product_name)
            traceback.print_exc() #podemos ver en donde estuvo el error
            continue #poner break en vez de continue para debuggear

def find_products_tecnologia_televisoresQLED_Saga():

    #firebase.delete("/comparizy-test-default-rtdb/products/tecnologia/televisores/qled", None)

    #Find saga's products
    #Laptops
    print('Saga products!!!')
    print()

    driver = webdriver.Chrome()
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.falabella.com.pe/falabella-pe/category/cat7390472/Televisores-QLED')
        scrolldownSaga("0",driver)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')
    # html_text = requests.get('https://www.falabella.com.pe/falabella-pe/category/cat40712/Laptops',timeout=(3.05, 27)).text
    # soup = BeautifulSoup(html_text, 'lxml')

    product_cards = soup.find_all('div', class_='jsx-4221770651 pod') #Obtener todas las filas de productos
    count = 0
    product_name = ''
    for product_card in product_cards: #Iterar todas las filas de productos
        try:
            count += 1
            product_detail_link = product_card.find('a', class_='jsx-3128226947')['href'] #Obtener link detalle
            html_text_desc = requests.get(product_detail_link).text #Obtenemos HTML de pagina detalle 
            detail_link = BeautifulSoup(html_text_desc, 'lxml')
            #Extraccion de datos
            product_model = ''
            
            #Esto puede seer muy parecido para todas la e-commerces
            for row in detail_link.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                if row_text[0] == "Modelo": #Encontramos el modelo y los asignamos a product_model
                    product_model = row_text[1] 

            #print ('modelo',product_model)    
           
            product_image = detail_link.find('img', class_='jsx-2487856160')['src']
            #product_discount = detail_link.find_all('span', class_='jsx-4284799404') #Hay dos elementos con clases iguales en este caso
            #Obtenemos el que nos interesa del arreglo y extraemos solo los digitos
            #product_discount = re.findall(r'\d+', product_discount[len(product_discount) - 1].text)[0] 
            product_brand = detail_link.find('a', class_='jsx-3572928369').text
            product_name = detail_link.find('div', class_='jsx-3686231685').text
            has_icon = detail_link.find('li', class_='jsx-3342506598 price-0').div.i
            if has_icon:
                product_price = detail_link.find('li', class_='jsx-3342506598 price-1').div.span.text.split()[1] #Obtener solo los numeros no caracteres
            else:
                product_price = detail_link.find('li', class_='jsx-3342506598 price-0').div.span.text.split()[1] #Obtener solo los numeros no caracteres
            #product_description = detail_link.find('div', class_='jsx-3624412160 specifications-list').text #Podemos agregar clases separadas por un solo espacio para mayor especificidad y evitar conflictos con otros elementos
            
            #saveModelConverted = product_model.replace("/", "A")

            data = {
                'product_detail': product_detail_link,
                'product_image': product_image,
                #'product_discount': product_discount,
                'product_name': product_name,
                'product_price': product_price,
                'store': SAGA_STORE,
                'category_group': TECNOLOGIA_GROUP_CATEGORY,
                'category': TELEVISORES_CATEGORY,
                'sub_category': QLED_SUBCATEGORY,
                'brand': product_brand,
                'model': product_model, #Para poder hacer la comparación con el mismo producto en otras tiendas
                'model_store_unique_identifier':  SAGA_STORE + '_' + product_brand + '_' + product_model, #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                'pricekey': product_price + '_' +  SAGA_STORE + '_' + product_model #Para poder hacer paginación ordenada por precio en el app
            }
            #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
            #eg: products/grupo-categoria/categoria/subcategoria
            recorte = (data['model_store_unique_identifier']).find(".AWF")
            cambio = (data['model_store_unique_identifier'])
            print ('recorte',recorte)
            if recorte > 0:
                size =len(cambio)
                cambio = cambio[:size - 4]
                print ('cambio',cambio)
            path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, TELEVISORES_CATEGORY, QLED_SUBCATEGORY, cambio)
            result = firebase.patch(path, data) #creamos o actualizamos
            today = date.today()
            price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
            if price_history:
                price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                result['price_history'] = price_history
            else:
                result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
            result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
            print('TODO CORRECTO!!!')
        except Exception:
            print("Producto no creado, error en el web scraping")
            print(product_name)
            traceback.print_exc() #podemos ver en donde estuvo el error
            continue #poner break en vez de continue para debuggear

def find_products_electrohogar_refigeradoras_saga():
    #procesador, disco duro, memoria y marca. (en vez del modelo)

    #eg: products/grupo-categoria/categoria/subcategoria
    #Trabajamos con constantes (MAYUSCULAS) para evitar problemas de tipado
        
    #Analizar el siguiente detalle de producto como referencia 
    #https://www.falabella.com.pe/falabella-pe/product/882222620/Laptop-Lenovo-81WD00U9US-14-FHD-Core-i5-1035G1,8GB,512GB-SSD,-Platinium-Grey,-Teclado-en-ingles/882222620
    #Se recomienda probar linea por linea haciendo print de cada variable si se necesita comprender el código

    #firebase.delete("/comparizy-test-default-rtdb/products/electrohogar/refrigeracion/", None)

    #Find saga's productss
    #Laptops
    print('Saga products!!!')
    print()

    driver = webdriver.Chrome()
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.falabella.com.pe/falabella-pe/category/cat780530/Refrigeradoras')
        scrolldownSaga("0",driver)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')
    # html_text = requests.get('https://www.falabella.com.pe/falabella-pe/category/cat40712/Laptops',timeout=(3.05, 27)).text
    # soup = BeautifulSoup(html_text, 'lxml')
    prueba = soup.find('ol', class_='jsx-1794558402 jsx-1490357007').find_all('li') #Obtener páginas 
    print ('prueba',prueba)
    primerapagina = prueba[0].text  
    ultimapagina = prueba[len(prueba)-1].text 
    print('primera',primerapagina)
    print ('ultima',ultimapagina)
    
    for i in range (int(primerapagina), int(ultimapagina)):
        driver = webdriver.Chrome()
        driver.get("about:blank")
        driver.maximize_window()
        try:
            driver.get('https://www.falabella.com.pe/falabella-pe/category/cat780530/Refrigeradoras?page='+ str(i))
            scrolldownSaga("0",driver)
            html = driver.execute_script("return document.body.innerHTML;")
            print("Pagina mostrada")
        except Exception as e:
            print(e)
        finally:
            driver.quit()   
        soup = BeautifulSoup(html,'lxml')

        product_cards = soup.find_all('div', class_='jsx-4221770651 pod') #Obtener todas las filas de productos
        count = 0
        product_name = ''
        for product_card in product_cards: #Iterar todas las filas de productos
            try:
                count += 1
                product_detail_link = product_card.find('a', class_='jsx-3128226947')['href'] #Obtener link detalle
                html_text_desc = requests.get(product_detail_link).text #Obtenemos HTML de pagina detalle 
                detail_link = BeautifulSoup(html_text_desc, 'lxml')

                #Extraccion de datos
                product_model = ''
                product_capacidad = ''

                #Esto puede seer muy parecido para todas la e-commerces
                for row in detail_link.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                    row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                    if row_text[0] == "Modelo": #Encontramos el modelo y los asignamos a product_model
                        product_model = row_text[1]
                    if row_text[0] == "Capacidad total útil":
                        product_capacidad = row_text[1]
                
                recorte_model = (product_model).find('/PE')

                print ('recorte',recorte_model)
                print ('capacidad', product_model)

                if recorte_model > 0:
                    size = len(product_model)
                    product_model = product_model[:size-3]
                    print ('nuevo', product_model) 

                if len(product_model) != 0:
                    product_image = detail_link.find('img', class_='jsx-2487856160')['src']
                    #product_discount = detail_link.find_all('span', class_='jsx-4284799404') #Hay dos elementos con clases iguales en este caso
                    #Obtenemos el que nos interesa del arreglo y extraemos solo los digitos
                    #product_discount = re.findall(r'\d+', product_discount[len(product_discount) - 1].text)[0] 
                    product_brand = detail_link.find('a', class_='jsx-3572928369').text
                    product_name = detail_link.find('div', class_='jsx-3686231685').text
                    has_icon = detail_link.find('li', class_='jsx-3342506598 price-0').div.i
                    if has_icon:
                        product_price = detail_link.find('li', class_='jsx-3342506598 price-1').div.span.text.split()[1] #Obtener solo los numeros no caracteres
                    else:
                        product_price = detail_link.find('li', class_='jsx-3342506598 price-0').div.span.text.split()[1] #Obtener solo los numeros no caracteres
                    product_description = detail_link.find('div', class_='jsx-734470688 specifications-container fa--product-characteristic-features').text #Podemos agregar clases separadas por un solo espacio para mayor especificidad y evitar conflictos con otros elementos

                    data = {
                        'product_detail': product_detail_link,
                        'product_image': product_image,
                        #'product_discount': product_discount,
                        'product_name': product_name,
                        'product_price': product_price,
                        'product_description': product_description,
                        'store': SAGA_STORE,
                        'category_group': ELECTROHOGAR_GROUP_CATEGORY,
                        'category': REFRIGERACION_CATEGORY,
                        'sub_category': REFIGERADORAS_SUBCATEGORY,
                        'brand': product_brand,
                        'model': product_model, #Para poder hacer la comparación con el mismo producto en otras tiendas
                        'model_store_unique_identifier':  SAGA_STORE + '_' + product_brand+ '_' + product_model, #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                        'pricekey': product_price + '_' +  SAGA_STORE + '_' + product_model #Para poder hacer paginación ordenada por precio en el app
                    }

                    #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                    #eg: products/grupo-categoria/categoria/subcategoria
                    path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(ELECTROHOGAR_GROUP_CATEGORY, REFRIGERACION_CATEGORY, REFIGERADORAS_SUBCATEGORY, data['model_store_unique_identifier'])
                    result = firebase.patch(path, data) #creamos o actualizamos
                    today = date.today()
                    price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                    if price_history:
                        price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                        result['price_history'] = price_history
                    else:
                        result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                    result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion

            except:
                print("Producto no creado, error en el web scraping")
                print(product_name)
                traceback.print_exc() #podemos ver en donde estuvo el error
                continue #poner break en vez de continue para debuggear

def find_products_electrohogar_lavadoras_saga():
    #procesador, disco duro, memoria y marca. (en vez del modelo)

    #eg: products/grupo-categoria/categoria/subcategoria
    #Trabajamos con constantes (MAYUSCULAS) para evitar problemas de tipado
        
    #Analizar el siguiente detalle de producto como referencia 
    #https://www.falabella.com.pe/falabella-pe/product/882222620/Laptop-Lenovo-81WD00U9US-14-FHD-Core-i5-1035G1,8GB,512GB-SSD,-Platinium-Grey,-Teclado-en-ingles/882222620
    #Se recomienda probar linea por linea haciendo print de cada variable si se necesita comprender el código

    #firebase.delete("/comparizy-test-default-rtdb/products/electrohogar/lavado/lavadoras", None)

    #Find saga's productss
    #Laptops
    print('Saga products!!!')
    print()

    driver = webdriver.Chrome()
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.falabella.com.pe/falabella-pe/category/cat780522/Lavadoras')
        scrolldownSaga("0",driver)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')
    # html_text = requests.get('https://www.falabella.com.pe/falabella-pe/category/cat40712/Laptops',timeout=(3.05, 27)).text
    # soup = BeautifulSoup(html_text, 'lxml')
    prueba = soup.find('ol', class_='jsx-1794558402 jsx-1490357007').find_all('li') #Obtener páginas 
    print ('prueba',prueba)
    primerapagina = prueba[0].text  
    ultimapagina = prueba[len(prueba)-1].text 
    print('primera',primerapagina)
    print ('ultima',ultimapagina)
    
    for i in range (int(primerapagina), int(ultimapagina)):
        driver = webdriver.Chrome()
        driver.get("about:blank")
        driver.maximize_window()
        try:
            driver.get('https://www.falabella.com.pe/falabella-pe/category/cat780522/Lavadoras?page='+ str(i))
            scrolldownSaga("0",driver)
            html = driver.execute_script("return document.body.innerHTML;")
            print("Pagina mostrada")
        except Exception as e:
            print(e)
        finally:
            driver.quit()   
        soup = BeautifulSoup(html,'lxml')

        product_cards = soup.find_all('div', class_='jsx-3153667981 jsx-3886284353 pod pod-4_GRID') #Obtener todas las filas de productos
        count = 0
        product_name = ''
        for product_card in product_cards: #Iterar todas las filas de productos
            try:
                count += 1
                product_detail_link = product_card.find('a', class_='jsx-3128226947')['href'] #Obtener link detalle
                html_text_desc = requests.get(product_detail_link).text #Obtenemos HTML de pagina detalle 
                detail_link = BeautifulSoup(html_text_desc, 'lxml')

                #Extraccion de datos
                product_model = ''
                product_capacidad = ''

                #Esto puede seer muy parecido para todas la e-commerces
                for row in detail_link.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                    row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                    if row_text[0] == "Modelo": #Encontramos el modelo y los asignamos a product_model
                        product_model = row_text[1]
                    if row_text[0] == "Capacidad total útil":
                        product_capacidad = row_text[1]
                
                recorte_model = (product_model).find('/PE')

                print ('recorte',recorte_model)
                print ('capacidad', product_model)

                if recorte_model > 0:
                    size = len(product_model)
                    product_model = product_model[:size-3]
                    print ('nuevo', product_model) 

                recorte_model4 = (product_model).find('.ASSGLGP')  

                if recorte_model4 > 0:

                    size = len(product_model)
                    product_model = product_model[:size-8]
                    print ('nuevo', product_model)    

                if len(product_model) != 0:
                    product_image = detail_link.find('img', class_='jsx-2487856160')['src']
                    #product_discount = detail_link.find_all('span', class_='jsx-4284799404') #Hay dos elementos con clases iguales en este caso
                    #Obtenemos el que nos interesa del arreglo y extraemos solo los digitos
                    #product_discount = re.findall(r'\d+', product_discount[len(product_discount) - 1].text)[0] 
                    product_brand = detail_link.find('a', class_='jsx-3572928369').text
                    product_name = detail_link.find('div', class_='jsx-3686231685').text
                    has_icon = detail_link.find('li', class_='jsx-3342506598 price-0').div.i
                    if has_icon:
                        product_price = detail_link.find('li', class_='jsx-3342506598 price-1').div.span.text.split()[1] #Obtener solo los numeros no caracteres
                    else:
                        product_price = detail_link.find('li', class_='jsx-3342506598 price-0').div.span.text.split()[1] #Obtener solo los numeros no caracteres
                    product_description = detail_link.find('div', class_='jsx-734470688 specifications-container fa--product-characteristic-features').text #Podemos agregar clases separadas por un solo espacio para mayor especificidad y evitar conflictos con otros elementos

                    data = {
                        'product_detail': product_detail_link,
                        'product_image': product_image,
                        #'product_discount': product_discount,
                        'product_name': product_name,
                        'product_price': product_price,
                        'product_description': product_description,
                        'store': SAGA_STORE,
                        'category_group': ELECTROHOGAR_GROUP_CATEGORY,
                        'category': LAVADO_CATEGORY,
                        'sub_category': LAVADORAS_SUBCATEGORY,
                        'brand': product_brand,
                        'model': product_model, #Para poder hacer la comparación con el mismo producto en otras tiendas
                        'model_store_unique_identifier':  SAGA_STORE + '_' + product_brand+ '_' + product_model, #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                        'pricekey': product_price + '_' +  SAGA_STORE + '_' + product_model #Para poder hacer paginación ordenada por precio en el app
                    }

                    #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                    #eg: products/grupo-categoria/categoria/subcategoria
                    path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(ELECTROHOGAR_GROUP_CATEGORY, LAVADO_CATEGORY, LAVADORAS_SUBCATEGORY, data['model_store_unique_identifier'])
                    result = firebase.patch(path, data) #creamos o actualizamos
                    today = date.today()
                    price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                    if price_history:
                        price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                        result['price_history'] = price_history
                    else:
                        result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                    result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion

            except:
                print("Producto no creado, error en el web scraping")
                print(product_name)
                traceback.print_exc() #podemos ver en donde estuvo el error
                continue #poner break en vez de continue para debuggear

def find_products_electrohogar_secadoras_saga():
    #procesador, disco duro, memoria y marca. (en vez del modelo)

    #eg: products/grupo-categoria/categoria/subcategoria
    #Trabajamos con constantes (MAYUSCULAS) para evitar problemas de tipado
        
    #Analizar el siguiente detalle de producto como referencia 
    #https://www.falabella.com.pe/falabella-pe/product/882222620/Laptop-Lenovo-81WD00U9US-14-FHD-Core-i5-1035G1,8GB,512GB-SSD,-Platinium-Grey,-Teclado-en-ingles/882222620
    #Se recomienda probar linea por linea haciendo print de cada variable si se necesita comprender el código

    #firebase.delete("/comparizy-test-default-rtdb/products/electrohogar/lavado/secadoras", None)

    #Find saga's productss
    #Laptops
    print('Saga products!!!')
    print()

    driver = webdriver.Chrome()
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.falabella.com.pe/falabella-pe/category/cat780524/Secadoras')
        scrolldownSaga("0",driver)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')
    # html_text = requests.get('https://www.falabella.com.pe/falabella-pe/category/cat40712/Laptops',timeout=(3.05, 27)).text
    # soup = BeautifulSoup(html_text, 'lxml')
    
    product_cards = soup.find_all('div', class_='jsx-3153667981 jsx-3886284353 pod pod-4_GRID') #Obtener todas las filas de productos
    count = 0
    product_name = ''
    for product_card in product_cards: #Iterar todas las filas de productos
        try:
            count += 1
            product_detail_link = product_card.find('a', class_='jsx-3128226947')['href'] #Obtener link detalle
            html_text_desc = requests.get(product_detail_link).text #Obtenemos HTML de pagina detalle 
            detail_link = BeautifulSoup(html_text_desc, 'lxml')
            #Extraccion de datos
            product_model = ''
            product_capacidad = ''
            #Esto puede seer muy parecido para todas la e-commerces
            for row in detail_link.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                if row_text[0] == "Modelo": #Encontramos el modelo y los asignamos a product_model
                    product_model = row_text[1]
                if row_text[0] == "Capacidad total útil":
                    product_capacidad = row_text[1]
            
            recorte_model = (product_model).find('/PE')
            print ('recorte',recorte_model)
            print ('capacidad', product_model)
            if recorte_model > 0:
                size = len(product_model)
                product_model = product_model[:size-3]
                print ('nuevo', product_model) 
            recorte_model4 = (product_model).find('.ASSGLGP')  
            if recorte_model4 > 0:
                size = len(product_model)
                product_model = product_model[:size-8]
                print ('nuevo', product_model)    
            if len(product_model) != 0:
                product_image = detail_link.find('img', class_='jsx-2487856160')['src']
                #product_discount = detail_link.find_all('span', class_='jsx-4284799404') #Hay dos elementos con clases iguales en este caso
                #Obtenemos el que nos interesa del arreglo y extraemos solo los digitos
                #product_discount = re.findall(r'\d+', product_discount[len(product_discount) - 1].text)[0] 
                product_brand = detail_link.find('a', class_='jsx-3572928369').text
                product_name = detail_link.find('div', class_='jsx-3686231685').text
                has_icon = detail_link.find('li', class_='jsx-3342506598 price-0').div.i
                if has_icon:
                    product_price = detail_link.find('li', class_='jsx-3342506598 price-1').div.span.text.split()[1] #Obtener solo los numeros no caracteres
                else:
                    product_price = detail_link.find('li', class_='jsx-3342506598 price-0').div.span.text.split()[1] #Obtener solo los numeros no caracteres
                product_description = detail_link.find('div', class_='jsx-734470688 specifications-container fa--product-characteristic-features').text #Podemos agregar clases separadas por un solo espacio para mayor especificidad y evitar conflictos con otros elementos
                data = {
                    'product_detail': product_detail_link,
                    'product_image': product_image,
                    #'product_discount': product_discount,
                    'product_name': product_name,
                    'product_price': product_price,
                    'product_description': product_description,
                    'store': SAGA_STORE,
                    'category_group': ELECTROHOGAR_GROUP_CATEGORY,
                    'category': LAVADO_CATEGORY,
                    'sub_category': SECADORAS_SUBCATEGORY,
                    'brand': product_brand,
                    'model': product_model, #Para poder hacer la comparación con el mismo producto en otras tiendas
                    'model_store_unique_identifier':  SAGA_STORE + '_' + product_brand+ '_' + product_model, #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                    'pricekey': product_price + '_' +  SAGA_STORE + '_' + product_model #Para poder hacer paginación ordenada por precio en el app
                }
                #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                #eg: products/grupo-categoria/categoria/subcategoria
                path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(ELECTROHOGAR_GROUP_CATEGORY, LAVADO_CATEGORY, SECADORAS_SUBCATEGORY, data['model_store_unique_identifier'])
                result = firebase.patch(path, data) #creamos o actualizamos
                today = date.today()
                price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                if price_history:
                    price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                    result['price_history'] = price_history
                else:
                    result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion

        except:
            print("Producto no creado, error en el web scraping")
            print(product_name)
            traceback.print_exc() #podemos ver en donde estuvo el error
            continue #poner break en vez de continue para debuggear

def find_products_electrohogar_cocinadepie_saga():
    #procesador, disco duro, memoria y marca. (en vez del modelo)

    #eg: products/grupo-categoria/categoria/subcategoria
    #Trabajamos con constantes (MAYUSCULAS) para evitar problemas de tipado
        
    #Analizar el siguiente detalle de producto como referencia 
    #https://www.falabella.com.pe/falabella-pe/product/882222620/Laptop-Lenovo-81WD00U9US-14-FHD-Core-i5-1035G1,8GB,512GB-SSD,-Platinium-Grey,-Teclado-en-ingles/882222620
    #Se recomienda probar linea por linea haciendo print de cada variable si se necesita comprender el código

    #firebase.delete("/comparizy-test-default-rtdb/products/electrohogar/cocina/", None)

    #Find saga's productss
    #Laptops
    print('Saga products!!!')
    print()

    driver = webdriver.Chrome()
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.falabella.com.pe/falabella-pe/category/cat840599/Cocinas-de-Pie')
        scrolldownSaga("0",driver)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')
    # html_text = requests.get('https://www.falabella.com.pe/falabella-pe/category/cat40712/Laptops',timeout=(3.05, 27)).text
    # soup = BeautifulSoup(html_text, 'lxml')
    prueba = soup.find('ol', class_='jsx-1794558402 jsx-1490357007').find_all('li') #Obtener páginas 
    print ('prueba',prueba)
    primerapagina = prueba[0].text  
    ultimapagina = prueba[len(prueba)-1].text 
    print('primera',primerapagina)
    print ('ultima',ultimapagina)
    
    for i in range (int(primerapagina), int(ultimapagina)):
        driver = webdriver.Chrome()
        driver.get("about:blank")
        driver.maximize_window()
        try:
            driver.get('https://www.falabella.com.pe/falabella-pe/category/cat840599/Cocinas-de-Pie?page='+ str(i))
            scrolldownSaga("0",driver)
            html = driver.execute_script("return document.body.innerHTML;")
            print("Pagina mostrada")
        except Exception as e:
            print(e)
        finally:
            driver.quit()   
        soup = BeautifulSoup(html,'lxml')

        product_cards = soup.find_all('div', class_='jsx-3153667981 jsx-3886284353 pod pod-4_GRID') #Obtener todas las filas de productos
        count = 0
        product_name = ''
        for product_card in product_cards: #Iterar todas las filas de productos
            try:
                count += 1
                product_detail_link = product_card.find('a', class_='jsx-3128226947')['href'] #Obtener link detalle
                html_text_desc = requests.get(product_detail_link).text #Obtenemos HTML de pagina detalle 
                detail_link = BeautifulSoup(html_text_desc, 'lxml')

                #Extraccion de datos
                product_model = ''
                product_capacidad = ''

                #Esto puede seer muy parecido para todas la e-commerces
                for row in detail_link.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                    row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                    if row_text[0] == "Modelo": #Encontramos el modelo y los asignamos a product_model
                        product_model = row_text[1]
                    if row_text[0] == "Capacidad total útil":
                        product_capacidad = row_text[1]
                
                recorte_model = (product_model).find('/PE')

                print ('recorte',recorte_model)
                print ('capacidad', product_model)

                if recorte_model > 0:
                    size = len(product_model)
                    product_model = product_model[:size-3]
                    print ('nuevo', product_model) 

                if len(product_model) != 0:
                    product_image = detail_link.find('img', class_='jsx-2487856160')['src']
                    #product_discount = detail_link.find_all('span', class_='jsx-4284799404') #Hay dos elementos con clases iguales en este caso
                    #Obtenemos el que nos interesa del arreglo y extraemos solo los digitos
                    #product_discount = re.findall(r'\d+', product_discount[len(product_discount) - 1].text)[0] 
                    product_brand = detail_link.find('a', class_='jsx-3572928369').text
                    product_name = detail_link.find('div', class_='jsx-3686231685').text
                    has_icon = detail_link.find('li', class_='jsx-3342506598 price-0').div.i
                    if has_icon:
                        product_price = detail_link.find('li', class_='jsx-3342506598 price-1').div.span.text.split()[1] #Obtener solo los numeros no caracteres
                    else:
                        product_price = detail_link.find('li', class_='jsx-3342506598 price-0').div.span.text.split()[1] #Obtener solo los numeros no caracteres
                    product_description = detail_link.find('div', class_='jsx-734470688 specifications-container fa--product-characteristic-features').text #Podemos agregar clases separadas por un solo espacio para mayor especificidad y evitar conflictos con otros elementos

                    data = {
                        'product_detail': product_detail_link,
                        'product_image': product_image,
                        #'product_discount': product_discount,
                        'product_name': product_name,
                        'product_price': product_price,
                        'product_description': product_description,
                        'store': SAGA_STORE,
                        'category_group': ELECTROHOGAR_GROUP_CATEGORY,
                        'category': COCINA_CATEGORY,
                        'sub_category': COCINADEPIE_SUBCATEGORY,
                        'brand': product_brand,
                        'model': product_model, #Para poder hacer la comparación con el mismo producto en otras tiendas
                        'model_store_unique_identifier':  SAGA_STORE + '_' + product_brand+ '_' + product_model, #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                        'pricekey': product_price + '_' +  SAGA_STORE + '_' + product_model #Para poder hacer paginación ordenada por precio en el app
                    }

                    #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                    #eg: products/grupo-categoria/categoria/subcategoria
                    path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(ELECTROHOGAR_GROUP_CATEGORY, COCINA_CATEGORY, COCINADEPIE_SUBCATEGORY, data['model_store_unique_identifier'])
                    result = firebase.patch(path, data) #creamos o actualizamos
                    today = date.today()
                    price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                    if price_history:
                        price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                        result['price_history'] = price_history
                    else:
                        result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                    result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion

            except:
                print("Producto no creado, error en el web scraping")
                print(product_name)
                traceback.print_exc() #podemos ver en donde estuvo el error
                continue #poner break en vez de continue para debuggear

def find_products_tecnologia_computadoras_ripley():

    #firebase.delete("/comparizy-test-default-rtdb/products/tecnologia/computadoras/", None)

    #Find replay's products
    print('Ripley products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://simple.ripley.com.pe/tecnologia/computacion/laptops?source=menu')
        scrolldownRipley("0",driver, 4623)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    prueba = soup.find('div', class_= "catalog-page__footer-pagination").find('nav').find('ul',class_="pagination").find_all('li')
    print ('prueba', prueba)
    primerapagina = prueba[1].text
    ultimapagina = prueba[len(prueba)-2].text
    print('primera',primerapagina)
    print ('ultima',ultimapagina)

    
    for i in range (int(primerapagina),int(ultimapagina)):

        driver = webdriver.Chrome(chrome_options=option)
        driver.get("about:blank")
        driver.maximize_window()
        try:
            driver.get('https://simple.ripley.com.pe/tecnologia/computacion/laptops?source=menu&page='+str(i))
            scrolldownRipley("0",driver, 4623)
            html = driver.execute_script("return document.body.innerHTML;")
            print("Pagina mostrada")
        except Exception as e:
            print(e)
        finally:
            driver.quit()   
        soup = BeautifulSoup(html,'lxml')

        product_cards = soup.find_all('div', class_='catalog-product-item')
        count = 0
        product_name = ''
        for product_card in product_cards:
            try:
                    # count += 1
                # if count == 3:
                    product_detail_link = product_card.find('a', class_='catalog-product-item')['href'] #Obtener link detalle
                    driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
                    driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
                    driver.maximize_window()
                    try:
                        driver.get('https://simple.ripley.com.pe' + product_detail_link)
                        scrolldownRipley("0",driver, 3272, 0.01) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                        html = driver.execute_script("return document.body.innerHTML;")
                        print("Pagina mostrada")
                    except Exception as e:
                        print(e)
                    finally:
                        driver.quit()   

                    detail_link = BeautifulSoup(html, 'lxml')

                    #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
                    #with open('file7.txt', 'w') as file: 
                        #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas

                    print('PASO LA LECTURA!!! ... obteniendo datos!')
                    #Extraccion de datos
                    product_image = detail_link.find('ul', class_='product-image-previews').li.img['data-src'][2:] # quitale las 2 rayitas de adelante del string
                    product_name = detail_link.find('section', class_='product-header visible-xs').h1.text
                    product_discount = detail_link.find('span', class_='discount-percentage')
                    if product_discount:
                        product_discount = detail_link.find('span', class_='discount-percentage').text[1:-1] #solo quiero el numerotext.
                    else:
                        product_discount = 0

                    product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best')
                    if product_price:
                        product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best').dt.text.split()[1]
                    else:
                         product_price = detail_link.find('div', class_='product-price-container product-internet-price').dt.text.split()[1]

                    product_description = detail_link.find('h2', class_='product-short-description').text

                    #obtenemos referencia a la tabla de especificaciones
                    tableReference = detail_link.find('table', class_='table table-striped')
                    product_brand = ''
                    product_model = ''
                    product_procesador = ''
                    product_ram= ''
                    product_disco_duro = ''
                    product_color= ''

                    #Esto puede seer muy parecido para todas la e-commerces
                    for row in tableReference.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                        row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                        if row_text[0] == "Marca": #Encontramos la marca, modelo
                            product_brand = row_text[1]
                        if row_text[0] == "Modelo": 
                            product_model = row_text[1]
                        if row_text[0] == "Procesador": #Encontramos el modelo y los asignamos a product_model
                            product_procesador = row_text[1]
                        if row_text[0] == "Memoria RAM":   
                            product_ram = row_text[1]
                        if row_text[0] == "Disco Duro":
                            product_disco_duro = row_text[1]
                        if  row_text[0] == 'Color':    
                            product_color = row_text[1]


                    saveModelConverted = product_model.replace("/", "A") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                    #.strip() remueve los espacios en blanco al inicio y al final de un string
                    #print('disco duro',product_disco_duro)

                    #size = len (product_disco_duro)
                    #if product_disco_duro[:size+3]

                    #print('disco duro',final_str)

                    data = {
                        'product_detail': 'https://simple.ripley.com.pe' + product_detail_link,
                        'product_image': product_image,
                        'product_discount': product_discount,
                        'product_name': product_name,
                        'product_price': product_price,
                        'product_description': product_description,
                        'store': RIPLEY_STORE,
                        'category_group': TECNOLOGIA_GROUP_CATEGORY,
                        'category': COMPUTADORAS_CATEGORY,
                        'sub_category': LAPTOPS_SUBCATEGORY,
                        'brand': product_brand,
                        'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                        'model_store_unique_identifier':  RIPLEY_STORE + '_' + product_brand+ '_' + product_procesador+ '_' + product_ram + '_' + product_disco_duro, #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                        'pricekey': product_price + '_' +  RIPLEY_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                    }

                    #Hacemos esto para quitar el SSD de la cadena string para que los codigo concidan 
                    recorte = (data['model_store_unique_identifier']).find("SSD")
                    cambio = (data['model_store_unique_identifier'])

                    print ('recorte',recorte)

                    if recorte > 0:
                        size = len(cambio)
                        cambio = cambio[:size - 4]
                        print ('cambio',cambio) 

                    #print ('cambio',cambio)

                    #if cambio[0:4] == ' SDD':
                        #cambio = cambio.strip['"']
                        #print ('cambio',cambio)
                        #cambio = cambio[1:-1]
                        

                    #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                    #eg: products/grupo-categoria/categoria/subcategoria
                    path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, COMPUTADORAS_CATEGORY, LAPTOPS_SUBCATEGORY, cambio)
                    result = firebase.patch(path, data) #creamos o actualizamos
                    today = date.today()
                    price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                    if price_history:
                        price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                        result['price_history'] = price_history
                    else:
                        result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                    result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                    print('TODO CORRECTO!!!')
            except Exception:
                print("Producto no creado, error en el web scraping")
                print(product_name)
                traceback.print_exc() #podemos ver en donde estuvo el error
                continue #poner break en vez de continue para debuggear

#def find_products_tecnologia_tablets_ripley():
#
#    #Find tablets products
#    print('Ripley tablets products!!!')
#    print()     
#
#    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
#    option.add_argument('disable-infobars') 
#
#    driver = webdriver.Chrome(chrome_options=option)
#    driver.get("about:blank")
#    driver.maximize_window()
#    try:
#        driver.get('https://simple.ripley.com.pe/tecnologia/computacion/tablets?source=menu')
#        scrolldownRipley("0",driver, 4494)
#        html = driver.execute_script("return document.body.innerHTML;")
#        print("Pagina mostrada")
#    except Exception as e:
#        print(e)
#    finally:
#        driver.quit()
#    soup = BeautifulSoup(html,'lxml')  
#     
#    product_cards = soup.find_all('div', class_='catalog-product-item')
#    count = 0
#    product_name = ''
#    for product_card in product_cards:
#        try:
#                product_detail_link = product_card.find('a', class_='catalog-product-item')['href'] #Obtener link detalle
#                driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
#                driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
#                driver.maximize_window()
#                try:
#                    driver.get('https://simple.ripley.com.pe' + product_detail_link)
#                    scrolldownRipley("0",driver,2921, 0.01) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
#                    html = driver.execute_script("return document.body.innerHTML;")
#                    print("Pagina mostrada")
#                except Exception as e:
#                    print(e)
#                finally:
#                    driver.quit()      
#
#                detail_link = BeautifulSoup(html, 'lxml')      
#
#            #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
#           # with open('file4.txt', 'w') as file: 
#                    #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas
#
#                print('PASO LA LECTURA!!! ... obteniendo datos!')
#                #Extraccion de datos
#                product_image = detail_link.find('ul', class_='product-image-previews').li.img['data-src'][2:] # quitale las 2 rayitas de adelante del string
#                product_name = detail_link.find('section', class_='product-header visible-xs').h1.text
#                product_discount = detail_link.find('span', class_='discount-percentage')
#                if product_discount:
#                    product_discount = detail_link.find('span', class_='discount-percentage').text[1:-1] #solo quiero el numerotext.
#                else:
#                    product_discount = 0
#                 
#                product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best')
#                if product_price:
#                    product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best').dt.text.split()[1]
#                else:
#                    product_price = detail_link.find('div', class_='product-price-container product-internet-price').dt.text.split()[1]
#                 
#                product_description = detail_link.find('h2', class_='product-short-description').text
#                
#                #obtenemos referencia a la tabla de especificaciones
#                tableReference = detail_link.find('table', class_='table table-striped')
#                product_brand = ''
#                product_model = ''
#
#                #Esto puede seer muy parecido para todas la e-commerces
#                for row in tableReference.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
#                    row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
#                    if row_text[0] == "Marca": #Encontramos la marca, modelo
#                        product_brand = row_text[1]
#                    if row_text[0] == "Modelo": 
#                        product_model = row_text[1]
#                
#                saveModelConverted = product_model.replace("/", "A") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
#                #.strip() remueve los espacios en blanco al inicio y al final de un string
#                
#                data = {
#                    'product_detail': 'https://simple.ripley.com.pe' + product_detail_link,
#                    'product_image': product_image,
#                    'product_discount': product_discount,
#                    'product_name': product_name,
#                    'product_price': product_price,
#                    'product_description': product_description,
#                    'store': RIPLEY_STORE,
#                    'category_group': TECNOLOGIA_GROUP_CATEGORY,
#                    'category': COMPUTADORAS_CATEGORY,
#                    'sub_category': TABLETS_SUBCATEGORY,
#                    'brand': product_brand,
#                    'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
#                    'model_store_unique_identifier':  RIPLEY_STORE + '_' + saveModelConverted.strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
#                    'pricekey': product_price + '_' +  RIPLEY_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
#                }
#
#                #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
#                #eg: products/grupo-categoria/categoria/subcategoria
#                path = "/comparizy-c73ab-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, COMPUTADORAS_CATEGORY, TABLETS_SUBCATEGORY, data['model_store_unique_identifier'])
#                result = firebase.patch(path, data) #creamos o actualizamos
#                today = date.today()
#                price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
#                if price_history:
#                    price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
#                    result['price_history'] = price_history
#                else:
#                    result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
#                result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
#                print('TODO CORRECTO!!!')
#        except Exception:
#            print("Producto no creado, error en el web scraping")
#            print(product_name)
#            traceback.print_exc() #podemos ver en donde estuvo el error
#            continue #poner break en vez de continue para debuggear    
            
def find_products_tecnologia_televisoresOLED_Ripley():

    #firebase.delete("/comparizy-test-default-rtdb/products/tecnologia/computadoras/", None)

    #Find replay's products
    print('Ripley products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://simple.ripley.com.pe/tecnologia/tv-y-cine-en-casa/televisores?facet=Tecnolog%C3%ADa%20de%20Pantalla%3AOLED')
        scrolldownRipley("0",driver, 4623)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    product_cards = soup.find_all('div', class_='catalog-product-item')
    count = 0
    product_name = ''
    for product_card in product_cards:
        try:
                # count += 1
            # if count == 3:
                product_detail_link = product_card.find('a', class_='catalog-product-item')['href'] #Obtener link detalle
                driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
                driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
                driver.maximize_window()
                try:
                    driver.get('https://simple.ripley.com.pe' + product_detail_link)
                    scrolldownRipley("0",driver, 3272, 0.01) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                    html = driver.execute_script("return document.body.innerHTML;")
                    print("Pagina mostrada")
                except Exception as e:
                    print(e)
                finally:
                    driver.quit()   
                detail_link = BeautifulSoup(html, 'lxml')
                #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
                #with open('file7.txt', 'w') as file: 
                    #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas
                print('PASO LA LECTURA!!! ... obteniendo datos!')
                #Extraccion de datos
                product_image = detail_link.find('ul', class_='product-image-previews').li.img['data-src'][2:] # quitale las 2 rayitas de adelante del string
                product_name = detail_link.find('section', class_='product-header visible-xs').h1.text
                product_discount = detail_link.find('span', class_='discount-percentage')
                if product_discount:
                    product_discount = detail_link.find('span', class_='discount-percentage').text[1:-1] #solo quiero el numerotext.
                else:
                    product_discount = 0
                product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best')
                if product_price:
                    product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best').dt.text.split()[1]
                else:
                     product_price = detail_link.find('div', class_='product-price-container product-internet-price').dt.text.split()[1]
                product_description = detail_link.find('h2', class_='product-short-description').text
                #obtenemos referencia a la tabla de especificaciones
                tableReference = detail_link.find('table', class_='table table-striped')
                product_brand = ''
                product_model = ''

                #Esto puede seer muy parecido para todas la e-commerces
                for row in tableReference.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                    row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                    if row_text[0] == "Modelo": 
                        product_model = row_text[1]
                    if row_text[0] == "Marca":
                        product_brand = row_text[1]

                saveModelConverted = product_model.replace("/", "A") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                #.strip() remueve los espacios en blanco al inicio y al final de un string
                #print('disco duro',product_disco_duro)
                #size = len (product_disco_duro)
                #if product_disco_duro[:size+3]
                #print('disco duro',final_str)
                data = {
                    'product_detail': 'https://simple.ripley.com.pe' + product_detail_link,
                    'product_image': product_image,
                    'product_discount': product_discount,
                    'product_name': product_name,
                    'product_price': product_price,
                    'product_description': product_description,
                    'store': RIPLEY_STORE,
                    'category_group': TECNOLOGIA_GROUP_CATEGORY,
                    'category': COMPUTADORAS_CATEGORY,
                    'sub_category': LAPTOPS_SUBCATEGORY,
                    'brand': product_brand,
                    'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                    'model_store_unique_identifier':  RIPLEY_STORE + '_'+ product_brand + '_' + saveModelConverted .strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                    'pricekey': product_price + '_' +  RIPLEY_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                }
                #cambio = (data['model_store_unique_identifier']).rstrip('SDD')
                #print ('cambio',cambio)
                #if cambio[0:4] == ' SDD':
                    #cambio = cambio.strip['"']
                    #print ('cambio',cambio)
                    #cambio = cambio[1:-1]
                    
                #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                #eg: products/grupo-categoria/categoria/subcategoria
                path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, TELEVISORES_CATEGORY, OLED_SUBCATEGORY, data['model_store_unique_identifier'])
                result = firebase.patch(path, data) #creamos o actualizamos
                today = date.today()
                price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                if price_history:
                    price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                    result['price_history'] = price_history
                else:
                    result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                print('TODO CORRECTO!!!')
        except Exception:
            print("Producto no creado, error en el web scraping")
            print(product_name)
            traceback.print_exc() #podemos ver en donde estuvo el error
            continue #poner break en vez de continue para debuggear

def find_products_tecnologia_televisoresQLED_Ripley():

    #firebase.delete("/comparizy-test-default-rtdb/products/tecnologia/computadoras/", None)

    #Find replay's products
    print('Ripley products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://simple.ripley.com.pe/tecnologia/tv-y-cine-en-casa/televisores?facet=Tecnolog%C3%ADa%20de%20Pantalla%3AQLED')
        scrolldownRipley("0",driver, 4623)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    product_cards = soup.find_all('div', class_='catalog-product-item')
    count = 0
    product_name = ''
    for product_card in product_cards:
        try:
                # count += 1
            # if count == 3:
                product_detail_link = product_card.find('a', class_='catalog-product-item')['href'] #Obtener link detalle
                driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
                driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
                driver.maximize_window()
                try:
                    driver.get('https://simple.ripley.com.pe' + product_detail_link)
                    scrolldownRipley("0",driver, 3272, 0.01) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                    html = driver.execute_script("return document.body.innerHTML;")
                    print("Pagina mostrada")
                except Exception as e:
                    print(e)
                finally:
                    driver.quit()   
                detail_link = BeautifulSoup(html, 'lxml')
                #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
                #with open('file7.txt', 'w') as file: 
                    #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas
                print('PASO LA LECTURA!!! ... obteniendo datos!')
                #Extraccion de datos
                product_image = detail_link.find('ul', class_='product-image-previews').li.img['data-src'][2:] # quitale las 2 rayitas de adelante del string
                product_name = detail_link.find('section', class_='product-header visible-xs').h1.text
                product_discount = detail_link.find('span', class_='discount-percentage')
                if product_discount:
                    product_discount = detail_link.find('span', class_='discount-percentage').text[1:-1] #solo quiero el numerotext.
                else:
                    product_discount = 0
                product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best')
                if product_price:
                    product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best').dt.text.split()[1]
                else:
                     product_price = detail_link.find('div', class_='product-price-container product-internet-price').dt.text.split()[1]
                product_description = detail_link.find('h2', class_='product-short-description').text
                #obtenemos referencia a la tabla de especificaciones
                tableReference = detail_link.find('table', class_='table table-striped')
                product_brand = ''
                product_model = ''

                #Esto puede seer muy parecido para todas la e-commerces
                for row in tableReference.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                    row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                    if row_text[0] == "Modelo": 
                        product_model = row_text[1]
                    if row_text[0] == "Marca":
                        product_brand = row_text[1]

                saveModelConverted = product_model.replace("/", "A") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                #.strip() remueve los espacios en blanco al inicio y al final de un string
                #print('disco duro',product_disco_duro)
                #size = len (product_disco_duro)
                #if product_disco_duro[:size+3]
                #print('disco duro',final_str)
                data = {
                    'product_detail': 'https://simple.ripley.com.pe' + product_detail_link,
                    'product_image': product_image,
                    'product_discount': product_discount,
                    'product_name': product_name,
                    'product_price': product_price,
                    'product_description': product_description,
                    'store': RIPLEY_STORE,
                    'category_group': TECNOLOGIA_GROUP_CATEGORY,
                    'category': COMPUTADORAS_CATEGORY,
                    'sub_category': LAPTOPS_SUBCATEGORY,
                    'brand': product_brand,
                    'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                    'model_store_unique_identifier':  RIPLEY_STORE + '_'+ product_brand + '_' + saveModelConverted .strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                    'pricekey': product_price + '_' +  RIPLEY_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                }
                #cambio = (data['model_store_unique_identifier']).rstrip('SDD')
                #print ('cambio',cambio)
                #if cambio[0:4] == ' SDD':
                    #cambio = cambio.strip['"']
                    #print ('cambio',cambio)
                    #cambio = cambio[1:-1]
                    
                #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                #eg: products/grupo-categoria/categoria/subcategoria
                path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, TELEVISORES_CATEGORY, QLED_SUBCATEGORY, data['model_store_unique_identifier'])
                result = firebase.patch(path, data) #creamos o actualizamos
                today = date.today()
                price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                if price_history:
                    price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                    result['price_history'] = price_history
                else:
                    result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                print('TODO CORRECTO!!!')
        except Exception:
            print("Producto no creado, error en el web scraping")
            print(product_name)
            traceback.print_exc() #podemos ver en donde estuvo el error
            continue #poner break en vez de continue para debuggear

def find_products_electrohogar_refigeradoras_Ripley():

#Find replay's products
    print('Ripley products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://simple.ripley.com.pe/electrohogar/refrigeracion/refrigeradoras?source=menu')
        scrolldownRipley("0",driver, 4623)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    prueba = soup.find('div', class_= "catalog-page__footer-pagination").find('nav').find('ul',class_="pagination").find_all('li')
    print ('prueba', prueba)
    primerapagina = prueba[1].text
    ultimapagina = prueba[len(prueba)-2].text
    print('primera',primerapagina)
    print ('ultima',ultimapagina)
    
    for i in range (int(primerapagina),int(ultimapagina)):

        driver = webdriver.Chrome(chrome_options=option)
        driver.get("about:blank")
        driver.maximize_window()
        try:
            driver.get('https://simple.ripley.com.pe/electrohogar/refrigeracion/refrigeradoras?source=menu&page='+str(i))
            scrolldownRipley("0",driver, 4623)
            html = driver.execute_script("return document.body.innerHTML;")
            print("Pagina mostrada")
        except Exception as e:
            print(e)
        finally:
            driver.quit()   
        soup = BeautifulSoup(html,'lxml')

        product_cards = soup.find_all('div', class_='catalog-product-item')
        count = 0
        product_name = ''
        for product_card in product_cards:
            try:
                    # count += 1
                # if count == 3:
                    product_detail_link = product_card.find('a', class_='catalog-product-item')['href'] #Obtener link detalle
                    driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
                    driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
                    driver.maximize_window()
                    try:
                        driver.get('https://simple.ripley.com.pe' + product_detail_link)
                        scrolldownRipley("0",driver, 3272, 0.01) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                        html = driver.execute_script("return document.body.innerHTML;")
                        print("Pagina mostrada")
                    except Exception as e:
                        print(e)
                    finally:
                        driver.quit()   

                    detail_link = BeautifulSoup(html, 'lxml')

                    #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
                    #with open('file7.txt', 'w') as file: 
                        #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas
                    
                    #obtenemos referencia a la tabla de especificaciones
                    tableReference = detail_link.find('table', class_='table table-striped')
                    product_brand = ''
                    product_model = ''

                    #Esto puede seer muy parecido para todas la e-commerces
                    for row in tableReference.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                        row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                        if row_text[0] == "Marca": #Encontramos la marca, modelo
                            product_brand = row_text[1]
                        if row_text[0] == "Modelo": 
                            product_model = row_text[1] 

                    recorte_model = (product_model).find('/PE')

                    print ('recorte',recorte_model)
                    print ('capacidad', product_model)

                    if recorte_model > 0:
                        size = len(product_model)
                        product_model = product_model[:size-3]
                        print ('nuevo', product_model)

                    if len(product_model) != 0:
                        print('PASO LA LECTURA!!! ... obteniendo datos!')
                        #Extraccion de datos
                        product_image = detail_link.find('ul', class_='product-image-previews').li.img['data-src'][2:] # quitale las 2 rayitas de adelante del string
                        product_name = detail_link.find('section', class_='product-header visible-xs').h1.text
                        product_discount = detail_link.find('span', class_='discount-percentage')
                        if product_discount:
                            product_discount = detail_link.find('span', class_='discount-percentage').text[1:-1] #solo quiero el numerotext.
                        else:
                            product_discount = 0

                        product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best')
                        if product_price:
                            product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best').dt.text.split()[1]
                        else:
                             product_price = detail_link.find('div', class_='product-price-container product-internet-price').dt.text.split()[1]

                        product_description = detail_link.find('h2', class_='product-short-description').text     

                        saveModelConverted = product_model #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                        #.strip() remueve los espacios en blanco al inicio y al final de un string
                        #print('disco duro',product_disco_duro)

                        #size = len (product_disco_duro)
                        #if product_disco_duro[:size+3]

                        #print('disco duro',final_str)

                        data = {
                            'product_detail': 'https://simple.ripley.com.pe' + product_detail_link,
                            'product_image': product_image,
                            'product_discount': product_discount,
                            'product_name': product_name,
                            'product_price': product_price,
                            'product_description': product_description,
                            'store': RIPLEY_STORE,
                            'category_group': ELECTROHOGAR_GROUP_CATEGORY,
                            'category': REFRIGERACION_CATEGORY,
                            'sub_category': REFIGERADORAS_SUBCATEGORY,
                            'brand': product_brand,
                            'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                            'model_store_unique_identifier':  RIPLEY_STORE + '_' + product_brand+ '_' + saveModelConverted.strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                            'pricekey': product_price + '_' +  RIPLEY_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                        }

                        #cambio = (data['model_store_unique_identifier']).rstrip('SDD')

                        #print ('cambio',cambio)

                        #if cambio[0:4] == ' SDD':
                            #cambio = cambio.strip['"']
                            #print ('cambio',cambio)
                            #cambio = cambio[1:-1]


                        #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                        #eg: products/grupo-categoria/categoria/subcategoria
                        path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(ELECTROHOGAR_GROUP_CATEGORY, REFRIGERACION_CATEGORY, REFIGERADORAS_SUBCATEGORY, data['model_store_unique_identifier'])
                        result = firebase.patch(path, data) #creamos o actualizamos
                        today = date.today()
                        price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                        if price_history:
                            price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                            result['price_history'] = price_history
                        else:
                            result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                        result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                        print('TODO CORRECTO!!!')
            except Exception:
                print("Producto no creado, error en el web scraping")
                print(product_name)
                traceback.print_exc() #podemos ver en donde estuvo el error
                continue #poner break en vez de continue para debuggear

def find_products_electrohogar_lavadoras_Ripley():

    #firebase.delete("/comparizy-test-default-rtdb/products/electrohogar/lavado/lavadoras", None)

    #Find replay's products
    print('Ripley products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://simple.ripley.com.pe/electrohogar/lavado/lavadoras?source=menu')
        scrolldownRipley("0",driver, 4623)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    prueba = soup.find('div', class_= "catalog-page__footer-pagination").find('nav').find('ul',class_="pagination").find_all('li')
    print ('prueba', prueba)
    primerapagina = prueba[1].text
    ultimapagina = prueba[len(prueba)-2].text
    print('primera',primerapagina)
    print ('ultima',ultimapagina)
    
    for i in range (int(primerapagina),int(ultimapagina)):

        driver = webdriver.Chrome(chrome_options=option)
        driver.get("about:blank")
        driver.maximize_window()
        try:
            driver.get('https://simple.ripley.com.pe/electrohogar/lavado/lavadoras?source=menu&page='+str(i))
            scrolldownRipley("0",driver, 4623)
            html = driver.execute_script("return document.body.innerHTML;")
            print("Pagina mostrada")
        except Exception as e:
            print(e)
        finally:
            driver.quit()   
        soup = BeautifulSoup(html,'lxml')

        product_cards = soup.find_all('div', class_='catalog-product-item')
        count = 0
        product_name = ''
        for product_card in product_cards:
            try:
                    # count += 1
                # if count == 3:
                    product_detail_link = product_card.find('a', class_='catalog-product-item')['href'] #Obtener link detalle
                    driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
                    driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
                    driver.maximize_window()
                    try:
                        driver.get('https://simple.ripley.com.pe' + product_detail_link)
                        scrolldownRipley("0",driver, 3272, 0.01) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                        html = driver.execute_script("return document.body.innerHTML;")
                        print("Pagina mostrada")
                    except Exception as e:
                        print(e)
                    finally:
                        driver.quit()   

                    detail_link = BeautifulSoup(html, 'lxml')

                    #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
                    #with open('file7.txt', 'w') as file: 
                        #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas
                    
                    #obtenemos referencia a la tabla de especificaciones
                    tableReference = detail_link.find('table', class_='table table-striped')
                    product_brand = ''
                    product_model = ''

                    #Esto puede seer muy parecido para todas la e-commerces
                    for row in tableReference.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                        row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                        if row_text[0] == "Marca": #Encontramos la marca, modelo
                            product_brand = row_text[1]
                        if row_text[0] == "Modelo": 
                            product_model = row_text[1] 

                    #print('MODELOOOOOOOOOOOOOO>>>>>>>>>>>>>>>>>', product_model)       

                    recorte_model = (product_model).find('/PE')

                    #print ('recorte',recorte_model)
                    #print ('capacidad', product_model)
#
                    if recorte_model > 0:
                        size = len(product_model)
                        product_model = product_model[:size-3]
                        print ('nuevo', product_model)

                    recorte_model2 = (product_model).find('.ABWGLGP')  

                    if recorte_model2 > 0:
                        size = len(product_model)
                        product_model = product_model[:size-8]
                        print ('nuevo', product_model)

                    recorte_model3 = (product_model).find('.ABLGLGP')  

                    if recorte_model3 > 0:
                        size = len(product_model)
                        product_model = product_model[:size-8]
                        print ('nuevo', product_model)

                    recorte_model4 = (product_model).find('.ASSGLGP')  

                    if recorte_model4 > 0:
                        size = len(product_model)
                        product_model = product_model[:size-8]
                        print ('nuevo', product_model)

                    recorte_model5 = (product_model).find('.ABMGLGP')  

                    if recorte_model5 > 0:
                        size = len(product_model)
                        product_model = product_model[:size-8]
                        print ('nuevo', product_model)

                    recorte_model6 = (product_model).find('.AESGLGP')  

                    if recorte_model6 > 0:
                        size = len(product_model)
                        product_model = product_model[:size-8]
                        print ('nuevo', product_model)

                    if len(product_model) != 0:
                        print('PASO LA LECTURA!!! ... obteniendo datos!')
                        #Extraccion de datos
                        product_image = detail_link.find('ul', class_='product-image-previews').li.img['data-src'][2:] # quitale las 2 rayitas de adelante del string
                        product_name = detail_link.find('section', class_='product-header visible-xs').h1.text
                        product_discount = detail_link.find('span', class_='discount-percentage')
                        if product_discount:
                            product_discount = detail_link.find('span', class_='discount-percentage').text[1:-1] #solo quiero el numerotext.
                        else:
                            product_discount = 0

                        product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best')
                        if product_price:
                            product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best').dt.text.split()[1]
                        else:
                             product_price = detail_link.find('div', class_='product-price-container product-internet-price').dt.text.split()[1]

                        product_description = detail_link.find('h2', class_='product-short-description').text     

                        saveModelConverted = product_model #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                        #.strip() remueve los espacios en blanco al inicio y al final de un string
                        #print('disco duro',product_disco_duro)

                        #size = len (product_disco_duro)
                        #if product_disco_duro[:size+3]

                        #print('disco duro',final_str)

                        data = {
                            'product_detail': 'https://simple.ripley.com.pe' + product_detail_link,
                            'product_image': product_image,
                            'product_discount': product_discount,
                            'product_name': product_name,
                            'product_price': product_price,
                            'product_description': product_description,
                            'store': RIPLEY_STORE,
                            'category_group': ELECTROHOGAR_GROUP_CATEGORY,
                            'category': LAVADO_CATEGORY,
                            'sub_category': LAVADORAS_SUBCATEGORY,
                            'brand': product_brand,
                            'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                            'model_store_unique_identifier':  RIPLEY_STORE + '_' + product_brand+ '_' + saveModelConverted.strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                            'pricekey': product_price + '_' +  RIPLEY_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                        }

                        #cambio = (data['model_store_unique_identifier']).rstrip('SDD')

                        #print ('cambio',cambio)

                        #if cambio[0:4] == ' SDD':
                            #cambio = cambio.strip['"']
                            #print ('cambio',cambio)
                            #cambio = cambio[1:-1]


                        #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                        #eg: products/grupo-categoria/categoria/subcategoria
                        path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(ELECTROHOGAR_GROUP_CATEGORY, LAVADO_CATEGORY, LAVADORAS_SUBCATEGORY, data['model_store_unique_identifier'])
                        result = firebase.patch(path, data) #creamos o actualizamos
                        today = date.today()
                        price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                        if price_history:
                            price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                            result['price_history'] = price_history
                        else:
                            result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                        result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                        print('TODO CORRECTO!!!')
            except Exception:
                print("Producto no creado, error en el web scraping")
                print(product_name)
                traceback.print_exc() #podemos ver en donde estuvo el error
                continue #poner break en vez de continue para debuggear           

def find_products_electrohogar_secadoras_Ripley():

    #firebase.delete("/comparizy-test-default-rtdb/products/electrohogar/lavado/secadoras", None)

    #Find replay's products
    print('Ripley products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://simple.ripley.com.pe/electrohogar/lavado/secadoras?source=menu')
        scrolldownRipley("0",driver, 4623)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    product_cards = soup.find_all('div', class_='catalog-product-item')
    count = 0
    product_name = ''
    for product_card in product_cards:
        try:
                # count += 1
            # if count == 3:
                product_detail_link = product_card.find('a', class_='catalog-product-item')['href'] #Obtener link detalle
                driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
                driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
                driver.maximize_window()
                try:
                    driver.get('https://simple.ripley.com.pe' + product_detail_link)
                    scrolldownRipley("0",driver, 3272, 0.01) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                    html = driver.execute_script("return document.body.innerHTML;")
                    print("Pagina mostrada")
                except Exception as e:
                    print(e)
                finally:
                    driver.quit()   
                detail_link = BeautifulSoup(html, 'lxml')
                #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
                #with open('file7.txt', 'w') as file: 
                    #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas
                
                #obtenemos referencia a la tabla de especificaciones
                tableReference = detail_link.find('table', class_='table table-striped')
                product_brand = ''
                product_model = ''
                #Esto puede seer muy parecido para todas la e-commerces
                for row in tableReference.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                    row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                    if row_text[0] == "Marca": #Encontramos la marca, modelo
                        product_brand = row_text[1]
                    if row_text[0] == "Modelo": 
                        product_model = row_text[1] 
                #print('MODELOOOOOOOOOOOOOO>>>>>>>>>>>>>>>>>', product_model)       
                recorte_model = (product_model).find('/PE')
                #print ('recorte',recorte_model)
                #print ('capacidad', product_model)

                #if recorte_model > 0:
                #    size = len(product_model)
                #    product_model = product_model[:size-3]
                #    print ('nuevo', product_model)
                #recorte_model2 = (product_model).find('.ABWGLGP')  
                #if recorte_model2 > 0:
                #    size = len(product_model)
                #    product_model = product_model[:size-8]
                #    print ('nuevo', product_model)
                #recorte_model3 = (product_model).find('.ABLGLGP')  
                #if recorte_model3 > 0:
                #    size = len(product_model)
                #    product_model = product_model[:size-8]
                #    print ('nuevo', product_model)
                #recorte_model4 = (product_model).find('.ASSGLGP')  
                #if recorte_model4 > 0:
                #    size = len(product_model)
                #    product_model = product_model[:size-8]
                #    print ('nuevo', product_model)
                #recorte_model5 = (product_model).find('.ABMGLGP')  
                #if recorte_model5 > 0:
                #    size = len(product_model)
                #    product_model = product_model[:size-8]
                #    print ('nuevo', product_model)
                #recorte_model6 = (product_model).find('.AESGLGP')  
                #if recorte_model6 > 0:
                #    size = len(product_model)
                #    product_model = product_model[:size-8]
                #    print ('nuevo', product_model)

                if len(product_model) != 0:
                    print('PASO LA LECTURA!!! ... obteniendo datos!')
                    #Extraccion de datos
                    product_image = detail_link.find('ul', class_='product-image-previews').li.img['data-src'][2:] # quitale las 2 rayitas de adelante del string
                    product_name = detail_link.find('section', class_='product-header visible-xs').h1.text
                    product_discount = detail_link.find('span', class_='discount-percentage')
                    if product_discount:
                        product_discount = detail_link.find('span', class_='discount-percentage').text[1:-1] #solo quiero el numerotext.
                    else:
                        product_discount = 0
                    product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best')
                    if product_price:
                        product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best').dt.text.split()[1]
                    else:
                         product_price = detail_link.find('div', class_='product-price-container product-internet-price').dt.text.split()[1]
                    product_description = detail_link.find('h2', class_='product-short-description').text     
                    saveModelConverted = product_model #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                    #.strip() remueve los espacios en blanco al inicio y al final de un string
                    #print('disco duro',product_disco_duro)
                    #size = len (product_disco_duro)
                    #if product_disco_duro[:size+3]
                    #print('disco duro',final_str)
                    data = {
                        'product_detail': 'https://simple.ripley.com.pe' + product_detail_link,
                        'product_image': product_image,
                        'product_discount': product_discount,
                        'product_name': product_name,
                        'product_price': product_price,
                        'product_description': product_description,
                        'store': RIPLEY_STORE,
                        'category_group': ELECTROHOGAR_GROUP_CATEGORY,
                        'category': LAVADO_CATEGORY,
                        'sub_category': SECADORAS_SUBCATEGORY,
                        'brand': product_brand,
                        'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                        'model_store_unique_identifier':  RIPLEY_STORE + '_' + product_brand+ '_' + saveModelConverted.strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                        'pricekey': product_price + '_' +  RIPLEY_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                    }
                    #cambio = (data['model_store_unique_identifier']).rstrip('SDD')
                    #print ('cambio',cambio)
                    #if cambio[0:4] == ' SDD':
                        #cambio = cambio.strip['"']
                        #print ('cambio',cambio)
                        #cambio = cambio[1:-1]
                    #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                    #eg: products/grupo-categoria/categoria/subcategoria
                    path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(ELECTROHOGAR_GROUP_CATEGORY, LAVADO_CATEGORY, SECADORAS_SUBCATEGORY, data['model_store_unique_identifier'])
                    result = firebase.patch(path, data) #creamos o actualizamos
                    today = date.today()
                    price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                    if price_history:
                        price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                        result['price_history'] = price_history
                    else:
                        result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                    result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                    print('TODO CORRECTO!!!')
        except Exception:
            print("Producto no creado, error en el web scraping")
            print(product_name)
            traceback.print_exc() #podemos ver en donde estuvo el error
            continue #poner break en vez de continue para debuggear  

def find_products_electrohogar_cocinadepie_Ripley():

    #firebase.delete("/comparizy-test-default-rtdb/products/electrohogar/cocina/cocinadepie", None)

    #Find replay's products
    print('Ripley products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://simple.ripley.com.pe/electrohogar/cocina/cocinas-de-pie?source=menu')
        scrolldownRipley("0",driver, 4623)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    prueba = soup.find('div', class_= "catalog-page__footer-pagination").find('nav').find('ul',class_="pagination").find_all('li')
    print ('prueba', prueba)
    primerapagina = prueba[1].text
    ultimapagina = prueba[len(prueba)-2].text
    print('primera',primerapagina)
    print ('ultima',ultimapagina)
    
    for i in range (int(primerapagina),int(ultimapagina)):

        driver = webdriver.Chrome(chrome_options=option)
        driver.get("about:blank")
        driver.maximize_window()
        try:
            driver.get('https://simple.ripley.com.pe/electrohogar/cocina/cocinas-de-pie?source=menu&page='+str(i))
            scrolldownRipley("0",driver, 4623)
            html = driver.execute_script("return document.body.innerHTML;")
            print("Pagina mostrada")
        except Exception as e:
            print(e)
        finally:
            driver.quit()   
        soup = BeautifulSoup(html,'lxml')

        product_cards = soup.find_all('div', class_='catalog-product-item')
        count = 0
        product_name = ''
        for product_card in product_cards:
            try:
                    # count += 1
                # if count == 3:
                    product_detail_link = product_card.find('a', class_='catalog-product-item')['href'] #Obtener link detalle
                    driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
                    driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
                    driver.maximize_window()
                    try:
                        driver.get('https://simple.ripley.com.pe' + product_detail_link)
                        scrolldownRipley("0",driver, 3272, 0.01) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                        html = driver.execute_script("return document.body.innerHTML;")
                        print("Pagina mostrada")
                    except Exception as e:
                        print(e)
                    finally:
                        driver.quit()   

                    detail_link = BeautifulSoup(html, 'lxml')

                    #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
                    #with open('file7.txt', 'w') as file: 
                        #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas
                    
                    #obtenemos referencia a la tabla de especificaciones
                    tableReference = detail_link.find('table', class_='table table-striped')
                    product_brand = ''
                    product_model = ''

                    #Esto puede seer muy parecido para todas la e-commerces
                    for row in tableReference.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                        row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                        if row_text[0] == "Marca": #Encontramos la marca, modelo
                            product_brand = row_text[1]
                        if row_text[0] == "Modelo": 
                            product_model = row_text[1] 

                    #print('MODELOOOOOOOOOOOOOO>>>>>>>>>>>>>>>>>', product_model)       

                    recorte_model = (product_model).find('/PE')

                    #print ('recorte',recorte_model)
                    #print ('capacidad', product_model)
#
                    #if recorte_model > 0:
                    #    size = len(product_model)
                    #    product_model = product_model[:size-3]
                    #    print ('nuevo', product_model)
#
                    #recorte_model2 = (product_model).find('.ABWGLGP')  
#
                    #if recorte_model2 > 0:
                    #    size = len(product_model)
                    #    product_model = product_model[:size-8]
                    #    print ('nuevo', product_model)
#
                    #recorte_model3 = (product_model).find('.ABLGLGP')  
#
                    #if recorte_model3 > 0:
                    #    size = len(product_model)
                    #    product_model = product_model[:size-8]
                    #    print ('nuevo', product_model)
#
                    #recorte_model4 = (product_model).find('.ASSGLGP')  
#
                    #if recorte_model4 > 0:
                    #    size = len(product_model)
                    #    product_model = product_model[:size-8]
                    #    print ('nuevo', product_model)
#
                    #recorte_model5 = (product_model).find('.ABMGLGP')  
#
                    #if recorte_model5 > 0:
                    #    size = len(product_model)
                    #    product_model = product_model[:size-8]
                    #    print ('nuevo', product_model)

                    #recorte_model6 = (product_model).find('.AESGLGP')  

                    #if recorte_model6 > 0:
                    #    size = len(product_model)
                    #    product_model = product_model[:size-8]
                    #    print ('nuevo', product_model)

                    if len(product_model) != 0:
                        print('PASO LA LECTURA!!! ... obteniendo datos!')
                        #Extraccion de datos
                        product_image = detail_link.find('ul', class_='product-image-previews').li.img['data-src'][2:] # quitale las 2 rayitas de adelante del string
                        product_name = detail_link.find('section', class_='product-header visible-xs').h1.text
                        product_discount = detail_link.find('span', class_='discount-percentage')
                        if product_discount:
                            product_discount = detail_link.find('span', class_='discount-percentage').text[1:-1] #solo quiero el numerotext.
                        else:
                            product_discount = 0

                        product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best')
                        if product_price:
                            product_price = detail_link.find('div', class_='product-price-container product-internet-price-not-best').dt.text.split()[1]
                        else:
                             product_price = detail_link.find('div', class_='product-price-container product-internet-price').dt.text.split()[1]

                        product_description = detail_link.find('h2', class_='product-short-description').text     

                        saveModelConverted = product_model #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                        #.strip() remueve los espacios en blanco al inicio y al final de un string
                        #print('disco duro',product_disco_duro)

                        #size = len (product_disco_duro)
                        #if product_disco_duro[:size+3]

                        #print('disco duro',final_str)

                        data = {
                            'product_detail': 'https://simple.ripley.com.pe' + product_detail_link,
                            'product_image': product_image,
                            'product_discount': product_discount,
                            'product_name': product_name,
                            'product_price': product_price,
                            'product_description': product_description,
                            'store': RIPLEY_STORE,
                            'category_group': ELECTROHOGAR_GROUP_CATEGORY,
                            'category': COCINA_CATEGORY,
                            'sub_category': COCINADEPIE_SUBCATEGORY,
                            'brand': product_brand,
                            'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                            'model_store_unique_identifier':  RIPLEY_STORE + '_' + product_brand+ '_' + saveModelConverted.strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                            'pricekey': product_price + '_' +  RIPLEY_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                        }

                        #cambio = (data['model_store_unique_identifier']).rstrip('SDD')

                        #print ('cambio',cambio)

                        #if cambio[0:4] == ' SDD':
                            #cambio = cambio.strip['"']
                            #print ('cambio',cambio)
                            #cambio = cambio[1:-1]


                        #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                        #eg: products/grupo-categoria/categoria/subcategoria
                        path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(ELECTROHOGAR_GROUP_CATEGORY, COCINA_CATEGORY, COCINADEPIE_SUBCATEGORY, data['model_store_unique_identifier'])
                        result = firebase.patch(path, data) #creamos o actualizamos
                        today = date.today()
                        price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                        if price_history:
                            price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                            result['price_history'] = price_history
                        else:
                            result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                        result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                        print('TODO CORRECTO!!!')
            except Exception:
                print("Producto no creado, error en el web scraping")
                print(product_name)
                traceback.print_exc() #podemos ver en donde estuvo el error
                continue #poner break en vez de continue para debuggear        

def find_products_tecnologia_computadoras_oeschle():

    #firebase.delete("/comparizy-test-default-rtdb/products/tecnologia/computadoras/", None)

    #Find oeschle's products
    print('Oeschle products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.oechsle.pe/tecnologia/computo/laptops/')
        scrolldownRipley("0",driver, 4142) #(document.body.scrollHeight)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)   
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    pagination = soup.find('div', class_= "light-theme simple-pagination").find('ul').find_all('li')
    print('pagination',pagination)
    primerapagina = pagination[1].text  
    ultimapagina =pagination[len(pagination)-2].text
    print('primera',primerapagina)
    print ('ultima',ultimapagina)
    
    for i in range (int(primerapagina),int(ultimapagina)):

        driver = webdriver.Chrome(chrome_options=option)
        driver.get("about:blank")
        driver.maximize_window()
        try:
            driver.get('https://www.oechsle.pe/tecnologia/computo/laptops/?&optionOrderBy=OrderByScoreDESC&page='+str(i))
            scrolldownRipley("0",driver, 4142) #(document.body.scrollHeight)
            html = driver.execute_script("return document.body.innerHTML;")
            print("Pagina mostrada")
        except Exception as e:
            print(e)   
        finally:
            driver.quit()   
        soup = BeautifulSoup(html,'lxml')

        product_cards = soup.find_all('li', class_='tecnologia-|-oechsle')
        count = 0
        product_name = ''
        for product_card in product_cards:
            try:
                # count += 1
                # if count == 1:
                product_detail_link = product_card.find('a', class_='prod-image')['href'] #Obtener link detalle
                driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
                driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
                driver.maximize_window()
                try:
                    driver.get(product_detail_link)
                    scrolldownRipley("0",driver, 5774, 0.001) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                    html = driver.execute_script("return document.body.innerHTML;")
                    print("Pagina mostrada")
                except Exception as e:
                    print(e)
                finally:
                    driver.quit()   

                detail_link = BeautifulSoup(html, 'lxml')

                #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
                #with open('file5.txt', 'w') as file: 
                    #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas

                product_procesador = detail_link.find('td',class_='value-field Procesador').text
                product_ram = detail_link.find('td',class_='value-field Memoria-RAM').text
                product_disco_duro = detail_link.find('td',class_='value-field Disco-Duro').text    

                #En Oeschle algunos productos no tienen modelo
                product_model = detail_link.find('td', class_='value-field Modelo')
                print("Tiene Modelo?", product_model)
                #si no tiene modelo se pasa por alto el resto del codigo para evitar inconsistencias

                if product_model is not None:
                    print('PASO LA LECTURA!!! ... obteniendo datos!')
                    #Extraccion de datos
                    product_model = detail_link.find('td', class_='value-field Modelo').text 
                    product_image = detail_link.find('img', class_='sku-rich-image-main')['src']
                    product_name = detail_link.find('div', class_='productName').text
                    product_discount = detail_link.find('span', class_='flag-of ml-10')
                    if product_discount:
                        product_discount = detail_link.find('span', class_='flag-of ml-10').text[1:-1] #solo quiero el numero
                    else:
                        product_discount = 0

                    product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')
                    if product_price:
                        product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')[len(product_price) - 1].text.split()[1]

                    product_description = detail_link.find('div', class_='text fz-15 lh-14 text-gray-light p-15').text
                    product_brand = detail_link.find('div', class_='brandName').a.text

                    saveModelConverted = product_model.replace("/", "A") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                    #.strip() remueve los espacios en blanco al inicio y al final de un string

                    data = {
                        'product_detail': product_detail_link,
                        'product_image': product_image,
                        'product_discount': product_discount,
                        'product_name': product_name,
                        'product_price': product_price,
                        'product_description': product_description,
                        'store': OESCHLE_STORE,
                        'category_group': TECNOLOGIA_GROUP_CATEGORY,
                        'category': COMPUTADORAS_CATEGORY,
                        'sub_category': LAPTOPS_SUBCATEGORY,
                        'brand': product_brand.strip(),
                        'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                        'model_store_unique_identifier':  OESCHLE_STORE + '_' + product_brand+ '_' + str(product_procesador)+ '_' + str(product_ram)+ '_' + str(product_disco_duro), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                        'pricekey': product_price + '_' +  OESCHLE_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                    }

                    recorte = (data['model_store_unique_identifier']).find("SSD")
                    cambio = (data['model_store_unique_identifier'])

                    print ('recorte',recorte)

                    if recorte > 0:
                        size = len(cambio)
                        cambio = cambio[:size - 4]
                        print ('cambio',cambio) 

                    #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                    #eg: products/grupo-categoria/categoria/subcategoria
                    path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, COMPUTADORAS_CATEGORY, LAPTOPS_SUBCATEGORY, cambio)
                    result = firebase.patch(path, data) #creamos o actualizamos
                    today = date.today()
                    price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                    if price_history:
                        price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                        result['price_history'] = price_history
                    else:
                        result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                    result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                    print('TODO CORRECTO!!!')
            except Exception:
                print("Producto no creado, error en el web scraping")
                print(product_name)
                traceback.print_exc() #podemos ver en donde estuvo el error
                continue #poner break en vez de continue para debuggear

#def find_products_tecnologia_tablets_oeschle():
#
#    firebase.delete("/comparizy-test-default-rtdb/products/tecnologia/computadoras/", None)
#    #Find oeschle's products 
#    print ('Oeschle Tablets products!!!')
#    print()
#
#    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
#    option.add_argument('disable-infobars')
#
#    driver = webdriver.Chrome(chrome_options=option)
#    driver.get("about:blank")
#    driver.maximize_window()
#    try:
#        driver.get('https://www.oechsle.pe/tecnologia/computo/tablets/')
#        scrolldownRipley("0",driver, 3933) #(document.body.scrollHeight)
#        html = driver.execute_script("return document.body.innerHTML;")
#        print("Pagina mostrada")
#    except Exception as e:
#        print(e)
#    finally:
#        driver.quit()   
#    soup = BeautifulSoup(html,'lxml')
#    product_cards = soup.find_all('li', class_='tecnologia-|-oechsle')
#    count = 0
#    product_name = ''
#    for product_card in product_cards:
#        try:
#            # count += 1
#            # if count == 1:
#            product_detail_link = product_card.find('a', class_='prod-image')['href'] #Obtener link detalle
#            driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
#            driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
#            driver.maximize_window()
#            try:
#                driver.get(product_detail_link)
#                scrolldownRipley("0",driver, 5413, 0.001) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
#                html = driver.execute_script("return document.body.innerHTML;")
#                print("Pagina mostrada")
#            except Exception as e:
#                print(e)
#            finally:
#                driver.quit()   
#            detail_link = BeautifulSoup(html, 'lxml')
#
#            #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
#            #with open('file5.txt', 'w') as file: 
#                #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas
#
#            #En Oeschle algunos productos no tienen modelo
#            product_model = detail_link.find('td', class_='value-field Modelo')
#            print("Tiene Modelo?", product_model)
#            #si no tiene modelo se pasa por alto el resto del codigo para evitar inconsistencias
#
#            if product_model is not None:
#                print('PASO LA LECTURA!!! ... obteniendo datos!')
#                #Extraccion de datos
#                product_model = detail_link.find('td', class_='value-field Modelo').text 
#                product_image = detail_link.find('img', class_='sku-rich-image-main')['src']
#                product_name = detail_link.find('div', class_='productName').text
#                product_discount = detail_link.find('span', class_='flag-of ml-10')
#                if product_discount:
#                    product_discount = detail_link.find('span', class_='flag-of ml-10').text[1:-1] #solo quiero el numero
#                else:
#                    product_discount = 0
#                    
#                product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')
#                if product_price:
#                    product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')[len(product_price) - 1].text.split()[1]
#
#                product_description = detail_link.find('div', class_='text fz-15 lh-14 text-gray-light p-15').text
#                product_brand = detail_link.find('div', class_='brandName').a.text
#                
#                saveModelConverted = product_model.replace("/", "A") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
#                #.strip() remueve los espacios en blanco al inicio y al final de un string
#                
#                data = {
#                    'product_detail': product_detail_link,
#                    'product_image': product_image,
#                    'product_discount': product_discount,
#                    'product_name': product_name,
#                    'product_price': product_price,
#                    'product_description': product_description,
#                    'store': OESCHLE_STORE,
#                    'category_group': TECNOLOGIA_GROUP_CATEGORY,
#                    'category': COMPUTADORAS_CATEGORY,
#                    'sub_category': TABLETS_SUBCATEGORY,
#                    'brand': product_brand,
#                    'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
#                    'model_store_unique_identifier':  OESCHLE_STORE + '_' + saveModelConverted.strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
#                    'pricekey': product_price + '_' +  OESCHLE_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
#                }
#
#                #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
#                #eg: products/grupo-categoria/categoria/subcategoria
#                path = "/comparizy-c73ab-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, COMPUTADORAS_CATEGORY, TABLETS_SUBCATEGORY, data['model_store_unique_identifier'])
#                result = firebase.patch(path, data) #creamos o actualizamos
#                today = date.today()
#                price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
#                if price_history:
#                    price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
#                    result['price_history'] = price_history
#                else:
#                    result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
#                result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
#                print('TODO CORRECTO!!!')
#        except Exception:
#            print("Producto no creado, error en el web scraping")
#            print(product_name)
#            traceback.print_exc() #podemos ver en donde estuvo el error
#            continue #poner break en vez de continue para debuggear

def find_products_tecnologia_televisoresOLED_oeschle():

    #firebase.delete("/comparizy-test-default-rtdb/products/tecnologia/televisores/oled", None)

    #Find oeschle's products
    print('Oeschle products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.oechsle.pe/tecnologia/televisores/oled-tv/')
        scrolldownRipley("0",driver, 4142) #(document.body.scrollHeight)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)   
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    product_cards = soup.find_all('li', class_='tecnologia-|-oechsle')
    count = 0
    product_name = ''
    for product_card in product_cards:
        try:
            # count += 1
            # if count == 1:
            product_detail_link = product_card.find('a', class_='prod-image')['href'] #Obtener link detalle
            driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
            driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
            driver.maximize_window()
            try:
                driver.get(product_detail_link)
                scrolldownRipley("0",driver, 5774, 0.001) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                html = driver.execute_script("return document.body.innerHTML;")
                print("Pagina mostrada")
            except Exception as e:
                print(e)
            finally:
                driver.quit()   
            detail_link = BeautifulSoup(html, 'lxml')
            #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
            #with open('file5.txt', 'w') as file: 
                #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas
              
            #En Oeschle algunos productos no tienen modelo
            product_model = detail_link.find('td', class_='value-field Modelo')
            print("Tiene Modelo?", product_model)
            #si no tiene modelo se pasa por alto el resto del codigo para evitar inconsistencias
            if product_model is not None:
                print('PASO LA LECTURA!!! ... obteniendo datos!')
                #Extraccion de datos
                product_model = detail_link.find('td', class_='value-field Modelo').text 
                product_image = detail_link.find('img', class_='sku-rich-image-main')['src']
                product_name = detail_link.find('div', class_='productName').text
                product_discount = detail_link.find('span', class_='flag-of ml-10')
                if product_discount:
                    product_discount = detail_link.find('span', class_='flag-of ml-10').text[1:-1] #solo quiero el numero
                else:
                    product_discount = 0
                product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')
                if product_price:
                    product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')[len(product_price) - 1].text.split()[1]
                product_description = detail_link.find('div', class_='text fz-15 lh-14 text-gray-light p-15').text
                product_brand = detail_link.find('div', class_='brandName').a.text
                saveModelConverted = product_model.replace("/", "A") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                #.strip() remueve los espacios en blanco al inicio y al final de un string
                data = {
                    'product_detail': product_detail_link,
                    'product_image': product_image,
                    'product_discount': product_discount,
                    'product_name': product_name,
                    'product_price': product_price,
                    'product_description': product_description,
                    'store': OESCHLE_STORE,
                    'category_group': TECNOLOGIA_GROUP_CATEGORY,
                    'category': COMPUTADORAS_CATEGORY,
                    'sub_category': LAPTOPS_SUBCATEGORY,
                    'brand': product_brand.strip(),
                    'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                    'model_store_unique_identifier':  OESCHLE_STORE + '_' + product_brand + '_' + saveModelConverted .strip() , #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                    'pricekey': product_price + '_' +  OESCHLE_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                }
                #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                #eg: products/grupo-categoria/categoria/subcategoria
                
                recorte = (data['model_store_unique_identifier']).find(".AWF")
                print ('recorte',recorte)

                cambio = (data['model_store_unique_identifier'])
                print ('cambio',cambio)
                if recorte > 0:
                    size =len(cambio)
                    cambio = cambio[:size - 4]
                    print ('cambio',cambio)

                path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, TELEVISORES_CATEGORY, OLED_SUBCATEGORY, cambio)
                result = firebase.patch(path, data) #creamos o actualizamos
                today = date.today()
                price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                if price_history:
                    price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                    result['price_history'] = price_history
                else:
                    result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                print('TODO CORRECTO!!!')
        except Exception:
            print("Producto no creado, error en el web scraping")
            print(product_name)
            traceback.print_exc() #podemos ver en donde estuvo el error
            continue #poner break en vez de continue para debuggear

def find_products_tecnologia_televisoresQLED_oeschle():

    #firebase.delete("/comparizy-test-default-rtdb/products/tecnologia/televisores/oled", None)

    #Find oeschle's products
    print('Oeschle products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.oechsle.pe/tecnologia/televisores/samsung-qled-tv/')
        scrolldownRipley("0",driver, 4142) #(document.body.scrollHeight)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)   
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    product_cards = soup.find_all('li', class_='tecnologia-|-oechsle')
    count = 0
    product_name = ''
    for product_card in product_cards:
        try:
            # count += 1
            # if count == 1:
            product_detail_link = product_card.find('a', class_='prod-image')['href'] #Obtener link detalle
            driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
            driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
            driver.maximize_window()
            try:
                driver.get(product_detail_link)
                scrolldownRipley("0",driver, 5774, 0.001) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                html = driver.execute_script("return document.body.innerHTML;")
                print("Pagina mostrada")
            except Exception as e:
                print(e)
            finally:
                driver.quit()   
            detail_link = BeautifulSoup(html, 'lxml')
            #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
            #with open('file5.txt', 'w') as file: 
                #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas
              
            #En Oeschle algunos productos no tienen modelo
            product_model = detail_link.find('td', class_='value-field Modelo')
            print("Tiene Modelo?", product_model)
            #si no tiene modelo se pasa por alto el resto del codigo para evitar inconsistencias
            if product_model is not None:
                print('PASO LA LECTURA!!! ... obteniendo datos!')
                #Extraccion de datos
                product_model = detail_link.find('td', class_='value-field Modelo').text 
                product_image = detail_link.find('img', class_='sku-rich-image-main')['src']
                product_name = detail_link.find('div', class_='productName').text
                product_discount = detail_link.find('span', class_='flag-of ml-10')
                if product_discount:
                    product_discount = detail_link.find('span', class_='flag-of ml-10').text[1:-1] #solo quiero el numero
                else:
                    product_discount = 0
                product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')
                if product_price:
                    product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')[len(product_price) - 1].text.split()[1]
                product_description = detail_link.find('div', class_='text fz-15 lh-14 text-gray-light p-15').text
                product_brand = detail_link.find('div', class_='brandName').a.text
                saveModelConverted = product_model.replace("/", "A") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                #.strip() remueve los espacios en blanco al inicio y al final de un string
                data = {
                    'product_detail': product_detail_link,
                    'product_image': product_image,
                    'product_discount': product_discount,
                    'product_name': product_name,
                    'product_price': product_price,
                    'product_description': product_description,
                    'store': OESCHLE_STORE,
                    'category_group': TECNOLOGIA_GROUP_CATEGORY,
                    'category': COMPUTADORAS_CATEGORY,
                    'sub_category': LAPTOPS_SUBCATEGORY,
                    'brand': product_brand.strip(),
                    'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                    'model_store_unique_identifier':  OESCHLE_STORE + '_' + product_brand + '_' + saveModelConverted .strip() , #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                    'pricekey': product_price + '_' +  OESCHLE_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                }
                #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                #eg: products/grupo-categoria/categoria/subcategoria
                
                recorte = (data['model_store_unique_identifier']).find(".AWF")
                print ('recorte',recorte)

                cambio = (data['model_store_unique_identifier'])
                print ('cambio',cambio)
                if recorte > 0:
                    size =len(cambio)
                    cambio = cambio[:size - 4]
                    print ('cambio',cambio)

                path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, TELEVISORES_CATEGORY, QLED_SUBCATEGORY, cambio)
                result = firebase.patch(path, data) #creamos o actualizamos
                today = date.today()
                price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                if price_history:
                    price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                    result['price_history'] = price_history
                else:
                    result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                print('TODO CORRECTO!!!')
        except Exception:
            print("Producto no creado, error en el web scraping")
            print(product_name)
            traceback.print_exc() #podemos ver en donde estuvo el error
            continue #poner break en vez de continue para debuggear

def find_products_electrohogar_refigeradoras_oeschle():

    #Find oeschle's products
    print('Oeschle products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.oechsle.pe/electrohogar/refrigeracion/refrigeradoras/')
        scrolldownRipley("0",driver, 4142) #(document.body.scrollHeight)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)   
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    pagination = soup.find('div', class_= "light-theme simple-pagination").find('ul').find_all('li')
    print('pagination',pagination)
    primerapagina = pagination[1].text  
    ultimapagina =pagination[len(pagination)-2].text
    print('primera',primerapagina)
    print ('ultima',ultimapagina)
    
    for i in range (int(primerapagina),int(ultimapagina)):

        driver = webdriver.Chrome(chrome_options=option)
        driver.get("about:blank")
        driver.maximize_window()
        try:
            driver.get('https://www.oechsle.pe/electrohogar/refrigeracion/refrigeradoras/?&optionOrderBy=&O=OrderByScoreDESC&page='+str(i))
            scrolldownRipley("0",driver, 4142) #(document.body.scrollHeight)
            html = driver.execute_script("return document.body.innerHTML;")
            print("Pagina mostrada")
        except Exception as e:
            print(e)   
        finally:
            driver.quit()   
        soup = BeautifulSoup(html,'lxml')

        product_cards = soup.find_all('li', class_='electrohogar-|-oechsle')
        count = 0
        product_name = ''
        for product_card in product_cards:
            try:
                # count += 1
                # if count == 1:
                product_detail_link = product_card.find('a', class_='prod-image')['href'] #Obtener link detalle
                driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
                driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
                driver.maximize_window()
                try:
                    driver.get(product_detail_link)
                    scrolldownRipley("0",driver, 5774, 0.001) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                    html = driver.execute_script("return document.body.innerHTML;")
                    print("Pagina mostrada")
                except Exception as e:
                    print(e)
                finally:
                    driver.quit()   

                detail_link = BeautifulSoup(html, 'lxml')

                #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
                #with open('file5.txt', 'w') as file: 
                    #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas   

                #En Oeschle algunos productos no tienen modelo
                product_model = detail_link.find('td', class_='value-field Modelo')
                print("Tiene Modelo?", product_model)
                #si no tiene modelo se pasa por alto el resto del codigo para evitar inconsistencias

                recorte_model = (product_model).find('/PE')

                print ('recorte',recorte_model)
                print ('capacidad', product_model)

                if recorte_model > 0:

                    size = len(product_model)
                    product_model = product_model[:size-3]
                    print ('nuevo', product_model)

                if product_model is not None:
                    print('PASO LA LECTURA!!! ... obteniendo datos!')
                    #Extraccion de datos
                    product_model = detail_link.find('td', class_='value-field Modelo').text 
                    product_image = detail_link.find('img', class_='sku-rich-image-main')['src']
                    product_name = detail_link.find('div', class_='productName').text
                    product_discount = detail_link.find('span', class_='flag-of ml-10')
                    if product_discount:
                        product_discount = detail_link.find('span', class_='flag-of ml-10').text[1:-1] #solo quiero el numero
                    else:
                        product_discount = 0

                    product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')
                    if product_price:
                        product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')[len(product_price) - 1].text.split()[1]

                    product_description = detail_link.find('div', class_='text fz-15 lh-14 text-gray-light p-15').text
                    product_brand = detail_link.find('div', class_='brandName').a.text

                    saveModelConverted = product_model.replace("/", "A") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                    #.strip() remueve los espacios en blanco al inicio y al final de un string

                    data = {
                        'product_detail': product_detail_link,
                        'product_image': product_image,
                        'product_discount': product_discount,
                        'product_name': product_name,
                        'product_price': product_price,
                        'product_description': product_description,
                        'store': OESCHLE_STORE,
                        'category_group': ELECTROHOGAR_GROUP_CATEGORY,
                        'category': REFRIGERACION_CATEGORY,
                        'sub_category': REFIGERADORAS_SUBCATEGORY,
                        'brand': product_brand.strip(),
                        'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                        'model_store_unique_identifier':  OESCHLE_STORE + '_' + product_brand+ '_' + saveModelConverted.strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                        'pricekey': product_price + '_' +  OESCHLE_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                    }

                    #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                    #eg: products/grupo-categoria/categoria/subcategoria
                    path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(ELECTROHOGAR_GROUP_CATEGORY, REFRIGERACION_CATEGORY, REFIGERADORAS_SUBCATEGORY, data['model_store_unique_identifier'])
                    result = firebase.patch(path, data) #creamos o actualizamos
                    today = date.today()
                    price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                    if price_history:
                        price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                        result['price_history'] = price_history
                    else:
                        result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                    result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                    print('TODO CORRECTO!!!')
            except Exception:
                print("Producto no creado, error en el web scraping")
                print(product_name)
                traceback.print_exc() #podemos ver en donde estuvo el error
                continue #poner break en vez de continue para debuggear


def find_products_electrohogar_lavadoras_oeschle():

    #Find oeschle's products
    print('Oeschle products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.oechsle.pe/electrohogar/lavado/lavadoras/')
        scrolldownRipley("0",driver, 4142) #(document.body.scrollHeight)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)   
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    pagination = soup.find('div', class_= "light-theme simple-pagination").find('ul').find_all('li')
    print('pagination',pagination)
    primerapagina = pagination[1].text  
    ultimapagina =pagination[len(pagination)-2].text
    print('primera',primerapagina)
    print ('ultima',ultimapagina)
    
    for i in range (int(primerapagina),int(ultimapagina)):

        driver = webdriver.Chrome(chrome_options=option)
        driver.get("about:blank")
        driver.maximize_window()
        try:
            driver.get('https://www.oechsle.pe/electrohogar/lavado/lavadoras/?&optionOrderBy=&O=OrderByScoreDESC&page='+str(i))
            scrolldownRipley("0",driver, 4142) #(document.body.scrollHeight)
            html = driver.execute_script("return document.body.innerHTML;")
            print("Pagina mostrada")
        except Exception as e:
            print(e)   
        finally:
            driver.quit()   
        soup = BeautifulSoup(html,'lxml')

        product_cards = soup.find_all('li', class_='electrohogar-|-oechsle')
        count = 0
        product_name = ''
        for product_card in product_cards:
            try:
                # count += 1
                # if count == 1:
                product_detail_link = product_card.find('a', class_='prod-image')['href'] #Obtener link detalle
                driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
                driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
                driver.maximize_window()
                try:
                    driver.get(product_detail_link)
                    scrolldownRipley("0",driver, 5774, 0.01) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                    html = driver.execute_script("return document.body.innerHTML;")
                    print("Pagina mostrada")
                except Exception as e:
                    print(e)
                finally:
                    driver.quit()   

                detail_link = BeautifulSoup(html, 'lxml')

                #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
                #with open('file5.txt', 'w') as file: 
                    #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas   

                #En Oeschle algunos productos no tienen modelo
                product_model = detail_link.find('td', class_='value-field Modelo')
                print("Tiene Modelo?", product_model)
                #si no tiene modelo se pasa por alto el resto del codigo para evitar inconsistencias

                #recorte_model = (product_model).find('/PE')
#
                #print ('recorte',recorte_model)
                #print ('capacidad', product_model)
#
                #if recorte_model > 0:
#
                #    size = len(product_model)
                #    product_model = product_model[:size - 3]
                #    print ('nuevo', product_model)
#
                if product_model is not None:
                    print('PASO LA LECTURA!!! ... obteniendo datos!')
                    #Extraccion de datos
                    product_model = detail_link.find('td', class_='value-field Modelo').text 
                    product_image = detail_link.find('img', class_='sku-rich-image-main')['src']
                    product_name = detail_link.find('div', class_='productName').text
                    product_discount = detail_link.find('span', class_='flag-of ml-10')
                    if product_discount:
                        product_discount = detail_link.find('span', class_='flag-of ml-10').text[1:-1] #solo quiero el numero
                    else:
                        product_discount = 0

                    product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')
                    if product_price:
                        product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')[len(product_price) - 1].text.split()[1]

                    product_description = detail_link.find('div', class_='text fz-15 lh-14 text-gray-light p-15').text
                    product_brand = detail_link.find('div', class_='brandName').a.text

                    saveModelConverted = product_model.replace("/", "A") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                    #.strip() remueve los espacios en blanco al inicio y al final de un string
                    saveModelConverted = product_model.replace("/PE", " ")

                    data = {
                        'product_detail': product_detail_link,
                        'product_image': product_image,
                        'product_discount': product_discount,
                        'product_name': product_name,
                        'product_price': product_price,
                        'product_description': product_description,
                        'store': OESCHLE_STORE,
                        'category_group': ELECTROHOGAR_GROUP_CATEGORY,
                        'category': LAVADO_CATEGORY,
                        'sub_category': LAVADORAS_SUBCATEGORY,
                        'brand': product_brand.strip(),
                        'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                        'model_store_unique_identifier':  OESCHLE_STORE + '_' + product_brand+ '_' + saveModelConverted.strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                        'pricekey': product_price + '_' +  OESCHLE_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                    }

                    #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                    #eg: products/grupo-categoria/categoria/subcategoria
                    path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(ELECTROHOGAR_GROUP_CATEGORY, LAVADO_CATEGORY, LAVADORAS_SUBCATEGORY, data['model_store_unique_identifier'])
                    result = firebase.patch(path, data) #creamos o actualizamos
                    today = date.today()
                    price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                    if price_history:
                        price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                        result['price_history'] = price_history
                    else:
                        result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                    result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                    print('TODO CORRECTO!!!')
            except Exception:
                print("Producto no creado, error en el web scraping")
                print(product_name)
                traceback.print_exc() #podemos ver en donde estuvo el error
                continue #poner break en vez de continue para debuggear

def find_products_electrohogar_secadoras_oeschle():

    #Find oeschle's products
    print('Oeschle products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.oechsle.pe/electrohogar/lavado/secadoras/')
        scrolldownRipley("0",driver, 4142) #(document.body.scrollHeight)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)   
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    product_cards = soup.find_all('li', class_='electrohogar-|-oechsle')
    count = 0
    product_name = ''
    for product_card in product_cards:
        try:
            # count += 1
            # if count == 1:
            product_detail_link = product_card.find('a', class_='prod-image')['href'] #Obtener link detalle
            driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
            driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
            driver.maximize_window()
            try:
                driver.get(product_detail_link)
                scrolldownRipley("0",driver, 5774, 0.001) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                html = driver.execute_script("return document.body.innerHTML;")
                print("Pagina mostrada")
            except Exception as e:
                print(e)
            finally:
                driver.quit()   
            detail_link = BeautifulSoup(html, 'lxml')
            #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
            #with open('file5.txt', 'w') as file: 
                #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas   
            #En Oeschle algunos productos no tienen modelo
            product_model = detail_link.find('td', class_='value-field Modelo')
            print("Tiene Modelo?", product_model)
            #si no tiene modelo se pasa por alto el resto del codigo para evitar inconsistencias
            recorte_model = (product_model).find("/PE")
            print ('recorte',recorte_model)
            
            #contar = len(product_model)
#
            #if contar > 0:
#
            #    size = len(product_model)
            #    product_model = product_model[:size-3]
            #    print ('nuevo', product_model)

            if product_model is not None:
                print('PASO LA LECTURA!!! ... obteniendo datos!')
                #Extraccion de datos
                product_model = detail_link.find('td', class_='value-field Modelo').text 
                product_image = detail_link.find('img', class_='sku-rich-image-main')['src']
                product_name = detail_link.find('div', class_='productName').text
                product_discount = detail_link.find('span', class_='flag-of ml-10')
                if product_discount:
                    product_discount = detail_link.find('span', class_='flag-of ml-10').text[1:-1] #solo quiero el numero
                else:
                    product_discount = 0
                product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')
                if product_price:
                    product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')[len(product_price) - 1].text.split()[1]
                product_description = detail_link.find('div', class_='text fz-15 lh-14 text-gray-light p-15').text
                product_brand = detail_link.find('div', class_='brandName').a.text
                saveModelConverted = product_model.replace("/PE", " ") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                #.strip() remueve los espacios en blanco al inicio y al final de un string
                data = {
                    'product_detail': product_detail_link,
                    'product_image': product_image,
                    'product_discount': product_discount,
                    'product_name': product_name,
                    'product_price': product_price,
                    'product_description': product_description,
                    'store': OESCHLE_STORE,
                    'category_group': ELECTROHOGAR_GROUP_CATEGORY,
                    'category': LAVADO_CATEGORY,
                    'sub_category': SECADORAS_SUBCATEGORY,
                    'brand': product_brand.strip(),
                    'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                    'model_store_unique_identifier':  OESCHLE_STORE + '_' + product_brand+ '_' + saveModelConverted.strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                    'pricekey': product_price + '_' +  OESCHLE_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                }
                #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                #eg: products/grupo-categoria/categoria/subcategoria
                path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(ELECTROHOGAR_GROUP_CATEGORY, LAVADO_CATEGORY, SECADORAS_SUBCATEGORY, data['model_store_unique_identifier'])
                result = firebase.patch(path, data) #creamos o actualizamos
                today = date.today()
                price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                if price_history:
                    price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                    result['price_history'] = price_history
                else:
                    result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                print('TODO CORRECTO!!!')
        except Exception:
            print("Producto no creado, error en el web scraping")
            print(product_name)
            traceback.print_exc() #podemos ver en donde estuvo el error
            continue #poner break en vez de continue para debuggear           

def find_products_electrohogar_cocinadepie_oeschle():

    #Find oeschle's products
    print('Oeschle products!!!')
    print()

    option = webdriver.ChromeOptions() #ver https://www.programmersought.com/article/30255594749/
    option.add_argument('disable-infobars')

    driver = webdriver.Chrome(chrome_options=option)
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.oechsle.pe/electrohogar/cocina/cocinas-de-pie/')
        scrolldownRipley("0",driver, 4142) #(document.body.scrollHeight)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)   
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')

    pagination = soup.find('div', class_= "light-theme simple-pagination").find('ul').find_all('li')
    print('pagination',pagination)
    primerapagina = pagination[1].text  
    ultimapagina =pagination[len(pagination)-2].text
    print('primera',primerapagina)
    print ('ultima',ultimapagina)
    
    for i in range (int(primerapagina),int(ultimapagina)):

        driver = webdriver.Chrome(chrome_options=option)
        driver.get("about:blank")
        driver.maximize_window()
        try:
            driver.get('https://www.oechsle.pe/electrohogar/cocina/cocinas-de-pie/?&optionOrderBy=&O=OrderByScoreDESC&page='+str(i))
            scrolldownRipley("0",driver, 4142) #(document.body.scrollHeight)
            html = driver.execute_script("return document.body.innerHTML;")
            print("Pagina mostrada")
        except Exception as e:
            print(e)   
        finally:
            driver.quit()   
        soup = BeautifulSoup(html,'lxml')

        product_cards = soup.find_all('li', class_='electrohogar-|-oechsle')
        count = 0
        product_name = ''
        for product_card in product_cards:
            try:
                # count += 1
                # if count == 1:
                product_detail_link = product_card.find('a', class_='prod-image')['href'] #Obtener link detalle
                driver = driver = webdriver.Chrome(chrome_options=option) #debemos de crear un nuevo driver y scrollear la pagina dado que es la
                driver.get("about:blank") #unica forma de obtener todo el html completo (comprobado)
                driver.maximize_window()
                try:
                    driver.get(product_detail_link)
                    scrolldownRipley("0",driver, 5774, 0.001) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                    html = driver.execute_script("return document.body.innerHTML;")
                    print("Pagina mostrada")
                except Exception as e:
                    print(e)
                finally:
                    driver.quit()   

                detail_link = BeautifulSoup(html, 'lxml')

                #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
                #with open('file5.txt', 'w') as file: 
                    #file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas   

                #En Oeschle algunos productos no tienen modelo
                product_model = detail_link.find('td', class_='value-field Modelo')
                print("Tiene Modelo?", product_model)
                #si no tiene modelo se pasa por alto el resto del codigo para evitar inconsistencias

                #recorte_model = (product_model).find('/PE')
#
                #print ('recorte',recorte_model)
                #print ('capacidad', product_model)
#
                #if recorte_model > 0:
#
                #    size = len(product_model)
                #    product_model = product_model[:size-3]
                #    print ('nuevo', product_model)
#
                if product_model is not None:
                    print('PASO LA LECTURA!!! ... obteniendo datos!')
                    #Extraccion de datos
                    product_model = detail_link.find('td', class_='value-field Modelo').text 
                    product_image = detail_link.find('img', class_='sku-rich-image-main')['src']
                    product_name = detail_link.find('div', class_='productName').text
                    product_discount = detail_link.find('span', class_='flag-of ml-10')
                    if product_discount:
                        product_discount = detail_link.find('span', class_='flag-of ml-10').text[1:-1] #solo quiero el numero
                    else:
                        product_discount = 0

                    product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')
                    if product_price:
                        product_price = detail_link.find_all('span', class_='text fz-17 text-brown fw-bold')[len(product_price) - 1].text.split()[1]

                    product_description = detail_link.find('div', class_='text fz-15 lh-14 text-gray-light p-15').text
                    product_brand = detail_link.find('div', class_='brandName').a.text

                    saveModelConverted = product_model.replace("/PE", " ") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                    #.strip() remueve los espacios en blanco al inicio y al final de un string

                    data = {
                        'product_detail': product_detail_link,
                        'product_image': product_image,
                        'product_discount': product_discount,
                        'product_name': product_name,
                        'product_price': product_price,
                        'product_description': product_description,
                        'store': OESCHLE_STORE,
                        'category_group': ELECTROHOGAR_GROUP_CATEGORY,
                        'category': COCINA_CATEGORY,
                        'sub_category': COCINADEPIE_SUBCATEGORY,
                        'brand': product_brand.strip(),
                        'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                        'model_store_unique_identifier':  OESCHLE_STORE + '_' + product_brand+ '_' + saveModelConverted.strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                        'pricekey': product_price + '_' +  OESCHLE_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                    }

                    #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                    #eg: products/grupo-categoria/categoria/subcategoria
                    path = "/comparizy-test-default-rtdb/products/%s/%s/%s/%s"%(ELECTROHOGAR_GROUP_CATEGORY, COCINA_CATEGORY, COCINADEPIE_SUBCATEGORY, data['model_store_unique_identifier'])
                    result = firebase.patch(path, data) #creamos o actualizamos
                    today = date.today()
                    price_history = firebase.get(path+'/price_history', None) #verificamos si tienen historial de precios
                    if price_history:
                        price_history.append({'fecha': str(today), 'price': result['product_price']}) #si existe se concatena
                        result['price_history'] = price_history
                    else:
                        result['price_history'] = [{'fecha': str(today), 'price': result['product_price']}] #si no existe se crea
                    result = firebase.patch(path, result) #se vuelve a guardar con esta ultma adicion
                    print('TODO CORRECTO!!!')
            except Exception:
                print("Producto no creado, error en el web scraping")
                print(product_name)
                traceback.print_exc() #podemos ver en donde estuvo el error
                continue #poner break en vez de continue para debuggear