from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/extract-audio")
async def extract_audio(file: UploadFile = File(...)):
    uid = str(uuid.uuid4())

    input_file = f"/tmp/{uid}_{file.filename}"
    output_file = f"/tmp/{uid}.mp3"

    try:
        with open(input_file, "wb") as f:
            f.write(await file.read())

        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i", input_file,
                "-vn",
                "-ac", "1",
                "-ar", "16000",
                "-b:a", "24k",
                output_file
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=result.stderr
            )

        return FileResponse(
            output_file,
            media_type="audio/mpeg",
            filename="audio.mp3"
        )

    finally:
        if os.path.exists(input_file):
            os.remove(input_file)
