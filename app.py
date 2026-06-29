from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import subprocess
import uuid
import os
import zipfile
import shutil
import glob

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/extract-audio-chunks")
async def extract_audio_chunks(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    uid = str(uuid.uuid4())
    workdir = f"/tmp/{uid}"
    os.makedirs(workdir, exist_ok=True)

    input_file = f"{workdir}/input.mp4"
    audio_dir = f"{workdir}/audio"
    zip_file = f"{workdir}/chunks.zip"

    os.makedirs(audio_dir, exist_ok=True)

    try:
        with open(input_file, "wb") as f:
            f.write(await file.read())

        result = subprocess.run([
            "ffmpeg",
            "-y",
            "-i", input_file,
            "-vn",
            "-ac", "1",
            "-ar", "16000",
            "-b:a", "24k",
            "-f", "segment",
            "-segment_time", "3600",
            "-reset_timestamps", "1",
            f"{audio_dir}/chunk_%03d.mp3"
        ], capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)

        chunks = sorted(glob.glob(f"{audio_dir}/chunk_*.mp3"))

        if not chunks:
            raise HTTPException(status_code=500, detail="No se generaron chunks de audio")

        with zipfile.ZipFile(zip_file, "w") as zipf:
            for chunk in chunks:
                zipf.write(chunk, os.path.basename(chunk))

        background_tasks.add_task(shutil.rmtree, workdir, ignore_errors=True)

        return FileResponse(
            zip_file,
            media_type="application/zip",
            filename="audio_chunks.zip"
        )

    except Exception:
        shutil.rmtree(workdir, ignore_errors=True)
        raise
