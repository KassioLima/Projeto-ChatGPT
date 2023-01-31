import peewee

db = peewee.SqliteDatabase('BDconversas.db')

class BaseModel(peewee.Model):
    """Classe model base"""
    class Meta:
        # Indica em qual banco de dados a tabela
        # 'author' sera criada (obrigatorio). Neste caso,
        # utilizamos o banco 'codigo_avulso.db' criado anteriormente
        database = db

class lista_conversas(BaseModel):

    """
    Classe que representa a tabela lista_conversas
    """
    # A tabela possui apenas o campo 'name', que receberá o nome do autor sera unico
    chat_id = peewee.IntegerField()
    assunto = peewee.CharField(null=True)
    conversa = peewee.CharField(null=True)

class conversa_atual(BaseModel):

    """
    Classe que representa a tabela conversa_atual
    """
    # A tabela possui apenas o campo 'name', que receberá o nome do autor sera unico
    chat_id = peewee.IntegerField(unique=True)
    assunto = peewee.IntegerField(null=True)
    flag = peewee.BooleanField(null=True)

lista_conversas.create_table()
conversa_atual.create_table()