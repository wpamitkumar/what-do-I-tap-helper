# "What do I tap?" Helper

A private, 100% offline multimodal AI assistant that explains confusing smartphone screens in **Gujarati**, **Hindi**, and **English**, visually highlights where to tap, and detects financial fraud, phishing links, and cyber scams before users tap them.

---

## Key Features

- 📱 **Step-by-Step Screen Guidance ("Help Me")**: Upload any phone screenshot, ask a question in plain everyday language, and receive up to 5 simple, numbered instructions.
- 🎯 **Visual "Where to Tap" Target Overlay**: Draws a high-visibility target ring and `👉 TAP HERE` badge directly on the screenshot so elderly or non-technical users can see exactly where to touch.
- 🎙️ **Microphone Voice Input**: Ask questions out loud using native browser speech recognition in Gujarati, Hindi, or English without having to type.
- 🔊 **Voice Readout**: In-browser text-to-speech reads answers aloud in your chosen language with zero external API latency.
- 🛡️ **Scam & Fraud Detection ("Is this safe?")**: Evaluates bank KYC threats, electricity cut-off notices, lottery claims, and suspicious APK downloads with color-coded safety badges (**SAFE**, **SUSPICIOUS**, **SCAM**).
- 💸 **UPI Collect & Refund Fraud Shield**: Detects tricky UPI collect requests and fake refunds, alerting users with a clear safety banner: *"Entering a UPI PIN always sends money, never receives money!"*
- 👨‍👩‍👦 **One-Click WhatsApp Family Alert**: Instantly pre-formats scam details and sends an alert via WhatsApp to family members or trusted contacts for a second opinion.
- 🔒 **100% Offline & Private**: Powered locally by Google's **Gemma 4 E4B** via **Ollama**. No screenshots, credentials, or personal queries are ever uploaded to cloud servers.

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
         │                     │  │  - Visual Tap Overlay  │    │  (Multimodal / 4B) │  │
         ▼                     │  │  - Scam Detection Tab  │    │                    │  │
  [Microphone / Voice Input]   │  │  - UPI Fraud Shield    │    │                    │  │
         │                     │  │  - WhatsApp Alert      │    │                    │  │
         ▼                     │  │  - Web Speech Reader   │    │                    │  │
 [Visual Steps / Safety Card] ◀│  └────────────────────────┘    └────────────────────┘  │
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
| **Visual Tap Annotator** | **Pillow (PIL)** | Programmatically draws high-contrast concentric target circles and badge overlays pointing to target UI coordinates. |
| **Voice Assist & Audio** | **Web Speech API & gTTS** | Browser-native speech recognition for voice queries and client-side speech synthesis for reading guidance aloud. |
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
├── README.md                   # Project overview, architecture, setup steps, tests, and credits
├── requirements.txt            # Python package dependencies
├── app.py                      # Main Gradio application (Help Me, Visual Overlay, Scam Shield)
├── config.py                   # Centralized configuration & standard-library Ollama healthcheck
├── prompts.py                  # Vision system prompts (Gujarati, Hindi, English) & demo responses
├── test_suite.py               # Automated test suite for configuration, prompts, and JSON parsing
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

## Testing & Verification

The project includes an automated test suite (`test_suite.py`) that validates core subsystems with or without Docker, verifying that model prompts, JSON parsing, heuristic classifiers, image rendering, and safety rules work as expected.

### Running the Automated Test Suite

#### Option 1: On Host (Local Python)
```bash
python3 test_suite.py
```

#### Option 2: Inside Running Docker Container
```bash
docker compose exec app python test_suite.py
```

### What the Test Suite Verifies

| Test Case | Scope | What It Validates |
| :--- | :--- | :--- |
| **1. Configuration & Ollama Engine** | `config.py` | Validates environment variables, base URL format, model name tag, and live connection/fallback status. |
| **2. Multilingual Vision Prompts** | `prompts.py` | Verifies prompt formatting for Gujarati (`ગુજરાતી`), Hindi (`हिन्दी`), and English, ensuring UPI fraud rules are enforced. |
| **3. Resilient JSON Extraction** | `app.py` | Tests edge-case LLM outputs: raw JSON, markdown-wrapped blocks (` ```json...``` `), unfenced blocks, and surrounding chatter. |
| **4. Multilingual Intent Heuristics** | `app.py` | Tests natural language query categorization across Gujarati, Hindi, and English (bill payments, scam SMS, font zoom, order tracking). |
| **5. Visual Tap Target Overlay** | `app.py` | Confirms the Pillow annotator successfully draws concentric target rings and `👉 TAP HERE` badges without coordinate overflows. |
| **6. Demo Screenshots Health** | `demo/` | Verifies that all 4 sample phone screenshots exist and contain valid PNG header signatures (`\x89PNG`). |
| **7. Licensing Compliance** | Repository | Verifies that the GNU General Public License v3.0 (`LICENSE`) and `README.md` are present and valid. |

### Manual Verification Scenarios

You can also test the application interactively using the built-in demo examples:

1. **Electricity Bill Payment (Help Me Tab)**:
   - Click the "Electricity Bill" example card.
   - Question: *"How do I pay this bill?"* (or *"આ લાઈટ બિલ કેવી રીતે ચૂકવવું?"*).
   - Expected Output: 5 numbered steps pinpointing the **"PROCEED TO PAY"** button, visual target overlay ring around the button, and audio playback.

2. **Fake Bank KYC Phishing (Is This Safe Tab)**:
   - Click the "Phishing Bank SMS" example card.
   - Question: *"Is this SMS safe?"* (or *"શું આ મેસેજ સાચો છે?"*).
   - Expected Output: **SCAM** badge (Red), reasons warning about urgent threats and suspicious links, and a pre-formatted **Alert Family on WhatsApp** button.

3. **Android Display & Font Size (Help Me Tab)**:
   - Click the "Phone Settings" example card.
   - Question: *"How do I make text size bigger?"*.
   - Expected Output: Step-by-step guidance navigating to **Display & Brightness ➔ Font Size**.

4. **E-Commerce Order Delivery (Help Me Tab)**:
   - Click the "Order Delivered" example card.
   - Question: *"Where is my package?"*.
   - Expected Output: Confirms delivery status and guides to the **"Need Help?"** button if items are missing.

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
| **[Pillow (PIL)](https://python-pillow.org/)** | Jeffrey A. Clark & Contributors | HPND | Image manipulation, alpha compositing, and visual "Where to tap" target ring drawing. |
| **[Requests](https://requests.readthedocs.io/)** | Kenneth Reitz & Contributors | Apache 2.0 | HTTP client for interacting with the local Ollama API. |
| **[Pydantic](https://docs.pydantic.dev/)** | Samuel Colvin & Contributors | MIT | Data validation and schema parsing. |
| **[Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)** | W3C / Browser Standard | Open Web Standard | In-browser speech recognition (microphone input) and text-to-speech audio narration. |
| **[gTTS](https://github.com/pndurette/gTTS)** | Pierre Nicolas Durette | MIT | Optional text-to-speech audio rendering utility. |
| **Demo UI Assets** | Generated in-repo | GPL-3.0 | Synthetic smartphone interface mockups generated via `generate_demo_assets.py`. |

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  
See the [LICENSE](LICENSE) file for the complete terms and conditions.
