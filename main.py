import service
from telegram.ext import CommandHandler, MessageHandler, filters, Application
from os import getenv
from dotenv import load_dotenv
from  model import lista_conversas, conversa_atual,db
from peewee import fn as fn


async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Olá! Eu sou um bot do Telegram.\n\nPode me perguntar qualquer coisa.")


async def echo(update, context):
    assuntoAtual = (conversa_atual
                        .select()
                        .where(conversa_atual.chat_id == update.effective_chat.id)
                        .get())
    if assuntoAtual is not None:

        idAssunto = int(assuntoAtual.assunto)
        conversasAssunto = (lista_conversas
                            .select()
                            .where(lista_conversas.chat_id == update.effective_chat.id
                                   , lista_conversas.assunto == idAssunto)
                            .dicts())
                            # .get())
        for assuntos in conversasAssunto:
            conversaContext = conversaContext + " " + assuntos['conversa'] if assuntos['conversa'] is not None else ""
        print(conversaContext)
        await service.ResponderAComContexto(update.effective_chat.id, context.bot, [update.effective_message.text]) 
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Você não criou ou selecionou nenhuma conversa")

    #await service.ResponderA(update.effective_message.text, update.effective_chat.id, context.bot)


async def listarConversas(update, context):
    lista_conversas = db.get()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=lista_conversas)


async def novaConversa(update, context):
    id_assunto_atual = lista_conversas.select(fn.Max(lista_conversas.assunto)).where(lista_conversas.chat_id == update.effective_chat.id).get()
    print(id_assunto_atual)
    if id_assunto_atual.assunto is not None:
        id_assunto_novo = int(id_assunto_atual.assunto) + 1
    else:
        id_assunto_novo = 1
    lista_conversas.create(chat_id= update.effective_chat.id, assunto= id_assunto_novo)

    (conversa_atual
         .insert(chat_id=update.effective_chat.id, assunto= id_assunto_novo)
         .on_conflict(
             conflict_target=[conversa_atual.chat_id],  # Which constraint?
             preserve=[conversa_atual.chat_id],  # Use the value we would have inserted.
             update={conversa_atual.assunto: id_assunto_novo})
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