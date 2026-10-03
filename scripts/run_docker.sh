#!/usr/bin/env bash
set -e

echo "=================================================="
echo " Starting 'What do I tap?' Helper with Docker"
echo "=================================================="

# make sure docker daemon is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker daemon is not running. Please start Docker Desktop and retry."
    exit 1
fi

# support both modern 'docker compose' and older 'docker-compose'
if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
else
    echo "❌ Error: Neither 'docker compose' nor 'docker-compose' was found."
    exit 1
fi

echo "🐳 Building and starting containers with $COMPOSE (App + Ollama)..."
$COMPOSE up --build -d

echo ""
echo "✅ Containers are starting up!"
echo "📍 Gradio Web UI will be available at: http://localhost:7860"
echo "📍 Ollama API is available at:       http://localhost:11434"
echo ""
echo "To pull the Gemma 4 model into the container, run:"
echo "   docker compose exec ollama ollama pull gemma4:e4b"
echo ""
echo "To view live application logs:"
echo "   docker compose logs -f app"
