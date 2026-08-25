from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Downloader Backend is running!"
    }


@app.get("/test")
def test():
    return {
        "status": "success",
        "message": "API is working!"
    }


@app.get("/info")
def get_info(url: str):

    options = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True
    }

    try:

        with yt_dlp.YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        return {
            "success": True,
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "channel": info.get("uploader")
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }
