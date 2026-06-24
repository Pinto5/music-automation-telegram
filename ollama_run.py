from ollama import chat
import requests
import re

# Pesquisa na web usando a API do Ollama
def fetch_answer(api_key,question):
    response = requests.post(
        "https://ollama.com/api/web_search",
        headers={
            "Authorization" : f"Bearer {api_key}",
            "Content-Type" : "application/json",
        },
        json={
            "query" : question,
            "max_results": 3, # Número de fontes/páginas de pesquisa
        },
    )
    return response

# Preparar os resultados para enviar ao modelo local
def prepare_results_web(question, results):
    context = ""

    if results:
        for i, result in enumerate(results, start=1):
            title = result.get("title", "")
            url = result.get("url", "")
            content = result.get("content", "")

            # Limita o tamanho do conteúdo
            content = content[:700]

            context += f"""
            Resultado {i}
            Título: {title}
            URL: {url}
            Resumo: {content}
            """
    else:
        context = "Não foram encontrados resultados de pesquisa."

    prompt = f"""
    Mensagem do utilizador:
    {question}

    Resultados de pesquisa disponíveis:
    {context}

    Instrução para esta resposta:
    Primeiro, verifica se a pergunta está relacionada com música.
    Se não estiver relacionada com música, responde apenas:
    "Só consigo ajudar com temas relacionados com música."

    Se estiver relacionada com música, usa os resultados acima apenas se forem relevantes.
    Não menciones "resultado 1", "resultado 2", "resultado 3" ou números de resultados.
    Não digas frases como "os resultados encontrados dizem".
    Não fales sobre a pesquisa em si.
    Responde diretamente ao utilizador.
    Se os resultados não forem suficientes, diz isso claramente.
    Não inventes informação.
    Responde de forma curta, natural e útil.
    """

    return prompt
    
def send_local_ollama(prompt):
    final_answer = requests.post(
        "http://localhost:11434/api/chat",
        json = {
            "model" : "llama3.2",
            "messages": [
                {
                    "role" : "system",
                    "content": """
                    És um bot de música no Telegram.

                    Responde sempre em português de Portugal.

                    A tua função é ajudar o utilizador com temas relacionados com música, incluindo:
                    - músicas;
                    - artistas;
                    - álbuns;
                    - géneros musicais;
                    - letras de forma geral;
                    - links do YouTube enviados pelo utilizador.

                    Regras:
                    - Responde de forma curta, natural e útil.
                    - Se a mensagem não estiver relacionada com música, diz educadamente que só ajudas com temas de música.
                    - Se a mensagem for confusa ou sem sentido, pede ao utilizador para reformular.
                    - Se receberes um link do YouTube, responde apenas com base na mensagem, no link e nos metadados disponíveis.
                    - Não inventes informação.
                    - Não digas que analisaste áudio, vídeo ou letra completa se esses dados não foram fornecidos.
                    - Não simules progresso como "estou a processar", "estou a descarregar" ou "estou a analisar".
                    """
                },
                {
                    "role": "user",
                    "content" : prompt,
                },
            ],
            "stream" : False,
        },
    )        
    return final_answer    

