#!/usr/bin/env bash
set -e

MODEL="${1:-gemma4:e4b}"

echo "=================================================="
echo " Pulling Multimodal Model: ${MODEL}"
echo "=================================================="

# 1. try host ollama first if installed locally
if command -v ollama >/dev/null 2>&1; then
    echo "⚡ Pulling via local host Ollama..."
    ollama pull "$MODEL"
    exit 0
fi

# 2. next check if the docker container is running
if docker ps --format '{{.Names}}' | grep -q "what-do-i-tap-ollama"; then
    echo "🐳 Pulling via Docker Ollama container..."
    IT_FLAG=""
    if [ -t 0 ]; then
        IT_FLAG="-it"
    fi
    docker exec $IT_FLAG what-do-i-tap-ollama ollama pull "$MODEL"
    exit 0
fi

# 3. fallback: trigger via the ollama rest api
echo "🌐 Triggering pull via Ollama REST API (http://localhost:11434)..."
curl -X POST http://localhost:11434/api/pull -d "{\"name\": \"${MODEL}\", \"stream\": false}"

echo ""
echo "✅ Finished model pull check for: ${MODEL}"
