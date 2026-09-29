import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
OUTPUT_DIR = BASE_DIR / "output"
DOWNLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
MAX_DOWNLOAD_MB = int(os.getenv("MAX_DOWNLOAD_MB", "2048"))
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")
FFPROBE_BIN = os.getenv("FFPROBE_BIN", "ffprobe")
BOT_API_BASE_URL = os.getenv("BOT_API_BASE_URL", "https://api.telegram.org/bot").strip()
BOT_API_FILE_URL = os.getenv("BOT_API_FILE_URL", "https://api.telegram.org/file/bot").strip()
BOT_API_LOCAL_MODE = os.getenv("BOT_API_LOCAL_MODE", "0").strip().lower() in {"1", "true", "yes", "on"}

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Put it in your .env file.")