# Verifica se a mensagem enviada pelo utilizador não é troll
def is_probably_gibberish(text):
    if not text:
        return True

    text = text.strip().lower()

    if not text:
        return True

    # Se tiver link, não é gibberish
    if re.search(r"https?://", text):
        return False

    # Mensagens curtas aceitáveis num bot de música
    short_valid_messages = {
        "oi", "olá", "ola", "ok", "sim", "não", "nao",
        "rock", "pop", "rap", "trap", "funk", "jazz",
        "dj", "bts", "r&b"
    }

    if text in short_valid_messages:
        return False

    # Uma única letra normalmente não é uma mensagem útil
    if len(text) == 1:
        return True

    # Exemplo: "aaaaaa", "!!!!!!", "??????"
    if re.fullmatch(r"(.)\1{3,}", text):
        return True

    # Remove símbolos para analisar melhor o conteúdo
    cleaned = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", "", text).strip()

    if not cleaned:
        return True

    words = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", cleaned)

    if not words:
        return True

    # Se só tiver números, provavelmente não interessa para o bot
    has_letters = any(char.isalpha() for char in cleaned)

    if not has_letters:
        return True

    # Demasiados símbolos em relação ao tamanho da mensagem
    non_space_chars = re.sub(r"\s+", "", text)
    symbols = re.findall(r"[^a-zA-ZÀ-ÿ0-9\s]", text)

    if len(non_space_chars) >= 6:
        symbol_ratio = len(symbols) / len(non_space_chars)
        if symbol_ratio > 0.5:
            return True

    vowels = "aeiouáàâãéêíóôõúü"

    for word in words:
        # Palavras curtas como "bts", "dj", "rap" ou "rnb" devem passar
        if len(word) <= 4:
            continue

        vowel_count = sum(char in vowels for char in word)

        # Palavra grande sem vogais: provavelmente aleatória
        if len(word) >= 8 and vowel_count == 0:
            return True

        # Muitas consoantes seguidas costuma indicar texto aleatório
        if re.search(r"[bcdfghjklmnpqrstvwxyzç]{7,}", word):
            return True

    # Padrões comuns de teclado aleatório
    keyboard_noise = ["asdf", "qwer", "zxcv", "hjkl"]

    if any(pattern in text for pattern in keyboard_noise) and len(text.replace(" ", "")) >= 6:
        return True

    return False

def is_bot_identity_question(text):
    if not text:
        return False

    text = text.strip().lower()

    # Remove pontuação simples
    text = re.sub(r"[?!.,;:]+", "", text)

    identity_questions = {
        "quem és",
        "quem es",
        "quem és tu",
        "quem es tu",
        "quem é você",
        "quem e voce",
        "quem és você",
        "quem es voce",
        "o que és",
        "o que es",
        "o que és tu",
        "o que es tu",
        "que bot és",
        "que bot es",
        "quem é o bot",
        "quem e o bot"
    }

    return text in identity_questions

def is_greeting(text):
    if not text:
        return False

    text = text.strip().lower()
    text = re.sub(r"[?!.,;:]+", "", text)

    greetings = {
        "ola",
        "olá",
        "oi",
        "boas",
        "bom dia",
        "boa tarde",
        "boa noite",
        "hey",
        "hello",
        "hi"
    }

    return text in greetings

def ollama_run(message_received, api_key, link=None, video_info = None):
    if not api_key:
        raise Exception("API key do Ollama não existe.")
    
    if is_greeting(message_received):
        return "Olá! Sou um bot assistente de música. Posso ajudar-te com músicas, artistas, álbuns, géneros musicais e links do YouTube."

    if is_bot_identity_question(message_received):
        return "Sou um bot de música no Telegram. Posso ajudar-te com músicas, artistas, álbuns, géneros musicais e links do YouTube."
    
    if link:
        question = f"""
        Mensagem do utilizador:
        {message_received}

        Link do YouTube encontrado:
        {link}

        Metadados reais do vídeo:
        Título: {video_info.get("title") if video_info else "desconhecido"}
        Canal: {video_info.get("uploader") if video_info else "desconhecido"}
        Duração: {video_info.get("duration") if video_info else "desconhecida"} segundos

        Instrução para esta resposta:
        Responde com base apenas na mensagem, no link e nos metadados acima.
        Se o título ou o canal indicarem claramente a música ou o artista, podes mencionar isso.
        Não inventes artista, título, álbum, letra ou contexto.
        Não digas que o link é inválido.
        Não expliques o URL.
        No fim, escreve exatamente: "Vou tentar enviar o áudio a seguir."
        """

        final_answer = send_local_ollama(question)
        final_answer.raise_for_status()

        model_data = final_answer.json()
        return model_data["message"]["content"]

    question = message_received

    search_response = fetch_answer(api_key, question)
    search_response.raise_for_status()

    search_data = search_response.json()
    results = search_data["results"]

    web_results = prepare_results_web(question, results)

    final_answer = send_local_ollama(web_results)
    final_answer.raise_for_status()

    model_data = final_answer.json()

    return model_data["message"]["content"]