import telegram 
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
import time # Librería para hacer que el programa que controla el bot no se acabe.
from googletrans import Translator
import random
import os
from PIL import Image

from subprocess import call #la necesitamos para la interrupcion de teclado
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD) #Queremos usar la numeracion de la placa
 
#Definimos los dos pines del sensor que hemos conectado: Trigger y Echo
Trig = 11
Echo = 13
 
#Hay que configurar ambos pines del HC-SR04
GPIO.setup(Trig, GPIO.OUT)
GPIO.setup(Echo, GPIO.IN)

 
# Aqui definiremos aparte del Token, por ejemplo los ids de los grupos y pondríamos grupo= -XXXXX 
 
TOKEN = '733479422:AAEy9CdhfM79fousTwJG_Sbv-aRAetk7utI' # Nuestro token del bot.
AYUDA = 'Puedes utilizar los siguientes comandos : \n\n/ayuda - Guia para utilizar el bot. \n/info - Informacion De interes \n/hola - Saludo del Bot \n/piensa3D - Informacion sobre Piensa3D \n\n'
LENGUAJES = 'Los siguientes lenguajes están disponibles : \n\nEspañol \nInglés \nFrancés \nAlemán \nJaponés \nItaliano \n\n Ingresa: /language seguido del idioma \n\n'
languages_dict = {"Español": 'es', "Inglés": 'en', "Francés": 'fr', "Japonés": 'ja', "Italiano": 'it', "Alemán": 'de'}

bot = telegram.Bot(token=TOKEN) # Creamos el objeto de nuestro bot.
update = Updater(token=TOKEN)
dispatcher = update.dispatcher
trans = Translator()
language = 'es'


def helloTel(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="¡Hola! Estoy a tu servicio")

def helpTel(bot, update): # Definimos una función que resuleva lo que necesitemos.
    bot.send_chat_action(chat_id=update.message.chat_id, action='typing') # Enviando ...
    time.sleep(1) #La respuesta del bot tarda 1 segundo en ejecutarse
    bot.send_message(chat_id=update.message.chat_id, text=AYUDA) # Con la función 'send_message()' del bot, enviamos al ID almacenado el texto que queremos.

def quoteTel(bot, update): # Definimos la función que enviará una cita random.
    file = open("quotes.txt", "r", encoding="utf8")
    quotes_list = file.read().split("\n\n")
    quote = random.choice(quotes_list)
    chat_id = update.message.chat_id # Guardamos el ID de la conversación para poder responder.
    trans_text = trans.translate(quote, dest=language)
    bot.send_chat_action(chat_id, 'typing') # Enviando ...
    time.sleep(1) #La respuesta del bot tarda 1 segundo en ejecutarse
    bot.send_message(chat_id, text=trans_text.text) # Con la función 'send_message()' del bot, enviamos al ID almacenado el texto que queremos.

def translateTel(bot, update, args): # Definimos la función que enviará una cita random.
    chat_id = update.message.chat_id # Guardamos el ID de la conversación para poder responder.
    texto = ' '.join(args)
    trans_text = trans.translate(texto, dest=language)
    print(trans_text)
    bot.send_chat_action(chat_id, 'typing') # Enviando ...
    time.sleep(1) #La respuesta del bot tarda 1 segundo en ejecutarse
    bot.send_message(chat_id, text=trans_text.text) # Con la función 'send_message()' del bot, enviamos al ID almacenado el texto que queremos.

def languageTel(bot, update, args):
    chat_id = update.message.chat_id
    global language
    print(''.join(args))
    if not args:
        bot.send_message(chat_id, text=LENGUAJES) # Con la función 'send_message()' del bot, enviamos al ID almacenado el texto que queremos.
    else:
        language = languages_dict.get(''.join(args))
        mensaje = "Lenguaje cambiado a "+''.join(args)
        bot.send_message(chat_id, text=mensaje)

def grayTel(bot, update):
    chat_id = update.message.chat_id
    photo_file = bot.get_file(update.message.photo[-1].file_id)
    file_name = os.path.join('images','{}.png'.format(photo_file.file_id))
    #print(file_name)
    photo_file.download(file_name)
    img = Image.open(file_name).convert('LA')
    os.remove(file_name)
    img.save(file_name)
    bot.send_chat_action(chat_id, 'upload_photo') # Enviando ...
    time.sleep(1) #La respuesta del bot tarda 1 segundo en ejecutarse
    photo = open(file_name, 'rb')
    try:
        bot.send_photo(chat_id, photo=photo)
    except Exception as ex:
        print(ex)
    bot.send_message(chat_id, text="Cambié tu foto a escala de grises")


hello_handler = CommandHandler('hello', helloTel)
help_handler = CommandHandler('help', helpTel)
quote_handler = CommandHandler('quote', quoteTel)
translate_handler = CommandHandler('translate', translateTel, pass_args=True)
gray_handler = MessageHandler(Filters.photo, grayTel)
language_handler = CommandHandler('language', languageTel, pass_args=True)
dispatcher.add_handler(hello_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(quote_handler)
dispatcher.add_handler(translate_handler)
dispatcher.add_handler(gray_handler)
dispatcher.add_handler(language_handler)

update.start_polling()

def detectarObstaculo():
 
   GPIO.output(Trig, False) #apagamos el pin Trig
   time.sleep(2*10**-6) #esperamos dos microsegundos
   GPIO.output(Trig, True) #encendemos el pin Trig
   time.sleep(10*10**-6) #esperamos diez microsegundos
   GPIO.output(Trig, False) #y lo volvemos a apagar

   while GPIO.input(Echo) == 0:
      start = time.time()
   while GPIO.input(Echo) == 1:
      end = time.time()

   duracion = end-start
   duracion = duracion*10**6
   medida = duracion/58 #dividimos entre 58 para que muestre la distancia en cm
   return medida
   #print("%.2f" %medida) #mostramos resultado

while True:
   try:
      print("%.2f", detectarObstaculo())
   except Exception as ex:
        print(ex)
        print("Ha ocurrido un error inesperado. Vuelva a lanzar el bot")
        print("Reiniciando GPIO")
        time.sleep(1)
		GPIO.cleanup()
		print("Proceso terminado")