#!/usr/bin/env bash
set -e

MODEL="${1:-gemma4:e4b}"

echo "=================================================="
echo " Pulling Multimodal Model: ${MODEL}"
echo "=================================================="

# Check if local Ollama binary exists
if command -v ollama >/dev/null 2>&1; then
    echo "⚡ Pulling via local host Ollama..."
    ollama pull "$MODEL"
    exit 0
fi

# Check if Docker Ollama container is running
if docker ps --format '{{.Names}}' | grep -q "what-do-i-tap-ollama"; then
    echo "🐳 Pulling via Docker Ollama container..."
    docker exec -it what-do-i-tap-ollama ollama pull "$MODEL"
    exit 0
fi

# Try REST API on port 11434
echo "🌐 Attempting to trigger pull via Ollama REST API (http://localhost:11434)..."
curl -X POST http://localhost:11434/api/pull -d "{\"name\": \"${MODEL}\", \"stream\": false}"

echo ""
echo "✅ Finished model pull check for: ${MODEL}"
