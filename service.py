import requests
from transformers import GPT2Tokenizer
import openai
from os import getenv
from model import lista_conversas, conversa_atual
from peewee import fn

async def ResponderAComContexto(chat_id: int, bot, conversa):
    openai.api_key = getenv("CHAT_GPT_API_KEY")

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokens = tokenizer(" ".join(conversa))["input_ids"]
    n_tokens = len(tokens)

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=" ".join(conversa),
        max_tokens=4096-n_tokens,
        n=1,
        stop=None,
        temperature=0
    )

    await bot.send_message(chat_id=chat_id, text=response["choices"][0].text)
    
async def ResponderA(mensagemRecebida: str, chat_id: int, bot):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokens = tokenizer(mensagemRecebida)["input_ids"]
    n_tokens = len(tokens)

    params = {
        "model": "text-davinci-003",
        "prompt": mensagemRecebida,
        "max_tokens": 4096 - n_tokens,
        "temperature": 0
    }

    headers = {
        "Authorization": "Bearer " + getenv("CHAT_GPT_API_KEY"),
        "User-Agent": "MyApp/1.0",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.openai.com/v1/completions", json=params, headers=headers)
    resposta = response.json()["choices"][0]["text"]

    id_assunto_atual = lista_conversas.select(fn.Max(lista_conversas.assunto)).get()
    
    id_assunto_novo = id_assunto_atual + 1
    
    lista_conversas.create(chat_id= chat_id, assunto= id_assunto_novo, conversa=mensagemRecebida + resposta )

    conversa_atual.create(chat_id= chat_id, assunto= id_assunto_novo, flag=True)

    await bot.send_message(chat_id=chat_id, text=resposta)