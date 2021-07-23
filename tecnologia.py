
from utils import *
from constants import *
from firebase import firebase
from bs4 import BeautifulSoup
import re
import requests
from selenium import webdriver
import time
from datetime import date


firebase = firebase.FirebaseApplication("https://comparizy-c73ab-default-rtdb.firebaseio.com/", None)

def find_products_tecnologia_computadoras_saga():
    #procesador, disco duro, memoria y marca. (en vez del modelo)

    #eg: products/grupo-categoria/categoria/subcategoria
    #Trabajamos con constantes (MAYUSCULAS) para evitar problemas de tipado
        
    #Analizar el siguiente detalle de producto como referencia 
    #https://www.falabella.com.pe/falabella-pe/product/882222620/Laptop-Lenovo-81WD00U9US-14-FHD-Core-i5-1035G1,8GB,512GB-SSD,-Platinium-Grey,-Teclado-en-ingles/882222620
    #Se recomienda probar linea por linea haciendo print de cada variable si se necesita comprender el código

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
    product_cards = soup.find_all('div', class_='jsx-1172968660 pod') #Obtener todas las filas de productos
    count = 0
    product_name = ''
    for product_card in product_cards: #Iterar todas las filas de productos
        try:
            count += 1
            product_detail_link = product_card.find('a', class_='jsx-3128226947')['href'] #Obtener link detalle
            html_text_desc = requests.get(product_detail_link).text #Obtenemos HTML de pagina detalle 
            detail_link = BeautifulSoup(html_text_desc, 'lxml')

            #Extraccion de datos

            product_image = detail_link.find('img', class_='jsx-2487856160')['src']
            product_discount = detail_link.find_all('span', class_='jsx-51363394') #Hay dos elementos con clases iguales en este caso

            #Obtenemos el que nos interesa del arreglo y extraemos solo los digitos
            product_discount = re.findall(r'\d+', product_discount[len(product_discount) - 1].text)[0] 
            product_brand = detail_link.find('a', class_='jsx-3572928369').text
            product_name = detail_link.find('div', class_='jsx-3686231685').text
            has_icon = detail_link.find('li', class_='jsx-3342506598 price-0').div.i
            if has_icon:
                product_price = detail_link.find('li', class_='jsx-3342506598 price-1').div.span.text.split()[1] #Obtener solo los numeros no caracteres
            else:
                product_price = detail_link.find('li', class_='jsx-3342506598 price-0').div.span.text.split()[1] #Obtener solo los numeros no caracteres
            
            product_description = detail_link.find('div', class_='jsx-3624412160 specifications-list').text #Podemos agregar clases separadas por un solo espacio para mayor especificidad y evitar conflictos con otros elementos
            product_model = ''

            #Esto puede seer muy parecido para todas la e-commerces
            for row in detail_link.select('tbody tr'): #Obtenemos el tbody de donde sacamos todas especificaciones
                row_text = [x.text for x in row.find_all('td')] #interamos cada especificacion
                if row_text[0] == "Modelo": #Encontramos el modelo y los asignamos a product_model
                    product_model = row_text[1]

            saveModelConverted = product_model.replace("/", "A") #El backslash genera un anidamiento automatico en firebase (con esto se evita)

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
                'model_store_unique_identifier':  SAGA_STORE + '_' + saveModelConverted, #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                'pricekey': product_price + '_' +  SAGA_STORE + '_' + saveModelConverted #Para poder hacer paginación ordenada por precio en el app
            }

            #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
            #eg: products/grupo-categoria/categoria/subcategoria
            path = "/comparizy-c73ab-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, COMPUTADORAS_CATEGORY, LAPTOPS_SUBCATEGORY, data['model_store_unique_identifier'])
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
                    scrolldownRipley("0",driver, 3298, 0.01) #obtener el tamaño de la pagina de detalle (document.body.scrollHeight)
                    html = driver.execute_script("return document.body.innerHTML;")
                    print("Pagina mostrada")
                except Exception as e:
                    print(e)
                finally:
                    driver.quit()   

                detail_link = BeautifulSoup(html, 'lxml')

                #guarda en text files el html y analiza donde esta el texto que buscas (el archivo de texto no debe existir para crearlo) 
                with open('file4.txt', 'w') as file: 
                    file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas

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
                    if row_text[0] == "Marca": #Encontramos la marca, modelo
                        product_brand = row_text[1]
                    if row_text[0] == "Modelo": 
                        product_model = row_text[1]
                
                saveModelConverted = product_model.replace("/", "A") #El backslash genera un anidamiento automatico en firebase (con esto se evita)
                #.strip() remueve los espacios en blanco al inicio y al final de un string
                
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
                    'model_store_unique_identifier':  RIPLEY_STORE + '_' + saveModelConverted.strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                    'pricekey': product_price + '_' +  RIPLEY_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                }

                #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                #eg: products/grupo-categoria/categoria/subcategoria
                path = "/comparizy-c73ab-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, COMPUTADORAS_CATEGORY, LAPTOPS_SUBCATEGORY, data['model_store_unique_identifier'])
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
            with open('file5.txt', 'w') as file: 
                file.write(detail_link.prettify())  #analiza el html de la web y coteja con lo que tengas

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
                    'product_detail': 'https://simple.ripley.com.pe' + product_detail_link,
                    'product_image': product_image,
                    'product_discount': product_discount,
                    'product_name': product_name,
                    'product_price': product_price,
                    'product_description': product_description,
                    'store': OESCHLE_STORE,
                    'category_group': TECNOLOGIA_GROUP_CATEGORY,
                    'category': COMPUTADORAS_CATEGORY,
                    'sub_category': LAPTOPS_SUBCATEGORY,
                    'brand': product_brand,
                    'model': product_model.strip(), #Para poder hacer la comparación con el mismo producto en otras tiendas
                    'model_store_unique_identifier':  OESCHLE_STORE + '_' + saveModelConverted.strip(), #Para identificar el producto y actualizarlo (no eliminamos los productos, sino que actualizamos el registro y las variaciones de precios)
                    'pricekey': product_price + '_' +  OESCHLE_STORE + '_' + saveModelConverted .strip()#Para poder hacer paginación ordenada por precio en el app
                }

                #%s se reemplaza por el valor de cada constante en el orden en que aparecen: tecnologia/computadoras/laptops/model_store_unique_identifier
                #eg: products/grupo-categoria/categoria/subcategoria
                path = "/comparizy-c73ab-default-rtdb/products/%s/%s/%s/%s"%(TECNOLOGIA_GROUP_CATEGORY, COMPUTADORAS_CATEGORY, LAPTOPS_SUBCATEGORY, data['model_store_unique_identifier'])
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

