import requests
from transformers import GPT2Tokenizer
from os import getenv

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
_LIMIT_TOKENS = 4096
_LIMIT_TOKENS_PROMPT = _LIMIT_TOKENS / 2

def _contarTokens(text: str) -> int:
    tokens = tokenizer(text)["input_ids"]
    return len(tokens)

def cortarMensagemParaCaberNosTokens(mensagem) -> str:
    tokens_ids = tokenizer(mensagem)["input_ids"]

    if len(tokens_ids) <= _LIMIT_TOKENS_PROMPT:
        return mensagem
    else:
        tokens_ids = tokens_ids[-_LIMIT_TOKENS_PROMPT:]
        mensagemCortada = tokenizer.decode(tokens_ids)
        return mensagemCortada

async def EnviarMensagem(mensagemRecebida: str) -> str:
    n_tokens = _contarTokens(mensagemRecebida)

    params = {
        "model": "text-davinci-003",
        "prompt": mensagemRecebida,
        "max_tokens": _LIMIT_TOKENS - n_tokens,
        "temperature": 0
    }

    headers = {
        "Authorization": "Bearer " + getenv("CHAT_GPT_API_KEY"),
        "User-Agent": "MyApp/1.0",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.openai.com/v1/completions", json=params, headers=headers)
    resposta = response.json()["choices"][0]["text"]

    return resposta