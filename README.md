# 📱 "What do I tap?" Helper

> **One-line Pitch:** *"A private, offline helper that explains any phone screen in your own language and warns you before you fall for a scam."*

[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](#-running-with-docker-recommended)
[![Offline Gemma 4](https://img.shields.io/badge/Gemma_4-E4B_Instruction_Tuned-8E75C4)](#-architecture)
[![Languages](https://img.shields.io/badge/Languages-Gujarati%20%7C%20Hindi%20%7C%20English-blue)](#-key-features)
[![Privacy First](https://img.shields.io/badge/Privacy-100%25_On--Device-success)](#-architecture)

---

## 📖 Overview

Many older adults and non-tech-savvy users struggle with modern smartphone interfaces, unfamiliar buttons, complex menus, and predatory cyber scams. 

**"What do I tap?" Helper** is an **on-device, 100% offline multimodal AI assistant** designed specifically for them:
1. **Upload a screenshot** of any confusing app or screen.
2. **Pick a language** (**Gujarati / ગુજરાતી**, **Hindi / हिन्दी**, or **English**).
3. **Ask a question** (or tap a quick preset like *"How do I pay this bill?"* or *"Where do I tap next?"*).
4. Get **short, numbered, step-by-step instructions** identifying exact button names, their positions on screen, and safety warnings.
5. **Scam Detection Tab:** Detects fake bank alerts, lottery fraud, urgency pressure, phishing links, and malicious OTP requests with instant color-coded verdicts (**SAFE**, **SUSPICIOUS**, **SCAM**).
6. **Zero Cloud Leaks:** Runs completely locally on the device using Google's **Gemma 4 E4B** via Ollama. No private data or personal financial screenshots ever leave the laptop.

---

## 🏛️ Architecture

```
                               ┌────────────────────────────────────────────────────────┐
                               │                 "What do I tap?" Laptop                │
                               │                                                        │
[User Phone Screenshot]        │  ┌────────────────────────┐    ┌────────────────────┐  │
          │                    │  │      Gradio Web UI     │    │   Ollama Engine    │  │
          ▼                    │  │  (Port 7860 - Docker)  │───▶│  (Port 11434)      │  │
  [Pick Language]              │  │                        │    │                    │  │
(Gujarati / Hindi / English)   │  │  - Help Me Tab         │◀───│  Gemma 4 E4B       │  │
          │                    │  │  - Scam Check Tab      │    │  (Multimodal / 4B) │  │
          ▼                    │  │  - Speech Synthesis   │    │                    │  │
 [Numbered Steps / Verdict] ◀──│  └────────────────────────┘    └────────────────────┘  │
                               │                                                        │
                               │  🔒 100% Local Container Network (Zero Cloud Calls)     │
                               └────────────────────────────────────────────────────────┘
```

| Layer | Choice & Role |
| :--- | :--- |
| **Model** | **Gemma 4 E4B instruction-tuned** (multimodal vision + text, 140+ languages, runs in ~4.5 GB RAM at 4-bit quantization). |
| **Runtime** | **Ollama** in Docker or local host (exposes local REST API on port `11434`). |
| **Application** | **Python + Gradio (Blocks)** with high-contrast, senior-friendly typography and quick demo buttons. |
| **Structured Output** | JSON format enforcement for the Scam Check tab to render color-coded risk cards. |
| **Audio Assist** | Text-to-speech audio reader for step instructions. |
| **Docker** | Multi-container setup with persistent volume for cached AI models. |

---

## 🚀 Running with Docker (Recommended)

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose installed.

### 2. Start Services
From the project root:
```bash
docker compose up --build -d
```
This spins up:
- **`ollama`** container on `http://localhost:11434` with persistent volume `what-do-i-tap-ollama-models`.
- **`app`** container hosting the Gradio UI on `http://localhost:7860`.

### 3. Pull Gemma 4 Model into the Container
Run this once to download Gemma 4 into Ollama:
```bash
docker compose exec ollama ollama pull gemma4:e4b
```
*(If your laptop has less than 8 GB of RAM, you can use `gemma4:e2b` by updating `MODEL_NAME` in `.env`)*

### 4. Open Application
Open your browser and visit:
👉 **[http://localhost:7860](http://localhost:7860)**

---

## 💻 Running Locally (Without Docker)

If you prefer to run directly on your host machine:

### 1. Install Ollama and pull Gemma 4
```bash
# In your host terminal:
ollama pull gemma4:e4b
```

### 2. Set Up Python Environment
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```
Open **[http://localhost:7860](http://localhost:7860)** in your browser.

---

## 🎯 4-Hour Hackathon Workflow

| Phase | Milestone | Deliverable |
| :--- | :--- | :--- |
| **Hour 1 (0:00 - 1:00)** | Model Verification & Vision Pipeline | Tested multimodal API call in terminal; benchmarked latency in Gujarati, Hindi, and English. |
| **Hour 2 (1:00 - 2:00)** | "Help Me" Tab & Accessible UI | Gradio Blocks layout, large senior-friendly fonts, numbered steps with button positions, preset question chips. |
| **Hour 3 (2:00 - 3:00)** | "Is This Safe?" Scam Tab & Polish | Structured JSON output parsing, color-coded badges (🟢 SAFE, 🟡 SUSPICIOUS, 🔴 SCAM), permanent security warnings, speech assist. |
| **Hour 4 (3:00 - 4:00)** | Edge-Case Testing, Demo Recording & Pitch | Test edge cases (no image, blurry screen), freeze code, record 90s backup video, rehearse pitch. |

---

## 🧪 Demo Screenshots & Test Cases

The application includes 4 built-in test screenshots located in `demo/`, with 1-click test buttons directly in the UI:

| Sample | Screenshot File | Question | Expected Output |
| :--- | :--- | :--- | :--- |
| ⚡ **Electricity Bill** | `demo/1_electricity_bill.png` | *"How do I pay this bill?"* | 3 to 5 steps naming the real **"Pay Now"** button at the bottom; warning never to share UPI PIN. |
| 🚨 **Fake Bank SMS** | `demo/2_fake_bank_sms.png` | *"Is this safe?"* | Verdict: **🔴 SCAM**, reasons cite artificial urgency ("Account Blocked"), unknown link, and OTP phishing. |
| ⚙️ **Phone Settings** | `demo/3_phone_settings.png` | *"How do I make the text bigger?"* | Steps to locate **"Display"**, tap **"Font size and style"**, and slide text scaler. |
| 📦 **Delivery Order** | `demo/4_order_delivered.png` | *"Is this safe?"* | Verdict: **🟢 SAFE**, legitimate delivery confirmation, advice to contact in-app help if package missing. |

---

## 🎤 90-Second Pitch Script

- **[0:00 - 0:15] Problem:**  
  *"My grandmother cannot tell a real bank message from a phishing scam, and she is afraid to tap anything on her phone for fear of losing her savings."*
- **[0:15 - 0:45] Help Me Demo:**  
  *"With 'What do I tap?', she snaps a screenshot of an electricity bill and asks in Gujarati: 'આ બિલ કેવી રીતે ભરવું?'. Gemma 4 reads the screen offline and gives her 3 clear steps: 'Look at the bottom, tap the green Pay Now button, and enter your UPI PIN safely'."*
- **[0:45 - 1:10] Scam Check Demo:**  
  *"Next, she gets an SMS claiming her bank account is blocked. She switches to the Scam Check tab: instantly, a bright red **SCAM WARNING** appears: 'Fake urgency, suspicious link, and illegal request for OTP'."*
- **[1:10 - 1:20] Why Gemma 4:**  
  *"Gemma 4 E4B is multimodal, understands 140+ languages natively, and fits in under 5 GB of RAM directly on a standard laptop."*
- **[1:20 - 1:30] Close:**  
  *"It's 100% private, free, and nothing ever leaves her phone. Thank you!"*

---

## 🛡️ Risks and Fallback Strategy

| Risk | Mitigation |
| :--- | :--- |
| **Model tag differs in Ollama** | Configurable via `MODEL_NAME` in `.env` or the UI Status tab. |
| **Inference latency on older laptops** | Built-in `IMAGE_MAX_SIZE=1024` thumbnail compression downsamples high-res screenshots before inference. |
| **Ollama still downloading during demo** | Built-in **Demo Fallback Mode** (`DEMO_FALLBACK=true` in `.env`) automatically serves verified demo responses for sample screenshots so presenters never get stuck with a blank screen. |
| **Scam JSON parsing issues** | `clean_json_markdown()` automatically strips backticks; falls back to clean raw text if JSON is malformed. |

---

## 📂 Project Structure

```
what-do-I-tap-helper/
├── Dockerfile                  # Production container for Gradio app
├── docker-compose.yml          # Multi-container setup (app + ollama + model-puller)
├── .dockerignore               # Optimized container build
├── .env.example                # Environment variables template
├── .env                        # Active environment configuration
├── requirements.txt            # Python dependencies (gradio, requests, pillow, gtts)
├── app.py                      # Core Gradio UI (Help Me & Scam Check tabs)
├── config.py                   # Centralized configuration & Ollama health check
├── prompts.py                  # Multilingual prompts & verified demo fallbacks
├── generate_demo_assets.py     # Script generating mock phone screenshots
├── demo/                       # 4 realistic sample test screenshots
│   ├── 1_electricity_bill.png
│   ├── 2_fake_bank_sms.png
│   ├── 3_phone_settings.png
│   └── 4_order_delivered.png
├── scripts/
│   ├── run_docker.sh           # One-click Docker launcher
│   ├── run_local.sh            # Local virtualenv runner
│   └── pull_model.sh           # Model download helper
└── README.md                   # Complete documentation & Pitch guide
```

---

## 📋 Hackathon Submission Checklist

- [x] Code pushed to GitHub with comprehensive README.
- [x] Docker setup (`Dockerfile` & `docker-compose.yml`) tested and documented.
- [x] Gemma 4 E4B multimodal offline prompts configured for Gujarati, Hindi, and English.
- [x] Tab 1 ("Help Me") with numbered steps and button location guidance.
- [x] Tab 2 ("Is This Safe?") with JSON-parsed color-coded verdict (SAFE / SUSPICIOUS / SCAM).
- [x] 4 realistic demo screenshots created in `demo/` with 1-click test buttons.
- [x] Resilient demo fallback mode ensuring zero crashes on stage.
- [x] 90-second pitch script and demo workflow rehearsed.
