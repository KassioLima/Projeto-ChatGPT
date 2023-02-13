from telegram.ext import CommandHandler, MessageHandler, filters, Application, CallbackQueryHandler
from os import getenv
from dotenv import load_dotenv
from services import telegram_service as telegramService

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

application.run_polling()