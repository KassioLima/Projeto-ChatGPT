import datetime
import peewee

db = peewee.SqliteDatabase('BDconversas.db')

class BaseModel(peewee.Model):
    """Classe model base"""
    class Meta:
        # Indica em qual banco de dados a tabela
        # 'author' sera criada (obrigatorio). Neste caso,
        # utilizamos o banco 'codigo_avulso.db' criado anteriormente
        database = db

class Chats(BaseModel):
    chat_id = peewee.PrimaryKeyField(null=False)
    aguardandoAssuntoDaConversa = peewee.BooleanField(null=False, default=False)

class Conversas(BaseModel):
    id = peewee.PrimaryKeyField()
    chat = peewee.ForeignKeyField(Chats, to_field='chat_id')
    chat_id = peewee.IntegerField(null=False)
    assunto = peewee.CharField(null=False)
    assuntoAtual = peewee.BooleanField(null=False)

class Mensagens(BaseModel):
    id = peewee.PrimaryKeyField()
    mensagem = peewee.CharField(null=False)
    remetente = peewee.CharField(null=False)
    timestamp = peewee.DateTimeField(default=datetime.datetime.now)
    conversa = peewee.ForeignKeyField(Conversas, to_field='id')


Conversas.create_table()
Mensagens.create_table()
Chats.create_table()