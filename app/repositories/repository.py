from app.model import Conversas, Chats, Mensagens

async def ObterChatPorChatId(chat_id: int):
    chat = Chats.select().where(Chats.chat_id == chat_id).get_or_none()
    return chat

async def CadastrarChat(chat: Chats):
    Chats.create(chat_id = chat.chat_id, aguardandoAssuntoDaConversa = chat.aguardandoAssuntoDaConversa)

async def AtualizarChat(chat: Chats) -> int:
    return chat.save()

async def ObterConversasPorChatId(chat_id: int):
    conversas = Conversas.select().where(Conversas.chat_id == chat_id)
    return conversas

async def ObterConversaAtualPorChatId(chat_id: int):
    conversa = Conversas.select().where(Conversas.chat_id == chat_id).where(Conversas.assuntoAtual).get_or_none()
    return conversa

async def ObterConversaPorId(id: int):
    conversa = Conversas.select().where(Conversas.id == id).get_or_none()
    return conversa

async def CadastrarConversa(conversa: Conversas) -> int:
    return conversa.save()

async def AtualizarConversa(conversa: Conversas) -> int:
    return conversa.save()

async def RemoverAssuntoAtual(chat_id: int):
    Conversas.update(assuntoAtual = False).where(Conversas.chat_id == chat_id).execute()

async def ObterMensagensPorConversaId(conversa_id: int):
    mensagens = Mensagens.select().order_by(Mensagens.id).where(Mensagens.conversa_id == conversa_id)
    return mensagens

async def CadastrarMensagem(mensagem: Mensagens):
    mensagem.save()