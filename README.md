# "What do I tap?" Helper

A private, 100% offline multimodal AI assistant that explains confusing smartphone screens in **Gujarati**, **Hindi**, and **English**, and detects financial fraud, phishing links, and cyber scams before users tap them.

---

## Architecture

The application is architected to run entirely on-device with zero cloud dependencies. No screenshots, credentials, or personal queries ever leave the host machine.

```
                              ┌────────────────────────────────────────────────────────┐
                              │                 Host Machine / Docker Network          │
                              │                                                        │
[Phone Screenshot]            │  ┌────────────────────────┐    ┌────────────────────┐  │
        │                     │  │   Gradio Application   │    │   Ollama Runtime   │  │
        ▼                     │  │      (Port 7860)       │───▶│    (Port 11434)    │  │
 [Pick Language]              │  │                        │    │                    │  │
(Gujarati / Hindi / English)  │  │  - Help Me Pipeline    │◀───│  Gemma 4 E4B       │  │
        │                     │  │  - Scam Detection Tab  │    │  (Multimodal / 4B) │  │
        ▼                     │  │  - Web Speech Reader   │    │                    │  │
 [Step Actions / Verdict] ◀───│  └────────────────────────┘    └────────────────────┘  │
                              │                                          ▲             │
                              │                                          │             │
                              │                               ┌─────────────────────┐  │
                              │                               │ Persistent Volume   │  │
                              │                               │ (Cached AI Models)  │  │
                              │                               └─────────────────────┘  │
                              └────────────────────────────────────────────────────────┘
```

### Architectural Components

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Vision Language Model** | **Gemma 4 E4B** | Multimodal instruction-tuned model from Google (~4.5 GB RAM at 4-bit). Understands screenshot UI layout, icons, text, and 140+ languages. |
| **Model Runtime** | **Ollama** | Local REST API server exposing port `11434` for streaming or structured inference. |
| **Frontend UI** | **Gradio (Blocks)** | Senior-friendly web interface with high-contrast elements, font scaling, and instant sample loaders. |
| **Speech Assist** | **Web Speech API & gTTS** | Client-side native browser synthesis for Gujarati, Hindi, and English, with offline audio fallback. |
| **Containerization** | **Docker & Compose** | Multi-container isolation for predictable deployment on macOS, Linux, and Windows. |

---

## File Structure

```
what-do-I-tap-helper/
├── Dockerfile                  # Container definition with Python 3.11, audio libraries, and healthcheck
├── docker-compose.yml          # Compose specification defining app, ollama, and persistent volume
├── .dockerignore               # Build exclusion rules
├── .env.example                # Environment variable configuration template
├── .env                        # Active runtime configuration
├── .gitignore                  # Git repository exclusion rules
├── LICENSE                     # GNU General Public License v3.0 (GPL-3.0)
├── requirements.txt            # Python package dependencies
├── app.py                      # Main Gradio application (Help Me & Scam Check pipelines)
├── config.py                   # Centralized configuration & standard-library Ollama healthcheck
├── prompts.py                  # Vision system prompts (Gujarati, Hindi, English) & demo responses
├── generate_demo_assets.py     # Programmatic generator for realistic phone UI test screens
├── demo/                       # Sample mobile screenshots for testing
│   ├── 1_electricity_bill.png  # Utility bill payment scenario
│   ├── 2_fake_bank_sms.png     # Phishing SMS asking for urgent KYC/OTP
│   ├── 3_phone_settings.png    # Native OS settings (Display & Font size)
│   └── 4_order_delivered.png   # E-commerce delivery confirmation
└── scripts/
    ├── run_docker.sh           # Automated Docker Compose launcher with engine detection
    ├── run_local.sh            # Local virtual environment setup and execution script
    └── pull_model.sh           # Helper script to pull Gemma 4 into Ollama container or host
```


---

## Steps to Run the Project

### Option A: Running with Docker (Recommended)

#### 1. Start the Containers
Ensure Docker Desktop is running, then execute:
```bash
docker compose up --build -d
```
This launches:
- **Gradio Web Interface**: `http://localhost:7860`
- **Ollama Engine**: `http://localhost:11434`

#### 2. Download the Multimodal Model
Pull the Gemma 4 model into the persistent Ollama storage volume:
```bash
docker compose exec ollama ollama pull gemma4:e4b
```
*(For laptops with limited RAM under 8 GB, use `gemma4:e2b` and set `MODEL_NAME=gemma4:e2b` in `.env`)*

#### 3. Open the App
Visit **[http://localhost:7860](http://localhost:7860)** in your browser.

---

### Option B: Running Locally (Without Docker)

#### 1. Install & Start Ollama
Install Ollama from [ollama.com](https://ollama.com/) and pull the model:
```bash
ollama pull gemma4:e4b
```

#### 2. Set Up Python Environment
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run the application
python app.py
```

Open **[http://localhost:7860](http://localhost:7860)** in your browser.

---

## Configuration (`.env`)

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Endpoint for the Ollama API (set to `http://ollama:11434` in Docker). |
| `MODEL_NAME` | `gemma4:e4b` | Multimodal model tag (`gemma4:e4b` or `gemma4:e2b`). |
| `GRADIO_SERVER_NAME`| `0.0.0.0` | Host binding for Gradio. |
| `GRADIO_SERVER_PORT`| `7860` | Web server port. |
| `IMAGE_MAX_SIZE` | `1024` | Maximum image dimension in pixels before encoding (smaller = faster). |
| `DEMO_FALLBACK` | `true` | Serves verified demo outputs if Ollama is offline or model is downloading. |

---

## Third-Party Resources & Credits

This project relies on the following open-source libraries, models, and tools:

| Resource | Author / Provider | License | Purpose / Role |
| :--- | :--- | :--- | :--- |
| **[Gemma 4](https://ai.google.dev/gemma)** | Google DeepMind / Google | Gemma Terms of Use | Lightweight, state-of-the-art multimodal vision-language foundation model. |
| **[Ollama](https://github.com/ollama/ollama)** | Ollama Team | MIT | Local inference runtime engine for running open-weights LLMs. |
| **[Gradio](https://github.com/gradio-app/gradio)** | Hugging Face Gradio Team | Apache 2.0 | Reactive web UI framework for ML and multimodal applications. |
| **[Pillow (PIL)](https://python-pillow.org/)** | Jeffrey A. Clark & Contributors | HPND | Image manipulation, resizing, alpha compositing, and thumbnail generation. |
| **[Requests](https://requests.readthedocs.io/)** | Kenneth Reitz & Contributors | Apache 2.0 | HTTP client for interacting with the local Ollama API. |
| **[Pydantic](https://docs.pydantic.dev/)** | Samuel Colvin & Contributors | MIT | Data validation and schema parsing. |
| **[Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)** | W3C / Browser Standard | Open Web Standard | In-browser client-side text-to-speech without external API latency. |
| **[gTTS](https://github.com/pndurette/gTTS)** | Pierre Nicolas Durette | MIT | Optional text-to-speech audio rendering utility. |
| **Demo UI Assets** | Generated in-repo | GPL-3.0 | Synthetic smartphone interface mockups generated via `generate_demo_assets.py`. |

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  
See the [LICENSE](LICENSE) file for the complete terms and conditions.
