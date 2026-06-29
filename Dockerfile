FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn python-multipart

CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8000"]
