
from utils import *
from constants import *
from firebase import firebase
from bs4 import BeautifulSoup
import re
import requests
from selenium import webdriver
import time
import re
from datetime import date

firebase = firebase.FirebaseApplication("https://comparizy-test-default-rtdb.firebaseio.com/", None) #test

def find_products_tecnologia_computadoras():
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
        scrolldown("0",driver)
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
            continue

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