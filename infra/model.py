import datetime
import peewee
from os import getenv
from dotenv import load_dotenv

load_dotenv()

db = peewee.MySQLDatabase(getenv("DATABASE_NAME"), user=getenv("DATABASE_USER"), password=getenv("DATABASE_PASSWORD"), host=getenv("DATABASE_HOST"), port=3306, autoconnect=True)

class BaseModel(peewee.Model):
    class Meta:
        database = db

class Chats(BaseModel):
    chat_id = peewee.PrimaryKeyField(null=False)
    aguardandoAssuntoDaConversa = peewee.BooleanField(default=False, null=False)
    aguardandoDescricaoImagem = peewee.BooleanField(default=False, null=False)

class Conversas(BaseModel):
    id = peewee.PrimaryKeyField()
    chat_id = peewee.IntegerField(null=False)
    assunto = peewee.CharField(null=False)
    assuntoAtual = peewee.BooleanField(null=False)

class Mensagens(BaseModel):
    id = peewee.PrimaryKeyField()
    mensagem = peewee.CharField(null=False)
    remetente = peewee.CharField(null=False)
    timestamp = peewee.DateTimeField(default=datetime.datetime.now, null=False)
    conversa_id = peewee.IntegerField(null=False)


# Conversas.create_table()
# Mensagens.create_table()
# Chats.create_table()