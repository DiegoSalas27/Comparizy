
from utils import *
from constants import *
from firebase import firebase
from bs4 import BeautifulSoup
import re
import requests
from selenium import webdriver
import time

firebase = firebase.FirebaseApplication("https://comparizy-c73ab-default-rtdb.firebaseio.com/", None)

def find_products_tecnologia_computadoras():
   #Clean database
   #eg: products/categoria-padre/categoria/
   firebase.delete("/comparizy-c73ab-default-rtdb/products/%s/%s/"%(TECNOLOGIA_GROUP_CATEGORY, COMPUTADORAS_CATEGORY), None)

   #Find saga's products
   #Laptops
   print('Saga products!!!')
   print()
   html_text = requests.get('https://www.falabella.com.pe/falabella-pe/category/cat40712/Laptops',timeout=(3.05, 27)).text
   soup = BeautifulSoup(html_text, 'lxml')
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
               'store': SAGA_STORE,
               'category': TECNOLOGIA_GROUP_CATEGORY,
               'sub_category': COMPUTADORAS_CATEGORY,
               'sub_sub_category': LAPTOPS_SUBCATEGORY,
               'brand': product_brand
           }

           #eg: products/categoria/subcateogria/sub-subcategoria
           result = firebase.post("/comparizy-c73ab-default-rtdb/products/tecnologia/computadoras/laptops", data)
           print(result)
       except:
           continue

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
#    #Find replay's products
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
    driver = webdriver.Chrome()
    driver.get("about:blank")
    driver.maximize_window()
    try:
        driver.get('https://www.falabella.com.pe/falabella-pe/category/cat6370551/Televisores-LED')
        scrolldown("0",driver)
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
            continue