# Realizar la misma tarea con las demas subcategorias de la categoría computadora 
# Realizar el mismo procedimiento (el html puede variar entre e-commerce pero el código no debe ser muy distinto)

#    #Tablets (Doesn't work yet check html)
#    print('Saga products!!!')
#    print()
#    html_text = requests.get('https://www.falabella.com.pe/falabella-pe/category/cat270476/Tablets').text
#    soup = BeautifulSoup(html_text, 'lxml')
#    product_cards = soup.find_all('div', class_='jsx-1802348960')
#    for product_card in product_cards:
#        try:
#            product_detail_link = product_card.find('a', class_='jsx-3128226947')['href']
#            product_image = product_card.find('a', class_='jsx-3128226947').img['src']
#            product_discount = re.findall(r'\d+', product_card.find('div', class_='pod-badges-LIST').span.text)[0]
#            product_detail_grid = product_card.find('a', class_='section-body')
#            product_brand = product_detail_grid.find('div', class_='jsx-1802348960').b.text
#            product_name = product_detail_grid.find('span').b.text
#            product_price = product_detail_grid.find('div', class_='section-body--right').text.split()[2]
#            product_description = product_card.find('ul', class_='section__pod-bottom-description').text
#
#            print('product_detail', product_detail_link)
#            print('product_image', product_image)
#            print('product_discount', product_discount)
#            print('product_brand', product_brand)
#            print('product_name', product_name)
#            print('product_price', product_price)
#            print('product_description', product_description)
#
#            data = {
#                'product_detail': product_detail_link,
#                'product_image': product_image,
#                'product_discount': product_discount,
#                'product_name': product_name,
#                'product_price': product_price,
#                'product_description': product_description,
#                'store': 'SF',
#                'category': 'Tecnología',
#                'sub_category': 'Computadoras',
#                'sub_sub_category': 'Tablets',
#                'brand': product_brand
#            }
#
#            result = firebase.post("/comparizy-c73ab-default-rtdb/products/tecnologia/computadoras/tablets", data)
#            print(result)
#        except:
#            continue
#
    #Find replay's products
