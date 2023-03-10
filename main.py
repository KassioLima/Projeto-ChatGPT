from telegram.ext import CommandHandler, MessageHandler, filters, Application, CallbackQueryHandler
from os import getenv
from dotenv import load_dotenv
from services import telegram_service as telegramService
from threading import Thread
from flask import Flask

load_dotenv()
application = Application.builder().token(getenv("TELEGRAM_BOT_KEY")).build()

application.add_handler(CommandHandler("start", telegramService.start))
application.add_handler(CommandHandler("novaconversa", telegramService.novaConversa))
application.add_handler(CommandHandler("minhasconversas", telegramService.listarConversas))
application.add_handler(CommandHandler("apagarconversa", telegramService.apagarConversa))
application.add_handler(CommandHandler("mudarconversa", telegramService.continuarConversa))
application.add_handler(CommandHandler("gerarimagem", telegramService.gerarimagem))
application.add_handler(MessageHandler(filters.TEXT, telegramService.mensagemRecebida))
application.add_handler(CallbackQueryHandler(telegramService.callback_handler))

class FlaskThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        Flask(__name__).run(host='0.0.0.0', port=8081)

FlaskThread().start()
application.run_polling()
