from  model import lista_conversas, conversa_atual,db
from peewee import fn as fn

#result = lista_conversas.select(fn.Max(lista_conversas.assunto)).group_by(lista_conversas.assunto)

# query = lista_conversas.select().dicts()
# for row in query:
#     print(row)

query = lista_conversas.select(fn.Max(lista_conversas.assunto)).get()

print(query.assunto)