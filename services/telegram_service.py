import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from infra.model import Chats, Conversas, Mensagens
from repositories.repository import Repository as repository
import services.open_ai_service as open_ai

async def start(update, context):
    chat = await repository.ObterChatPorChatId(update.effective_chat.id)

    if chat is None:
        await repository.CadastrarChat(Chats(chat_id = update.effective_chat.id, aguardandoAssuntoDaConversa = True))
        await _responderNoTelegram(context.bot, update.effective_chat.id, "Olá! Eu sou um bot do Telegram.\n\nSobre que você quer falar?")
    else:
        conversa = await repository.ObterConversaAtualPorChatId(chat.chat_id)

        if conversa is not None:
            chat.aguardandoAssuntoDaConversa = False
            chat.aguardandoDescricaoImagem = False
            await repository.AtualizarChat(chat)
            await _responderNoTelegram(context.bot, update.effective_chat.id, "Estávamos falando sobre \"" + conversa.assunto + "\".\n\nPode me perguntar qualquer coisa.")
        else:
            chat.aguardandoAssuntoDaConversa = True
            await repository.AtualizarChat(chat)
            await _responderNoTelegram(context.bot, update.effective_chat.id, "Sobre que você quer falar?")

async def mensagemRecebida(update, context):
    chat = await repository.ObterChatPorChatId(update.effective_chat.id)

    if chat is None:
        if not _ehGrupo(update):
            await start(update, context)
        elif _falouComOBot(update):
            await start(update, context)

    elif _ehPrivado(update) or (_ehGrupo(update) and _falouComOBot(update)):
        if chat.aguardandoAssuntoDaConversa or chat.aguardandoDescricaoImagem:
            await _verificaOQueEstaSendoAguardado(update, context, chat)
        else:
            await _trocarMensagem(update, context)

async def _trocarMensagem(update, context):
    conversa = await repository.ObterConversaAtualPorChatId(update.effective_chat.id)

    if conversa is None:
        await _responderNoTelegram(context.bot, update.effective_chat.id, "Você não iniciou nenhuma conversa ainda.")
        return

    message = str(update.effective_message.text)
    if message.startswith("@ChatGPT_Oficial_Bot "):
        message = message[len("@ChatGPT_Oficial_Bot "):]

    await repository.CadastrarMensagem(Mensagens(mensagem = message, remetente = update.effective_user.first_name, conversa_id=conversa.id))

    mensagemComContexto = await _obterContextoDaConversa(conversa)

    resposta = await open_ai.EnviarMensagem(mensagemComContexto)
    await repository.CadastrarMensagem(Mensagens(mensagem=resposta, remetente="Chat GPT", conversa_id=conversa.id))

    while len(resposta) > 0:
        await _responderNoTelegram(context.bot, update.effective_chat.id, resposta[:4096])
        resposta = resposta[4096:]

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

        message = str(update.effective_message.text)
        if message.startswith("@ChatGPT_Oficial_Bot "):
            message = message[len("@ChatGPT_Oficial_Bot "):]

        await _cadastrarNovaConversa(update.effective_chat.id, message, context.bot)

    elif chat.aguardandoDescricaoImagem:
        chat.aguardandoDescricaoImagem = False
        await repository.AtualizarChat(chat)

        message = str(update.effective_message.text)
        if message.startswith("@ChatGPT_Oficial_Bot "):
            message = message[len("@ChatGPT_Oficial_Bot "):]

        await _gerarimagem(update.effective_chat.id, message, context.bot)

async def listarConversas(update, context):
    chat = await repository.ObterChatPorChatId(update.effective_chat.id)

    if chat is None:
        return

    chat.aguardandoAssuntoDaConversa = False
    chat.aguardandoDescricaoImagem = False
    await repository.AtualizarChat(chat)

    lista_conversas = ""

    for conversa in await repository.ObterConversasPorChatId(update.effective_chat.id):
        lista_conversas += conversa.assunto + (" (Atual)" if conversa.assuntoAtual else "") + "\n"

    if len(lista_conversas) == 0:
        lista_conversas = "Você não iniciou nenhuma conversa ainda."

    await _responderNoTelegram(context.bot, update.effective_chat.id, lista_conversas)

async def novaConversa(update, context):
    chat = await repository.ObterChatPorChatId(update.effective_chat.id)

    if chat is None:
        return

    chat.aguardandoAssuntoDaConversa = True
    await repository.AtualizarChat(chat)
    await _responderNoTelegram(context.bot, update.effective_chat.id, "Qual é o assunto da conversa?")

