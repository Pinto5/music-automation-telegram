import asyncio
import telegram
import os
import ollama_run as olm
import yt_dlp_music as dlp


# Número máximo de mensagens processadas ao mesmo tempo
MAX_CONCURRENT_UPDATES = 3


async def process_update(bot, update, api_key, semaphore, download_lock):
    # Limita quantas mensagens podem estar a ser processadas ao mesmo tempo
    async with semaphore:

        if not update.effective_chat:
            return
        if not update.message or not update.message.text:
            return

        # Guarda o ID do chat para responder ao utilizador correto
        chat_id = update.effective_chat.id

        # Guarda o texto enviado pelo utilizador
        message_received = update.message.text

        # Tenta encontrar um link do YouTube na mensagem
        link = dlp.save_link(message_received)

        # Começa sem metadados do vídeo
        video_info = None

        # Se existir link, tenta obter informações do vídeo
        if link:
            video_info = await asyncio.to_thread(dlp.get_video_info, link)
            print("VIDEO INFO:", video_info)

        try:
            # Se não houver link e a mensagem parecer sem sentido, responde sem chamar o Ollama
            if not link and olm.is_probably_gibberish(message_received):
                await bot.send_message(
                    chat_id=chat_id,
                    text="Não percebi a tua mensagem. Envia uma mensagem sobre música e/ou um link do YouTube."
                )
                return

            # Chama o Ollama numa thread separada para não bloquear o loop assíncrono
            message_to_send = await asyncio.to_thread(
                olm.ollama_run,
                message_received,
                api_key,
                link,
                video_info
            )

            # Se o Ollama devolver uma resposta válida, envia-a ao utilizador
            if message_to_send and message_to_send.strip():
                await bot.send_message(
                    chat_id=chat_id,
                    text=message_to_send
                )

            # Se o Ollama não devolver texto útil, envia uma resposta padrão
            else:
                await bot.send_message(
                    chat_id=chat_id,
                    text="Recebi a tua mensagem. Vou tentar processar o áudio se houver link."
                )

        except Exception as e:
            print(f"Ollama falhou: {e}")
            await bot.send_message(
                chat_id=chat_id,
                text="Não consegui gerar uma resposta, mas vou tentar processar o áudio se houver link."
            )

        if link:

            # Impede conflitos se duas tarefas tentarem usar o mesmo ficheiro ao mesmo tempo
            async with download_lock:

                # Faz o download numa thread separada porque yt_dlp é bloqueante
                audio_path = await asyncio.to_thread(dlp.download_music, link)

                # Se o download tiver criado um ficheiro válido, envia o áudio
                if audio_path:
                    try:
                        # Abre o ficheiro de áudio em modo binário
                        with open(audio_path, "rb") as audio_file:

                            # Envia o áudio para o chat correto
                            await bot.send_audio(
                                chat_id=chat_id,
                                audio=audio_file,
                                title=video_info.get("title") if video_info else None,
                                performer=video_info.get("uploader") if video_info else None,
                                read_timeout=120,
                                write_timeout=120,
                                connect_timeout=60,
                                pool_timeout=60
                            )

                    # Apaga o ficheiro depois de enviar, mesmo que ocorra algum erro no envio
                    finally:
                        if os.path.exists(audio_path):
                            os.remove(audio_path)

        # Se não houver link, apenas escreve isso na consola
        else:
            print("Mensagem sem link do YouTube.")

        # Mostra na consola para que chat a mensagem foi tratada
        print("Mensagem enviada para:", chat_id)


async def main(token, api_key):

    if not token:
        raise Exception("TELEGRAM_BOT_TOKEN não está definido.")


    if not api_key:
        raise Exception("OLLAMA_API_KEY não está definida.")

    # Cria o objeto do bot
    bot = telegram.Bot(token)

    # Limita o número de updates processados ao mesmo tempo
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_UPDATES)

    # Evita que dois downloads mexam no mesmo ficheiro ao mesmo tempo
    download_lock = asyncio.Lock()

    # Guarda tarefas em execução para evitar que sejam removidas da memória cedo demais
    # Necessário criar uma variável que guarda as tasks porque uma task sem referência forte pode ser recolhida pelo garbage collector antes de terminar.
    background_tasks = set()

    # Abre a sessão do bot
    async with bot:

        # Mostra informações do bot na consola
        print(await bot.get_me())

        # Vai buscar updates antigos ao iniciar
        updates = await bot.get_updates(timeout=10)

        # Guarda o último update antigo para não responder a mensagens antigas
        last_update_id = updates[-1].update_id if updates else None

        while True:

            # Define a partir de que update o bot deve procurar mensagens novas
            offset = last_update_id + 1 if last_update_id is not None else None

            # Espera por novos updates/mensagens
            new_updates = await bot.get_updates(
                offset=offset,
                timeout=10
            )

            if not new_updates:
                continue

            for update in new_updates:

                # Atualiza o último update processado
                last_update_id = update.update_id

                # Cria uma tarefa para processar este update sem bloquear os outros
                task = asyncio.create_task(
                    process_update(
                        bot,
                        update,
                        api_key,
                        semaphore,
                        download_lock
                    )
                )

                background_tasks.add(task)

                # Remove a tarefa da lista quando terminar
                task.add_done_callback(background_tasks.discard)

if __name__ == "__main__":

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    api_key = os.getenv("OLLAMA_API_KEY")

    asyncio.run(main(token, api_key))