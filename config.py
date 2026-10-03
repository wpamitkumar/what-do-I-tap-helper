import os
import requests
from typing import Tuple, List

# Core Configuration
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
MODEL_NAME = os.environ.get("MODEL_NAME", "gemma4:e4b")
IMAGE_MAX_SIZE = int(os.environ.get("IMAGE_MAX_SIZE", "1024"))
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "180"))
DEMO_FALLBACK = os.environ.get("DEMO_FALLBACK", "true").lower() in ("true", "1", "yes")

GRADIO_SERVER_NAME = os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0")
GRADIO_SERVER_PORT = int(os.environ.get("GRADIO_SERVER_PORT", "7860"))

SUPPORTED_LANGUAGES = [
    "Gujarati (ગુજરાતી)",
    "Hindi (हिन्दी)",
    "English"
]

LANGUAGE_MAP = {
    "Gujarati (ગુજરાતી)": "Gujarati",
    "Hindi (हिन्दी)": "Hindi",
    "English": "English"
}

def check_ollama_connection() -> Tuple[bool, str, List[str]]:
    """
    Checks if Ollama is responding and lists available models.
    Returns: (is_online, message, model_list)
    """
    try:
        url = f"{OLLAMA_BASE_URL}/api/tags"
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            data = res.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            has_target = any(MODEL_NAME in m for m in models)
            if has_target:
                msg = f"Connected to Ollama ({MODEL_NAME} ready)"
            elif models:
                msg = f"Connected to Ollama (Available: {', '.join(models[:3])}; target '{MODEL_NAME}' not found)"
            else:
                msg = f"Ollama is running, but no models found. Run: ollama pull {MODEL_NAME}"
            return True, msg, models
        else:
            return False, f"Ollama returned HTTP {res.status_code}", []
    except Exception as e:
        return False, f"Ollama offline ({OLLAMA_BASE_URL})", []
