# Music Automation Telegram

Este é um bot de Telegram feito em Python para ajudar com temas relacionados com música.

O bot responde a mensagens sobre músicas, artistas, álbuns e géneros musicais. Também consegue receber links do YouTube, obter informações básicas sobre o vídeo e tentar enviar o áudio para o utilizador.

Este projeto junta Telegram, Ollama e `yt-dlp` numa automação simples e prática.

## O que o bot faz

* Responde a mensagens relacionadas com música.
* Usa o Ollama para gerar respostas curtas e úteis.
* Deteta links do YouTube enviados no chat.
* Obtém informações do vídeo, como título, canal e duração.
* Descarrega o áudio com `yt-dlp`.
* Envia o áudio diretamente no Telegram.
* Consegue processar várias mensagens ao mesmo tempo usando `asyncio`.

## Tecnologias usadas

* Python
* Telegram Bot API
* Ollama
* yt-dlp
* imageio-ffmpeg
* requests
* asyncio

## Estrutura do projeto

```text
music-automation-telegram/
├── app.py
├── ollama_run.py
├── yt_dlp_music.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Como colocar o projeto a funcionar

### 1. Clonar o projeto

```bash
git clone https://github.com/Pinto5/music-automation-telegram.git
cd music-automation-telegram
```

### 2. Criar e ativar o ambiente virtual

No Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

Este projeto precisa de duas variáveis:

* `TELEGRAM_BOT_TOKEN`
* `OLLAMA_API_KEY`

No PowerShell, podes definir assim:

```powershell
$env:TELEGRAM_BOT_TOKEN="coloca_aqui_o_token_do_teu_bot"
$env:OLLAMA_API_KEY="coloca_aqui_a_tua_api_key_da_ollama"
```

Estas chaves são privadas. Não devem ser colocadas diretamente no código nem enviadas para o GitHub.

### 5. Garantir que o Ollama está disponível

O projeto usa o modelo `llama3.2` através do Ollama local.

Se ainda não tiveres o modelo, podes instalar com:

```bash
ollama pull llama3.2
```

Depois garante que o Ollama está a correr no teu computador.

### 6. Executar o bot

```bash
python app.py
```

Se tudo estiver configurado corretamente, o bot começa a receber mensagens no Telegram.

## Segurança

Este projeto usa tokens e API keys, por isso é importante ter cuidado antes de enviar código para o GitHub.

O ficheiro `.gitignore` deve impedir que sejam enviados ficheiros como:

```text
.env
.venv/
downloads/
__pycache__/
```

A pasta `downloads/` também não deve ir para o GitHub, porque é usada para guardar temporariamente os ficheiros de áudio descarregados.

## Nota

Este projeto foi feito para aprendizagem e automação pessoal.


## Autor

Projeto desenvolvido por Pinto5.
