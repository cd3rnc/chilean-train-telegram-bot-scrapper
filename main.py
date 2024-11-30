from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import datetime
import dataframe_image as dfi
import requests
from dotenv import load_dotenv
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

def extract_data(origen, destino):
    try:
        path = "/usr/bin/chromedriver"  
        service = Service(executable_path=path)
        
        options = Options()
        options.add_argument("--headless")  
        options.add_argument("--disable-gpu") 
        options.add_argument("--no-sandbox")  
        options.add_argument("--disable-dev-shm-usage")  
        options.binary_location = '/usr/bin/chromium'
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get("https://www.efe.cl/planificador/")
        
        first_point = Select(driver.find_element(By.ID, 'ranorigenViaje'))
        first_point.select_by_visible_text(origen)
        
        second_point = Select(driver.find_element(By.ID, 'randestinoViaje'))
        second_point.select_by_visible_text(destino)
        
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        date_scrapper = tomorrow.strftime("%m-%d-%Y")  
        date = driver.find_element(By.ID, 'ranfechaIda')
        date.clear()  
        date.send_keys(date_scrapper)
        date.send_keys(Keys.ENTER)
        
        time.sleep(2)
        
        encabezados = driver.find_elements(By.TAG_NAME, 'th')
        encabezado_datos = [encabezado.text for encabezado in encabezados]
        
        filas = driver.find_elements(By.TAG_NAME, 'tr')
        tabla_datos = []

        for fila in filas:
            celdas = fila.find_elements(By.TAG_NAME, 'td') 
            fila_datos = [celda.text for celda in celdas]  
            if fila_datos:  
                tabla_datos.append(fila_datos)
        
        if encabezado_datos:
            tabla_datos.insert(0, encabezado_datos)
        
        return tabla_datos
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    finally:
        driver.quit()

def clean_table(tabla_datos):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    df = pd.DataFrame(tabla_datos, columns=['salida', 'llegada', 'duracion', 'valor'])

    df['timestamp'] = time.time()
    df = df[['timestamp', 'salida', 'llegada', 'duracion', 'valor']]
    return df

def enviar_mensaje_telegram(token, chat_id, mensaje):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": mensaje}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Mensaje enviado correctamente")
    else:
        print(f"Error al enviar mensaje. Código de estado: {response.status_code}")
        print(response.text)

def enviar_imagen_telegram(token, chat_id, ruta_imagen):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    files = {"photo": open(ruta_imagen, "rb")}
    data = {"chat_id": chat_id}
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        print("Imagen enviada correctamente")
    else:
        print(f"Error al enviar imagen. Código de estado: {response.status_code}")
        print(response.text)

def df_as_image(df):
    dfi.export(df[['salida', 'llegada', 'duracion', 'valor']], 'df_styled.png')
    return 'df_styled.png'


origen = 'Buin'
destino = 'Estación Central'


####to work############
tabla_datos = extract_data(origen, destino)
if tabla_datos:
    df = clean_table(tabla_datos)

    imagen = df_as_image(df)

    enviar_mensaje_telegram(bot_token, chat_id, f'Trenes {origen} a {destino}')
    enviar_imagen_telegram(bot_token, chat_id, imagen)
else:
    print("No se pudo extraer información de la tabla.")

######back to home :)############
tabla_datos = extract_data(destino, origen)

if tabla_datos:
    df = clean_table(tabla_datos)

    imagen = df_as_image(df)

    enviar_mensaje_telegram(bot_token, chat_id, f'Trenes {destino} a {origen}')
    enviar_imagen_telegram(bot_token, chat_id, imagen)
else:
    print("No se pudo extraer información de la tabla.")






