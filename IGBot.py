from instabot import Bot
from shutil import rmtree
import os
import time
import datetime
import json
import re

username = "dancingpels"
password = "Ktagarop71"
bot = Bot()

comments_file = "comentarios.json"
dms_file = "dms_leidos.json"
correos_file = "correos_recibidos.json"

def cargar_datos_guardados(file_name):
    try:
        with open(file_name, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    except FileNotFoundError:
        return {}

def guardar_datos(data, file_name):
    with open(file_name, "w") as file:
        json.dump(data, file)

def guardar_comentario(usuario, fecha_comentario):
    comentarios_guardados = cargar_datos_guardados(comments_file)
    if usuario not in comentarios_guardados:
        comentarios_guardados[usuario] = []
    if fecha_comentario not in comentarios_guardados[usuario]:
        comentarios_guardados[usuario].append(fecha_comentario)
        guardar_datos(comentarios_guardados, comments_file)

def guardar_correo(usuario, correo):
    correos_recibidos = cargar_datos_guardados(correos_file)
    if usuario not in correos_recibidos:
        correos_recibidos[usuario] = []
    if correo not in correos_recibidos[usuario]:
        correos_recibidos[usuario].append(correo)
        guardar_datos(correos_recibidos, correos_file)

def procesar_dms():
    dms_leidos = cargar_datos_guardados(dms_file)
    dms = bot.get_messages()
    for thread in dms['inbox']['threads']:
        for item in thread['items']:
            #print(item)  # Agrega esta línea para depurar
            if item['item_id'] in dms_leidos:
                continue  # Saltar mensajes ya leídos

            remitente_id = item['user_id']
            remitente_username = bot.get_username_from_user_id(remitente_id)
            # Asegúrate de que 'text' está en item antes de acceder a él
            if 'text' in item:
                mensaje = item['text']
                
                # Comprobar si el mensaje contiene un correo electrónico
                resultado_busqueda = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', mensaje)
                if resultado_busqueda:
                    correo_encontrado = resultado_busqueda.group()
                    print(f"CORREO RECIBIDO DE {remitente_username}: {correo_encontrado}")
                    guardar_correo(remitente_username, correo_encontrado)
                    bot.send_message("Great, thanks for sharing your email! We'll be sending the Web Design Guide to you shortly. Stay tuned, and don't hesitate to reach out with any questions or for further assistance!", [remitente_id])
                else:
                    print(f"mensaje nuevo de {remitente_username}: {mensaje}")
            dms_leidos[item['item_id']] = True

    guardar_datos(dms_leidos, dms_file)

try:
    bot.login(username=username, password=password)
    total_medias = bot.get_total_user_medias("dancingpels")

    while True:
        print("######################### Ciclo Nuevo #########################", datetime.datetime.now())
        comentarios_guardados = cargar_datos_guardados(comments_file)

        for media_index in range(len(total_medias)):
            comments = bot.get_media_comments_all(total_medias[media_index])

            for comment in comments:
                usuario = comment['user']['username']
                fecha_comentario = comment['created_at_utc']

                if "WEBSITE".lower() in comment['text'].lower() and (usuario not in comentarios_guardados or fecha_comentario not in comentarios_guardados[usuario]):
                    bot.send_message("Thank you for your interest. Please share the email address where we should send your Web Design Guide.", usuario)
                    guardar_comentario(usuario, fecha_comentario)

        # Procesar DMs
        procesar_dms()

        time.sleep(300)  # Espera de 60 segundos

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    bot.logout()
    if os.path.exists("config"):
        rmtree("config")
