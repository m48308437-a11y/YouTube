from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import os
import uuid
import shutil


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://m48308437-a11y.github.io"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


DOWNLOAD_FOLDER = "downloads"


os.makedirs(
    DOWNLOAD_FOLDER,
    exist_ok=True
)


class VideoRequest(BaseModel):
    url: str
    quality: str = "720"
    format: str = "mp4"


@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Downloader Backend is running!"
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


@app.post("/download")
def download_video(
    request: VideoRequest,
    background_tasks: BackgroundTasks
):

    download_id = str(uuid.uuid4())

    download_path = os.path.join(
        DOWNLOAD_FOLDER,
        download_id
    )

    os.makedirs(
        download_path,
        exist_ok=True
    )


    try:

        if request.format == "mp3":

            options = {

                "format": "bestaudio/best",

                "outtmpl": os.path.join(
                    download_path,
                    "%(title)s.%(ext)s"
                ),

                "noplaylist": True,

                "quiet": True,

                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192"
                    }
                ]

            }


        else:

            options = {

                "format": (
                    f"bestvideo[height<={request.quality}]"
                    "+bestaudio/"
                    f"best[height<={request.quality}]"
                ),

                "outtmpl": os.path.join(
                    download_path,
                    "%(title)s.%(ext)s"
                ),

                "merge_output_format": "mp4",

                "noplaylist": True,

                "quiet": True

            }


        with yt_dlp.YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                request.url,
                download=True
            )


        files = os.listdir(
            download_path
        )


        if not files:

            raise Exception(
                "فایل دانلود نشد"
            )


        file_path = os.path.join(
            download_path,
            files[0]
        )


        background_tasks.add_task(
            shutil.rmtree,
            download_path,
            ignore_errors=True
        )


        return FileResponse(
            path=file_path,
            filename=os.path.basename(
                file_path
            ),
            media_type="application/octet-stream"
        )


    except Exception as e:

        if os.path.exists(
            download_path
        ):

            shutil.rmtree(
                download_path,
                ignore_errors=True
            )


        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
