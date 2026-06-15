import yt_dlp
import imageio_ffmpeg
import re
import os


# Função para extrair apenas o link da mensagem
def save_link(message):
    pattern = r"https?://(?:www\.|m\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)[A-Za-z0-9_-]+(?:[^\s]*)?"
    result = re.search(pattern, message)

    if result:
        return result.group(0).rstrip(".,);]!?")
    return None

# Função para obter informaçõess sobre o link
def get_video_info(url):
    opts = {
        "quiet": True,
        "noplaylist": True,
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title") or info.get("fulltitle"),
            "uploader": info.get("uploader") or info.get("channel"),
            "duration": info.get("duration"),
            "webpage_url": info.get("webpage_url"),
        }

    except Exception as e:
        print(f"Failed to get video info: {e}")
        return None

def download_music(url):

    if url is None:
        print("No url found.")
        return None
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    opts = {
        "format" : "bestaudio/best",
        "ffmpeg_location" : ffmpeg_path,
        "noplaylist" : True,
        "postprocessors" : [{
            "key" : "FFmpegExtractAudio",
            "preferredcodec" : "mp3",
            "preferredquality" : 192,
        }],
        "outtmpl": "downloads/%(id)s.%(ext)s" ,
    }
    try:
        os.makedirs("downloads" , exist_ok = True)
        with yt_dlp.YoutubeDL(opts) as ydl:

            info = ydl.extract_info(url, download=True)
            video_id = info["id"]
            file_path = f"downloads/{video_id}.mp3"
            if os.path.exists(file_path):
                return file_path
            return None
    except Exception as e:
        print(f"Download failed {e}")
        return None