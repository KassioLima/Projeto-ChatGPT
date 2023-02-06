import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from model import Chats, Conversas, Mensagens
from repositories import repository
import services.open_ai_service as open_ai

async def start(update, context):
    chat = await repository.ObterChatPorChatId(update.effective_chat.id)

    if chat is None:
        await repository.CadastrarChat(Chats(chat_id = update.effective_chat.id, aguardandoAssuntoDaConversa = True))
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Olá! Eu sou um bot do Telegram.\n\nSobre que você quer falar?")
    else:
        chat.aguardandoAssuntoDaConversa = False
        await repository.AtualizarChat(chat)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Pode me perguntar qualquer coisa.")

async def mensagemRecebida(update, context):
    chat = await repository.ObterChatPorChatId(update.effective_chat.id)

    if chat.EstaAguardandoAlgo():
        await _verificaOQueEstaSendoAguardado(update, context, chat)
    else:
        await _trocarMensagem(update, context)

async def _trocarMensagem(update, context):
    conversa = await repository.ObterConversaAtualPorChatId(update.effective_chat.id)

    if conversa is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Você não iniciou nenhuma conversa ainda.")
        return

    await repository.CadastrarMensagem(Mensagens(mensagem = update.effective_message.text, remetente = update.effective_chat.first_name, conversa = conversa.id))

    mensagemComContexto = await _obterContextoDaConversa(conversa)

    resposta = await open_ai.EnviarMensagem(mensagemComContexto)
    await repository.CadastrarMensagem(Mensagens(mensagem=resposta, remetente="Chat GPT", conversa=conversa.id))

    await context.bot.send_message(chat_id=update.effective_chat.id, text=resposta)

async def _obterContextoDaConversa(conversa: Conversas):
    mensagens = await repository.ObterMensagensPorConversaId(conversa.id)

    mesagensConcatenadas = ""
    for mensagen in mensagens:
        mesagensConcatenadas += mensagen.mensagem + "\n\n"

    mesagensConcatenadas = open_ai.cortarMensagemParaCaberNosTokens(mesagensConcatenadas)
    mesagensConcatenadas = "Assunto: " + conversa.assunto + "\n\n" + mesagensConcatenadas

    return mesagensConcatenadas

async def _verificaOQueEstaSendoAguardado(update, context, chat: Chats):
    if chat.aguardandoAssuntoDaConversa:
        chat.aguardandoAssuntoDaConversa = False
        await repository.AtualizarChat(chat)
        await _cadastrarNovaConversa(update.effective_chat.id, update.effective_message.text, context.bot)

async def listarConversas(update, context):
    chat = await repository.ObterChatPorChatId(update.effective_chat.id)
    chat.aguardandoAssuntoDaConversa = False
    await repository.AtualizarChat(chat)

    lista_conversas = ""

    for conversa in await repository.ObterConversasPorChatId(update.effective_chat.id):
        lista_conversas += conversa.assunto + (" (Atual)" if conversa.assuntoAtual else "") + "\n"

    if len(lista_conversas) == 0:
        lista_conversas = "Você não iniciou nenhuma conversa ainda."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=lista_conversas)

async def novaConversa(update, context):
    chat = await repository.ObterChatPorChatId(update.effective_chat.id)
    chat.aguardandoAssuntoDaConversa = True
    await repository.AtualizarChat(chat)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Qual é o assunto da conversa?")

async def apagarConversa(update, context):
    chat = await repository.ObterChatPorChatId(update.effective_chat.id)
    chat.aguardandoAssuntoDaConversa = False
    await repository.AtualizarChat(chat)

    conversas = await repository.ObterConversasPorChatId(update.effective_chat.id)

    if not conversas.count() > 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Você não iniciou nenhuma conversa ainda.")
        return

    keyboard = [[InlineKeyboardButton(conversa.assunto + (" (Atual)" if conversa.assuntoAtual else ""), callback_data='{"action": "apagar-conversa", "value": "'+str(conversa.id)+'"}')] for conversa in conversas]
    keyboard.append([InlineKeyboardButton("Cancelar", callback_data='{"action": "cancelar", "value": "None"}')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Escolha uma conversa:", reply_markup=reply_markup)

async def continuarConversa(update, context):
    chat = await repository.ObterChatPorChatId(update.effective_chat.id)
    chat.aguardandoAssuntoDaConversa = False
    await repository.AtualizarChat(chat)

    conversas = await repository.ObterConversasPorChatId(update.effective_chat.id)

    if not conversas.count() > 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Você não iniciou nenhuma conversa ainda.")
        return

    keyboard = [[InlineKeyboardButton(conversa.assunto + (" (Atual)" if conversa.assuntoAtual else ""), callback_data='{"action": "continuar-conversa", "value": "' + str(conversa.id) + '"}')] for conversa in conversas]
    keyboard.append([InlineKeyboardButton("Cancelar", callback_data='{"action": "cancelar", "value": "None"}')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Escolha uma conversa:", reply_markup=reply_markup)

async def callback_handler(update, context):
    objeto = json.loads(update.callback_query.data)

    action = objeto['action']
    value = objeto['value']

    if action == "apagar-conversa":
        conversa_id = int(value)
        await _apagarConversa(update, context, conversa_id)

    elif action == "continuar-conversa":
        conversa_id = int(value)
        await _continuarConversa(update, context, conversa_id)

    elif action == "cancelar":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ação cancelada.")

async def _cadastrarNovaConversa(chat_id, assunto, bot):
    await repository.RemoverAssuntoAtual(chat_id)
    await repository.CadastrarConversa(Conversas(chat_id=chat_id, assunto=assunto, assuntoAtual=True))
    await bot.send_message(chat_id=chat_id, text="Agora estamos falando sobre \"" + assunto + "\".\n\nPode me perguntar qualquer coisa.")

async def _apagarConversa(update, context, conversa_id):
    conversa = await repository.ObterConversaPorId(conversa_id)

    if conversa is not None:
        if conversa.assuntoAtual:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Você não pode apagar a conversa atual.")
        else:
            Mensagens.delete().where(Mensagens.conversa_id == conversa_id).execute()
            Conversas.delete().where(Conversas.id == conversa_id).execute()
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Conversa apagada")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Conversa não encontrada.")

async def _continuarConversa(update, context, conversa_id):
    conversa = await repository.ObterConversaPorId(conversa_id)

    if conversa is not None:
        Conversas.update(assuntoAtual=False).where(Conversas.chat_id == update.effective_chat.id).execute()
        Conversas.update(assuntoAtual=True).where(Conversas.id == conversa_id).execute()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Agora estamos falando sobre \"" + conversa.assunto + "\".\n\nPode me perguntar qualquer coisa.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Conversa não encontrada.")