#    print('Ripley products!!!')
#    print()
#    html_text = requests.get('https://simple.ripley.com.pe/tecnologia/computacion/laptops?source=menu').text
#    soup = BeautifulSoup(html_text, 'lxml')
#    product_cards = soup.find_all('div', class_='catalog-product-item')
#    for product_card in product_cards:
#        try:
#            product_detail_link = product_card.find('a', class_='catalog-product-item')['href']
#            product_image = product_card.find('div', class_='images-preview-item').img['data-src']
#            product_detail_grid = product_card.find('a', class_='catalog-product-details')
#            product_discount = re.findall(r'\d+', product_card.find('div', class_='catalog-product-details__discount-tag').text)[0]
#            product_brand = product_card.find('div', class_='brand-logo').span.text
#            product_name = product_card.find('div', class_='catalog-product-details__name').text
#            product_price = product_card.find('li', class_='catalog-prices__offer-price catalog-prices__highest').text.split()[1]
#
#            html_text_desc = requests.get('https://simple.ripley.com.pe'+product_detail_link).text
#            soup2 = BeautifulSoup(html_text_desc, 'lxml')
#            product_description = soup2.find('h2', class_='product-short-description').text
#
#            print('product_detail', 'https://simple.ripley.com.pe'+product_detail_link)
#            print('product_image', 'https:'+product_image)
#            print('product_discount', product_discount)
#            print('product_brand', product_brand)
#            print('product_name', product_name)
#            print('product_price', product_price)
#            print('product_description', product_description)
#
#            data = {
#                'product_detail': 'https://simple.ripley.com.pe'+product_detail_link,
#                'product_image': 'https:'+product_image,
#                'product_discount': product_discount,
#                'product_name': product_name,
#                'product_price': product_price,
#                'product_description': product_description,
#                'store': 'RI',
#                'category': 'Tecnología',
#                'sub_category': 'Computadoras',
#                'sub_sub_category': 'Laptops',
#                'brand': product_brand
#            }
#
#            result = firebase.post("/comparizy-c73ab-default-rtdb/products/tecnologia/computadoras/laptops", data)
#            print(result)
#        except:
#            continue
#
#    #Find oeschle's products
#    print('Oeschle products!!!')
#    print()
#    html_text = requests.get('https://www.oechsle.pe/tecnologia/computo/laptops/').text
#    soup = BeautifulSoup(html_text, 'lxml')
#    product_cards = soup.find_all('li', class_='tecnologia-|-oechsle')
#    for product_card in product_cards:
#        try:
#            product_detail_link = product_card.find('a', class_='prod-image')['href']
#            product_image = product_card.find('div', class_='productImage').img['src']
#            product_discount = re.findall(r'\d+', product_card.find('span', class_='flag-of ml-10').text)[0]
#            product_brand = product_card.find('p', class_='brand').text
#            product_name = product_card.find('span', class_='prod-name').text
#            product_price = product_card.find('span', class_='BestPrice').text.split()[1]
#
#            # html_text_desc = requests.get(product_detail_link)
#            # soup = BeautifulSoup(html_text_desc, 'lxml')
#            # product_description = soup.find('table', class_="group Ficha-Tecnica table -striped text fz-15").text
#
#            print('product_detail', product_detail_link)
#            print('product_image', product_image)
#            print('product_discount', product_discount)
#            print('product_brand', product_brand)
#            print('product_name', product_name)
#            print('product_price', product_price)
#            print('product_description', product_name)
#            print()
#            
#            data = {
#                'product_detail': product_detail_link,
#                'product_image': product_image,
#                'product_discount': product_discount,
#                'product_name': product_name,
#                'product_price': product_price,
#                'product_description': product_description,
#                'store': 'OE',
#                'category': 'Tecnología',
#                'sub_category': 'Computadoras',
#                'sub_sub_category': 'Laptops',
#                'brand': product_brand
#            }
#
#            result = firebase.post("/comparizy-c73ab-default-rtdb/products/tecnologia/computadoras/laptops", data)
#            print(result)
#        except:
#            continue




