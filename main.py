import telebot
from telebot.types import ReplyKeyboardMarkup
from telebot.types import ForceReply
import threading
import time
import sqlite3
from os import remove
from pytube import YouTube
from googletrans import *
import requests
from gtts import gTTS

TOKEN = '5589185145:AAGltlD7OP7-bDT796Blkbys_B_BInmscsU'
NASA_KEY = 'S758LT18txQfuRSxpemAtFga0Thd7tp6dBGioNmb'

bot = telebot.TeleBot(TOKEN)
con = sqlite3.connect('usuarios.db')
cur = con.cursor()
traduce = Translator()


# Create table
cur.execute('''CREATE TABLE IF NOT EXISTS usuarios
               (id_user INTEGER PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL, recordatorio TEXT NOT NULL, hora_p DATE, chat_id INTEGER)''')


# Responde al comando listado en [""]
@bot.message_handler(commands=["Inicia", "Iniciar", "iniciar"])
def cmd_start(message):
    markup = ForceReply()
    resmsg = bot.send_message(message.chat.id, message.chat.first_name + "! Comenzare creandote un perfil, recopilare "
                                                                         "la información que me proporciona Telegram "
                                                                         "de ti.\n "
                                                                         "¿Estás de acuerdo?", reply_markup=markup)
    bot.register_next_step_handler(resmsg, recabarData)


@bot.message_handler(commands=["nasa"])
def msgNasa(message):
    apiNasa(message.chat.id)


@bot.message_handler(commands=["video"])
def cmd_start(message):
    bot.reply_to(message, "Por favor enviame el enlace de YouTube")


@bot.message_handler(content_types=["text"])
def msgText(message):
    txtRecibido = message.text
    if txtRecibido.startswith("/"):
        bot.send_message(message.chat.id, "El comando " + txtRecibido + " No esta Disponible")
    elif txtRecibido.startswith("https://www.youtube.com/") or txtRecibido.startswith("https://youtu"):
        downVideo(message.chat.id, txtRecibido, message.chat.first_name)
    else:
        bot.send_chat_action(message.chat.id, "typing")
        time.sleep(2)
        bot.send_message(message.chat.id,
                         "Hola " + message.chat.first_name + " Usa el Comando /iniciar para comenzar")


def downVideo(id_chat, enlace, nombre):
    yt = YouTube(enlace)
    bot.send_chat_action(id_chat, "upload_video")
    resMax = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    data = resMax.download()
    video = open(data, "rb")
    bot.send_video(id_chat, video, caption="Aqui tienes " + nombre)
    video.close()
    remove(data)


def recabarData(message):
    if message.text == str('Sí') or message.text == str('Si'):
        bot.send_message(message.chat.id, "Excelente dame unos segundos")
        bot.send_chat_action(message.chat.id, "typing")
        time.sleep(2)
        bot.send_message(message.chat.id, "Esta todo listo.\n¿En que puedo Ayudarte " + message.chat.first_name + "?")
    elif message.text == str('No') or message.text == str('No '):
        bot.send_chat_action(message.chat.id, "typing")
        time.sleep(0.5)
        bot.send_message(message.chat.id, "Me temo que no podremos entendernos </3")
    else:
        markup = ReplyKeyboardMarkup(
            one_time_keyboard=True,
            input_field_placeholder="¿Sí o No?",
            resize_keyboard=True)
        markup.add("Sí", "No")
        msg = bot.send_message(message.chat.id, '¿Estás de acuerdo?', reply_markup=markup)
        bot.register_next_step_handler(msg, recabarData)


def apiNasa(id_chat):
    resp = requests.get('https://api.nasa.gov/planetary/apod?api_key='+NASA_KEY).json()
    titulo = resp['title']
    fech = resp['date']
    imgHD = resp['hdurl']
    imgHQ = resp['url']
    xplica = traduce.translate(resp['explanation'],'es',src='en').text
    formato = f'<strong>{titulo}</strong>\n' \
             f'<em>{xplica}</em>'
    tts = gTTS(xplica, lang='es-us')
    tts.save(titulo+".mp3")
    audio = open(titulo+".mp3", "rb")
    bot.send_audio(id_chat, audio)
    bot.send_message(id_chat, formato, parse_mode='html')
    bot.send_photo(id_chat,imgHD)

def escuchaMSG():
    bot.infinity_polling()


if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand("/iniciar", "Comienza la experiencia"),
        telebot.types.BotCommand("/tareas", "Lista de Tareas"),
        telebot.types.BotCommand("/video", "Descarga video con Enlace"),
        telebot.types.BotCommand("/nasa", "Datos de la NASA"),
    ])
    print('Iniciando SAREH')
    bot_hilo = threading.Thread(name="hilo_bot", target=escuchaMSG)
    bot_hilo.start()
    print('SAREH en linea')
