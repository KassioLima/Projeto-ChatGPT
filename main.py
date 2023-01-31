import service
from telegram.ext import CommandHandler, MessageHandler, filters, Application
from os import getenv
from dotenv import load_dotenv

async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Olá! Eu sou um bot do Telegram.\n\nPode me perguntar qualquer coisa.")


async def echo(update, context):
    await service.ResponderAComContexto(update.effective_chat.id, context.bot, [update.effective_message.text])


async def listarConversas(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="lista de assuntos")


async def novaConversa(update, context):
    return

async def apagarConversa(update, context):
    return

async def continuarConversa(update, context):
    return

load_dotenv()
application = Application.builder().token(getenv("TELEGRAM_BOT_KEY")).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("novaconversa", novaConversa))
application.add_handler(CommandHandler("listarconversas", listarConversas))
application.add_handler(CommandHandler("apagarconversa", apagarConversa))
application.add_handler(CommandHandler("continuarconversa", continuarConversa))
application.add_handler(MessageHandler(filters.TEXT, echo))

application.run_polling()

class Conversa:

    mensagem: str

    def __init__(self, chat_id, conversa):
        self.chat_id = chat_id
        self.conversa = conversa