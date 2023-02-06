import datetime
import peewee

db = peewee.SqliteDatabase('BDconversas.db')

class BaseModel(peewee.Model):
    class Meta:
        database = db

class Chats(BaseModel):
    chat_id = peewee.PrimaryKeyField(null=False)
    aguardandoAssuntoDaConversa = peewee.BooleanField(default=False, null=False)

    def EstaAguardandoAlgo(self) -> bool:
        return self.aguardandoAssuntoDaConversa

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
    timestamp = peewee.DateTimeField(default=datetime.datetime.now, null=False)
    conversa = peewee.ForeignKeyField(Conversas, to_field='id', null=False)
    conversa_id = peewee.IntegerField(null=False)


Conversas.create_table()
Mensagens.create_table()
Chats.create_table()