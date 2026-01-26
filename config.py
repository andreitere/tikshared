import os
from pathlib import Path

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

EXPIRY_HOURS = 4
PORT = int(os.environ.get("PORT", 8008))
BASE_URL = os.environ.get("BASE_URL", f"http://localhost:{PORT}")

# Quality presets: name -> yt-dlp format string
QUALITY_PRESETS = {
    "best": "best[ext=mp4]/best",
    "1080p": "best[height<=1080][ext=mp4]/best[height<=1080]",
    "720p": "best[height<=720][ext=mp4]/best[height<=720]",
    "480p": "best[height<=480][ext=mp4]/best[height<=480]",
    "worst": "worst[ext=mp4]/worst",
}

DEFAULT_QUALITY = "best"