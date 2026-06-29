from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI()

@app.post("/extract-audio")
async def extract_audio(file: UploadFile = File(...)):
    uid = str(uuid.uuid4())

    input_file = f"/tmp/{uid}.mp4"
    output_file = f"/tmp/{uid}.mp3"

    with open(input_file,"wb") as f:
        f.write(await file.read())

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i",
        input_file,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        output_file
    ])

    return FileResponse(
        output_file,
        media_type="audio/mpeg",
        filename="audio.mp3"
    )
