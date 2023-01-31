import service
from telegram.ext import CommandHandler, MessageHandler, filters, Application
from os import getenv
from dotenv import load_dotenv
from  model import lista_conversas, conversa_atual,db
from peewee import fn as fn


async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Olá! Eu sou um bot do Telegram.\n\nPode me perguntar qualquer coisa.")


async def echo(update, context):

    await service.ResponderAComContexto(update.effective_chat.id, context.bot, [update.effective_message.text])
    #await service.ResponderA(update.effective_message.text, update.effective_chat.id, context.bot)


async def listarConversas(update, context):
    lista_conversas = db.get()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=lista_conversas)


async def novaConversa(update, context):
    id_assunto_atual = lista_conversas.select(fn.Max(lista_conversas.assunto)).where(chat_id=update.effective_chat.id).get()
    
    id_assunto_novo = id_assunto_atual + 1
    
    lista_conversas.create(chat_id= update.effective_chat.id, assunto= id_assunto_novo)

    (conversa_atual
         .insert(chat_id=update.effective_chat.id, assunto= id_assunto_novo, flag=True)
         .on_conflict(
             conflict_target=[conversa_atual.chat_id],  # Which constraint?
             preserve=[conversa_atual.chat_id],  # Use the value we would have inserted.
             update={conversa_atual.assunto: id_assunto_novo, conversa_atual.flag: True})
         .execute())

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