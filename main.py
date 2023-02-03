import json
import service
from telegram.ext import CommandHandler, MessageHandler, filters, Application, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from os import getenv
from dotenv import load_dotenv
from model import Conversas, Mensagens, db, Chats
from peewee import fn as fn

async def callback_handler(update, context):
    objeto = json.loads(update.callback_query.data)

    if objeto['action'] == "apagar-conversa":
        conversa_id = int(objeto['value'])

        conversa = Conversas.select().where(Conversas.id == conversa_id).get_or_none()
        if conversa is not None:
            if conversa.assuntoAtual:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Você não pode apagar a conversa da qual estamos falando.")
            else:
                Conversas.delete().where(Conversas.id == conversa_id).execute()
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Conversa apagada")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Conversa não encontrada.")

    elif objeto['action'] == "continuar-conversa":
        conversa_id = int(objeto['value'])

        conversa = Conversas.select().where(Conversas.id == conversa_id).get_or_none()
        if conversa is not None:
            Conversas.update(assuntoAtual=False).where(Conversas.chat_id == update.effective_chat.id).execute()
            Conversas.update(assuntoAtual=True).where(Conversas.id == conversa_id).execute()
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Agora estamos falando sobre \"" + conversa.assunto + "\".\n\nPode me perguntar qualquer coisa.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Conversa não encontrada.")

    elif objeto['action'] == "cancelar":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ação cancelada.")

async def start(update, context):
    if Chats.select().where(Chats.chat_id == update.effective_chat.id).get_or_none() is None:
        Chats.create(chat_id=update.effective_chat.id, aguardandoAssuntoDaConversa=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Olá! Eu sou um bot do Telegram.\n\nSobre que você quer falar?")
    else:
        Chats.update(aguardandoAssuntoDaConversa=False).where(Chats.chat_id == update.effective_chat.id).execute()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Pode me perguntar qualquer coisa.")


async def mensagemRecebida(update, context):
    await verificarStatusDoChat(update, context)


async def verificarStatusDoChat(update, context):
    chat = Chats.select(Chats.aguardandoAssuntoDaConversa).where(Chats.chat_id == update.effective_chat.id).get()

    if chat.aguardandoAssuntoDaConversa:
        Chats.update(aguardandoAssuntoDaConversa=False).where(Chats.chat_id == update.effective_chat.id).execute()
        await novaConversa(update.effective_chat.id, update.effective_message.text, context.bot)


async def listarConversas(update, context):
    Chats.update(aguardandoAssuntoDaConversa=False).where(Chats.chat_id == update.effective_chat.id).execute()
    lista_conversas = ""

    for conversa in Conversas.select().where(Conversas.chat_id == update.effective_chat.id):
        lista_conversas += conversa.assunto

        if conversa.assuntoAtual:
            lista_conversas += " (Atual)"

        lista_conversas += "\n"

    if len(lista_conversas) == 0:
        lista_conversas = "Você não iniciou nenhuma conversa ainda."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=lista_conversas)


async def pedirAssuntoDaConversa(update, context):
    Chats.update(aguardandoAssuntoDaConversa=True).where(Chats.chat_id == update.effective_chat.id).execute()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Qual é o assunto da conversa?")


async def novaConversa(chat_id, assunto, bot):
    # Coloca todos os outros assuntos como não sendo o atual
    Conversas.update(assuntoAtual=False).where(Conversas.chat_id == chat_id).execute()
    Conversas.create(chat_id=chat_id, assunto=assunto, assuntoAtual=True)
    await bot.send_message(chat_id=chat_id, text="Agora estamos falando sobre \"" + assunto + "\".\n\nPode me perguntar qualquer coisa.")

async def apagarConversa(update, context):
    Chats.update(aguardandoAssuntoDaConversa=False).where(Chats.chat_id == update.effective_chat.id).execute()
    conversas = Conversas.select().where(Conversas.chat_id == update.effective_chat.id)

    if conversas.count() == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Você não iniciou nenhuma conversa ainda.")
        return

    keyboard = [[InlineKeyboardButton(conversa.assunto, callback_data='{"action": "apagar-conversa", "value": "'+str(conversa.id)+'"}')] for conversa in conversas if not conversa.assuntoAtual]
    keyboard.append([InlineKeyboardButton("Cancelar", callback_data='{"action": "cancelar", "value": "None"}')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Escolha uma conversa:", reply_markup=reply_markup)

async def continuarConversa(update, context):
    Chats.update(aguardandoAssuntoDaConversa=False).where(Chats.chat_id == update.effective_chat.id).execute()
    conversas = Conversas.select().where(Conversas.chat_id == update.effective_chat.id)

    if conversas.count() == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Você não iniciou nenhuma conversa ainda.")
        return

    keyboard = [[InlineKeyboardButton(conversa.assunto, callback_data='{"action": "continuar-conversa", "value": "' + str(conversa.id) + '"}')] for conversa in conversas if not conversa.assuntoAtual]
    keyboard.append([InlineKeyboardButton("Cancelar", callback_data='{"action": "cancelar", "value": "None"}')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Escolha uma conversa:", reply_markup=reply_markup)

load_dotenv()
application = Application.builder().token(getenv("TELEGRAM_BOT_KEY")).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("novaconversa", pedirAssuntoDaConversa))
application.add_handler(CommandHandler("listarconversas", listarConversas))
application.add_handler(CommandHandler("apagarconversa", apagarConversa))
application.add_handler(CommandHandler("continuarconversa", continuarConversa))
application.add_handler(MessageHandler(filters.TEXT, mensagemRecebida))
application.add_handler(CallbackQueryHandler(callback_handler))

application.run_polling()