def find_products_tecnologia_televisores():
    #Clean database
    #eg: products/categoria/subcategoria/
    firebase.delete("/comparizy-c73ab-default-rtdb/products/tecnologia/televisores/", None)

    #Find saga's products
    #LED
    print('Saga products!!!')
    print()
    driver = webdriver.Chrome()
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.falabella.com.pe/falabella-pe/category/cat6370551/Televisores-LED')
        scrolldownDepreceted("0",driver)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit()   
    soup = BeautifulSoup(html,'lxml')
    #html_text = requests.get('https://www.falabella.com.pe/falabella-pe/category/cat6370551/Televisores-LED').text
    #soup = BeautifulSoup(html_text, 'lxml')
    #fic = open("prueba", "w")
    #fic.write(html_text)
    #fic.close
    product_cards = soup.find_all('div', class_='jsx-1172968660 pod')
    for product_card in product_cards:
        try:
            product_detail_link = product_card.find('a', class_='jsx-3128226947')['href']
            product_image = product_card.find('a', class_='jsx-3128226947').img['src']
            product_discount = re.findall(r'\d+', product_card.find('div', class_='pod-badges-LIST').span.text)[0]
            product_detail_grid = product_card.find('a', class_='section-body')
            product_brand = product_detail_grid.find('div', class_='jsx-1172968660').b.text
            product_name = product_detail_grid.find('span').b.text
            product_price = product_detail_grid.find('div', class_='section-body--right').text.split()[2]
            product_description = product_card.find('ul', class_='section__pod-bottom-description').text

            print('product_detail', product_detail_link)
            print('product_image', product_image)
            print('product_discount', product_discount)
            print('product_brand', product_brand)
            print('product_name', product_name)
            print('product_price', product_price)
            print('product_description', product_description)

            data = {
                'product_detail': product_detail_link,
                'product_image': product_image,
                'product_discount': product_discount,
                'product_name': product_name,
                'product_price': product_price,
                'product_description': product_description,
                'store': 'SF',
                'category': 'Tecnología',
                'sub_category': 'Televisores',
                'sub_sub_category': 'LED',
                'brand': product_brand
            }

            #eg: products/categoria/subcateogria/sub-subcategoria
            result = firebase.post("/comparizy-c73ab-default-rtdb/products/tecnologia/televisores/LED", data)
            print(result)
        except:
            print("Producto no creado, error en el web scraping")
            continue

    #Find replay's products
    print('Ripley products!!!')
    print()
    driver = webdriver.Chrome()
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://simple.ripley.com.pe/tecnologia/tv-y-cine-en-casa/televisores?facet=Tecnolog%C3%ADa%20de%20Pantalla%3ALED')
        scrolldown("0",driver)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit() 
    soup = BeautifulSoup(html, 'lxml')
    product_cards = soup.find_all('div', class_='catalog-product-item')
    for product_card in product_cards:
        try:
            product_detail_link = product_card.find('a', class_='catalog-product-item')['href']
            product_image = product_card.find('div', class_='images-preview-item').img['data-src']
            product_detail_grid = product_card.find('a', class_='catalog-product-details')
            product_discount = re.findall(r'\d+', product_card.find('div', class_='catalog-product-details__discount-tag').text)[0]
            product_brand = product_card.find('div', class_='brand-logo').span.text
            product_name = product_card.find('div', class_='catalog-product-details__name').text
            product_price = product_card.find('li', class_='catalog-prices__offer-price catalog-prices__highest').text.split()[1]

            html_text_desc = requests.get('https://simple.ripley.com.pe'+product_detail_link).text
            soup2 = BeautifulSoup(html_text_desc, 'lxml')
            product_description = soup2.find('h2', class_='product-short-description').text

            print('product_detail', 'https://simple.ripley.com.pe'+product_detail_link)
            print('product_image', 'https:'+product_image)
            print('product_discount', product_discount)
            print('product_brand', product_brand)
            print('product_name', product_name)
            print('product_price', product_price)
            print('product_description', product_description)

            data = {
                'product_detail': 'https://simple.ripley.com.pe'+product_detail_link,
                'product_image': 'https:'+product_image,
                'product_discount': product_discount,
                'product_name': product_name,
                'product_price': product_price,
                'product_description': product_description,
                'store': 'RI',
                'category': 'Tecnología',
                'sub_category': 'Computadoras',
                'sub_sub_category': 'Laptops',
                'brand': product_brand
            }

            #eg: products/categoria/subcateogria/sub-subcategoria
            result = firebase.post("/comparizy-c73ab-default-rtdb/products/tecnologia/televisores/LED", data)
            print(result)
        except:
            continue      

    #Find oeschle's products
    print('Oeschle products!!!')
    print()
    driver = webdriver.Chrome()
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.oechsle.pe/tecnologia/televisores/?search=P:[489%20TO%2021999],specificationFilter_4561:LED&page=1')
        scrolldown("0",driver)
        html = driver.execute_script("return document.body.innerHTML;")
        print("Pagina mostrada")
    except Exception as e:
        print(e)
    finally:
        driver.quit() 
    soup = BeautifulSoup(html, 'lxml')
    product_cards = soup.find_all('li', class_='tecnologia-|-oechsle')
    for product_card in product_cards:
        try:
            product_detail_link = product_card.find('a', class_='prod-image')['href']
            product_image = product_card.find('div', class_='productImage').img['src']
            product_discount = re.findall(r'\d+', product_card.find('span', class_='flag-of ml-10').text)[0]
            product_brand = product_card.find('p', class_='brand').text
            product_name = product_card.find('span', class_='prod-name').text
            product_price = product_card.find('span', class_='BestPrice').text.split()[1]

            # html_text_desc = requests.get(product_detail_link)
            # soup = BeautifulSoup(html_text_desc, 'lxml')
            # product_description = soup.find('table', class_="group Ficha-Tecnica table -striped text fz-15").text

            print('product_detail', product_detail_link)
            print('product_image', product_image)
            print('product_discount', product_discount)
            print('product_brand', product_brand)
            print('product_name', product_name)
            print('product_price', product_price)
            print('product_description', product_name)
            print()
            
            data = {
                'product_detail': product_detail_link,
                'product_image': product_image,
                'product_discount': product_discount,
                'product_name': product_name,
                'product_price': product_price,
                'product_description': product_description,
                'store': 'OE',
                'category': 'Tecnología',
                'sub_category': 'Computadoras',
                'sub_sub_category': 'Laptops',
                'brand': product_brand
            }

           #eg: products/categoria/subcateogria/sub-subcategoria
            result = firebase.post("/comparizy-c73ab-default-rtdb/products/tecnologia/televisores/LED", data)
            print(result)
        except:
            continue         