async def apagarConversa(update, context):
    chat = await repository.ObterChatPorChatId(update.effective_chat.id)

    if chat is None:
        return

    chat.aguardandoAssuntoDaConversa = False
    chat.aguardandoDescricaoImagem = False
    await repository.AtualizarChat(chat)

    conversas = await repository.ObterConversasPorChatId(update.effective_chat.id)

    if not conversas.count() > 0:
        await _responderNoTelegram(context.bot, update.effective_chat.id, "Você não iniciou nenhuma conversa ainda.")
        return

    keyboard = [[InlineKeyboardButton(conversa.assunto + (" (Atual)" if conversa.assuntoAtual else ""), callback_data='{"action": "apagar-conversa", "value": "' + str(conversa.id) + '"}')] for conversa in conversas]
    keyboard.append([InlineKeyboardButton("Cancelar", callback_data='{"action": "cancelar", "value": "None"}')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Escolha uma conversa:", reply_markup=reply_markup)

async def continuarConversa(update, context):
    chat = await repository.ObterChatPorChatId(update.effective_chat.id)

    if chat is None:
        return

    chat.aguardandoAssuntoDaConversa = False
    chat.aguardandoDescricaoImagem = False
    await repository.AtualizarChat(chat)

    conversas = await repository.ObterConversasPorChatId(update.effective_chat.id)

    if not conversas.count() > 0:
        await _responderNoTelegram(context.bot, update.effective_chat.id, "Você não iniciou nenhuma conversa ainda.")
        return

    keyboard = [[InlineKeyboardButton(conversa.assunto + (" (Atual)" if conversa.assuntoAtual else ""), callback_data='{"action": "continuar-conversa", "value": "' + str(conversa.id) + '"}')] for conversa in conversas]
    keyboard.append([InlineKeyboardButton("Cancelar", callback_data='{"action": "cancelar", "value": "None"}')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Escolha uma conversa:", reply_markup=reply_markup)

async def gerarimagem(update, context):
    chat = await repository.ObterChatPorChatId(update.effective_chat.id)

    if chat is None:
        return

    chat.aguardandoAssuntoDaConversa = False
    chat.aguardandoDescricaoImagem = True
    await repository.AtualizarChat(chat)
    await _responderNoTelegram(context.bot, update.effective_chat.id, "Descreva a imagem que você quer gerar")

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
        await _responderNoTelegram(context.bot, update.effective_chat.id, "Ação cancelada.")

    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.chat_id)
    except:
        print("Não foi possível apagar a mensagem")

async def _cadastrarNovaConversa(chat_id, assunto, bot):
    await repository.RemoverAssuntoAtual(chat_id)
    await repository.CadastrarConversa(Conversas(chat_id=chat_id, assunto=assunto, assuntoAtual=True))
    await _responderNoTelegram(bot, chat_id, "Agora estamos falando sobre \"" + assunto + "\".\n\nPode me perguntar qualquer coisa.")

async def _gerarimagem(chat_id, descricaoImagem, bot):
    resposta = await open_ai.GerarImagem(descricaoImagem)
    await _responderNoTelegram(bot, chat_id, resposta)

async def _apagarConversa(update, context, conversa_id):
    conversa = await repository.ObterConversaPorId(conversa_id)

    if conversa is not None:
        if conversa.assuntoAtual:
            await _responderNoTelegram(context.bot, update.effective_chat.id, "Você não pode apagar a conversa atual.")
        else:
            Mensagens.delete().where(Mensagens.conversa_id == conversa_id).execute()
            Conversas.delete().where(Conversas.id == conversa_id).execute()
            await _responderNoTelegram(context.bot, update.effective_chat.id, "Conversa apagada")
    else:
        await _responderNoTelegram(context.bot, update.effective_chat.id, "Conversa não encontrada.")

async def _continuarConversa(update, context, conversa_id):
    conversa = await repository.ObterConversaPorId(conversa_id)

    if conversa is not None:
        Conversas.update(assuntoAtual=False).where(Conversas.chat_id == update.effective_chat.id).execute()
        Conversas.update(assuntoAtual=True).where(Conversas.id == conversa_id).execute()
        await _responderNoTelegram(context.bot, update.effective_chat.id, "Agora estamos falando sobre \"" + conversa.assunto + "\".\n\nPode me perguntar qualquer coisa.")
    else:
        await _responderNoTelegram(context.bot, update.effective_chat.id, "Conversa não encontrada.")

async def _responderNoTelegram(bot, chat_id, mensagem):
    try:
        await bot.send_message(chat_id=chat_id, text=mensagem)
    except:
        print("Erro ao enviar mensagem no Telegram. Tentando novamente")

def _ehPrivado(update):
    return str(update.effective_chat.type) == "private"

def _ehGrupo(update):
    return "group" in str(update.effective_chat.type)

def _falouComOBot(update):
    return str(update.effective_message.text).startswith("@ChatGPT_Oficial_Bot ") or (update.effective_message.reply_to_message is not None and update.effective_message.reply_to_message.from_user.username == "ChatGPT_Oficial_Bot")
