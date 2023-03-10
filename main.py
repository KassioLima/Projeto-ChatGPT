from telegram.ext import CommandHandler, MessageHandler, filters, Application, CallbackQueryHandler
from os import getenv
from dotenv import load_dotenv
from services import telegram_service as telegramService
from threading import Thread
import time

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


class Th(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):

        from flask import Flask

        app = Flask(__name__)

        @app.route('/')
        def hello_world():  # put application's code here
            return 'Hello World!'

        if __name__ == '__main__':
            app.run(host='0.0.0.0', port=8081)

        while True:
            print("Rodando " + str(time.time()))
            time.sleep(5)


Th().start()


application.run_polling()
