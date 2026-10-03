FROM python:3.11-slim

# system tools for audio & healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    espeak \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# app source code
COPY . .

# create sample screenshots if not already present
RUN python generate_demo_assets.py || true

# default runtime config
ENV PYTHONUNBUFFERED=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860 \
    OLLAMA_BASE_URL=http://ollama:11434 \
    MODEL_NAME=gemma4:e4b

EXPOSE 7860

# verify web app is serving traffic
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

CMD ["python", "app.py"]
