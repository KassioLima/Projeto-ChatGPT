import requests
from transformers import GPT2Tokenizer
import openai
from os import getenv

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
        "Authorization": "Bearer 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",
        "User-Agent": "MyApp/1.0",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.openai.com/v1/completions", json=params, headers=headers)

    await bot.send_message(chat_id=chat_id, text=response.json()["choices"][0]["text"])