from infra.model import Conversas, Chats, Mensagens, db
import functools

class Repository:

    def catch_exception(f):
        @functools.wraps(f)
        def func(*args, **kwargs):
            db.connect(reuse_if_open=True)
            return f(*args, **kwargs)

        return func

    @catch_exception
    async def ObterChatPorChatId(chat_id: int):
        chat = Chats.select().where(Chats.chat_id == chat_id).get_or_none()
        return chat

    @catch_exception
    async def CadastrarChat(chat: Chats):
        Chats.create(chat_id = chat.chat_id, aguardandoAssuntoDaConversa = chat.aguardandoAssuntoDaConversa)

    @catch_exception
    async def AtualizarChat(chat: Chats) -> int:
        return chat.save()

    @catch_exception
    async def ObterConversasPorChatId(chat_id: int):
        conversas = Conversas.select().where(Conversas.chat_id == chat_id)
        return conversas

    @catch_exception
    async def ObterConversaAtualPorChatId(chat_id: int):
        conversa = Conversas.select().where(Conversas.chat_id == chat_id).where(Conversas.assuntoAtual).get_or_none()
        return conversa

    @catch_exception
    async def ObterConversaPorId(id: int):
        conversa = Conversas.select().where(Conversas.id == id).get_or_none()
        return conversa

    @catch_exception
    async def CadastrarConversa(conversa: Conversas) -> int:
        return conversa.save()

    @catch_exception
    async def AtualizarConversa(conversa: Conversas) -> int:
        return conversa.save()

    @catch_exception
    async def RemoverAssuntoAtual(chat_id: int):
        Conversas.update(assuntoAtual = False).where(Conversas.chat_id == chat_id).execute()

    @catch_exception
    async def ObterMensagensPorConversaId(conversa_id: int):
        mensagens = Mensagens.select().order_by(Mensagens.id).where(Mensagens.conversa_id == conversa_id)
        return mensagens

    @catch_exception
    async def CadastrarMensagem(mensagem: Mensagens):
        mensagem.save()