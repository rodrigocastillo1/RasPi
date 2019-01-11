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
import threading
import datetime
import 

"""from subprocess import call #la necesitamos para la interrupcion de teclado
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD) #Queremos usar la numeracion de la placa
 
#Definimos los dos pines del sensor que hemos conectado:
Sens = 10
Buzz = 12

GPIO.setup(Sens, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Buzz, GPIO.OUT)"""

 
# Aqui definiremos aparte del Token, por ejemplo los ids de los grupos y pondríamos grupo= -XXXXX 
 
TOKEN = '733479422:AAEy9CdhfM79fousTwJG_Sbv-aRAetk7utI' # Nuestro token del bot.
AYUDA = 'Puedes utilizar los siguientes comandos : \n\n/ayuda - Guia para utilizar el bot. \n/info - Informacion De interes \n/hola - Saludo del Bot \n/piensa3D - Informacion sobre Piensa3D \n\n'
LENGUAJES = 'Los siguientes lenguajes están disponibles : \n\nEspañol \nInglés \nFrancés \nAlemán \nJaponés \nItaliano \n\n Ingresa: /language seguido del idioma \n\n'
SECURITY = 'Sistema de seguridad, escriba: \n\n/security enable - para habilitar \n\n/security disable - para deshabilitar \n\n/security itsok - para apagar la alarma'
languages_dict = {"Español": 'es', "Inglés": 'en', "Francés": 'fr', "Japonés": 'ja', "Italiano": 'it', "Alemán": 'de'}

bot = telegram.Bot(token=TOKEN) # Creamos el objeto de nuestro bot.
update = Updater(token=TOKEN)
dispatcher = update.dispatcher
trans = Translator()
language = 'es'
stop_flag = ''
itsok_flag = ''

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

def security(chat_id):
	global stop_flag, itsok_flag
	currentdate = datetime.datetime.now().strftime("%Y-%m-%d_%H%M_%S")
	file_path = os.path.join('security','{}.png'.format(currentdate))
	os.system("fswebcam" + file_path)
	photo = open(file_path, 'rb')
	numeros = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
	
	while not stop_flag:
		#if GPIO.input(Sens) == GPIO.HIGH:
		num = random.choice(numeros)
		print(num)
		if(num == 5):
			bot.send_message(chat_id, text="¡Alerta!")
			currentdate = datetime.datetime.now().strftime("%Y-%m-%d_%H%M_%S")
			file_path = os.path.join('security','{}.png'.format(currentdate))
			os.system("fswebcam" + file_path)
			photo = open(file_path, 'rb')
			try:
		        bot.send_photo(chat_id, photo=photo)
		    except Exception as ex:
		        print(ex)
			while not itsok_flag:
				for i in range(10):
					#GPIO.output(Buzz, True)
					time.sleep(0.5)
					#GPIO.output(Buzz, False)
			itsok_flag = ''
	stop_flag = ''

def securityTel(bot, update, args):
	chat_id = update.message.chat_id
	global stop_flag, itsok_flag
	if not args:
		bot.send_message(chat_id, text=SECURITY)
	elif ''.join(args) == "enable":		#COMANDO enable: Activa el sistema
		bot.send_message(chat_id, text="Iniciando servicio de seguridad...")
		time.sleep(1)
		bot.send_message(chat_id, text="¡Armado!")
		#security(chat_id)
		t = threading.Thread(target=security, args=[chat_id])
		t.start()

	elif ''.join(args) == "disable":	#COMANDO ITSOK: Desactiva el sistema
		stop_flag = "stop"
		bot.send_message(chat_id, text="Sistema desactivado. Está indefenso ante intrusos.")

	elif ''.join(args) == "itsok":		#COMANDO ITSOK: Apaga la alarma
		itsok_flag = "itsok"
		bot.send_message(chat_id, text="Apagando alarma. Sistema armado.")

	else:
		bot.send_message(chat_id, text="Comando inválido")


hello_handler = CommandHandler('hello', helloTel)
help_handler = CommandHandler('help', helpTel)
quote_handler = CommandHandler('quote', quoteTel)
translate_handler = CommandHandler('translate', translateTel, pass_args=True)
gray_handler = MessageHandler(Filters.photo, grayTel)
language_handler = CommandHandler('language', languageTel, pass_args=True)
security_handler = CommandHandler('security', securityTel, pass_args=True)

dispatcher.add_handler(hello_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(quote_handler)
dispatcher.add_handler(translate_handler)
dispatcher.add_handler(gray_handler)
dispatcher.add_handler(language_handler)
dispatcher.add_handler(security_handler)

update.start_polling()
update.idle()

GPIO.cleanup()