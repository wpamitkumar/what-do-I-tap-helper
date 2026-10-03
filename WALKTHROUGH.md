# 📱 "What do I tap?" Helper — Complete Project Walkthrough

This guide walks you through the entire **"What do I tap?" Helper** system, explaining its architecture, how to start and operate it, and how each feature assists users with smartphone confusion and cyber scam prevention.

---

## 1. System Overview & Problem Statement

Many older adults and non-technical users struggle with modern smartphone interfaces:
- Complex nested menus, ambiguous icons, and unfamiliar button labels.
- Predatory cyber scams, fake bank KYC messages, and phishing links threatening urgent penalties.
- Language barriers when apps are in English or formal technical jargon.

**"What do I tap?" Helper** solves this by running an **instruction-tuned multimodal model (Google's Gemma 4)** locally on the user's laptop:
- **100% Offline & Private:** Zero cloud calls. Sensitive personal screenshots never leave the machine.
- **Multilingual:** Generates clear, plain-language guidance in **Gujarati**, **Hindi**, and **English**.
- **Two Specialized Pipelines:**
  1. **"Help me"**: Analyzes screen UI to give up to 5 numbered steps naming exact button labels and locations.
  2. **"Is this safe?"**: Inspects messages or screens for urgency, malicious links, and OTP phishing, returning color-coded verdicts (**SAFE**, **SUSPICIOUS**, **SCAM**).

---

## 2. Architecture & Runtime Flow

```
                      ┌────────────────────────────────────────────────────────┐
                      │              Local Machine / Container Network         │
                      │                                                        │
[Phone Screenshot]    │  ┌────────────────────────┐    ┌────────────────────┐  │
        │             │  │   Gradio Application   │    │   Ollama Runtime   │  │
        ▼             │  │      (Port 7860)       │───▶│    (Port 11434)    │  │
 [Pick Language]      │  │                        │    │                    │  │
(Gujarati/Hindi/Eng)  │  │  - Help Me Pipeline    │◀───│  Gemma 4 E4B       │  │
        │             │  │  - Scam Detection Tab  │    │  (Multimodal / 4B) │  │
        ▼             │  │  - Web Speech Reader   │    │                    │  │
 [Step / Verdict] ◀───│  └────────────────────────┘    └────────────────────┘  │
                      │                                          ▲             │
                      │                                          │             │
                      │                               ┌─────────────────────┐  │
                      │                               │ Persistent Volume   │  │
                      │                               │ (what-do-i-tap-     │  │
                      │                               │  ollama-models)     │  │
                      │                               └─────────────────────┘  │
                      └────────────────────────────────────────────────────────┘
```

1. **Gradio UI (`app.py`)**: Receives the image and question, handles alpha-channel compositing, resizes to 1024px JPEG, and encodes to base64.
2. **Local Ollama Daemon (`ollama`)**: Serves `gemma4:e4b` on `http://localhost:11434`.
3. **Structured Response**:
   - Tab 1 outputs markdown steps and optional audio.
   - Tab 2 enforces JSON formatting and parses verdict, reasons, and advice into visual cards.
4. **Resilient Fallback Mode**: If Ollama is offline or model download is in progress, the app automatically serves verified outputs for sample cases, ensuring zero UI crashes.

---

## 3. Step-by-Step Setup & Launch Walkthrough

### Step 3.1: Launch Docker Containers
Open your terminal in the project directory:
```bash
cd /Users/amitdudhat/Documents/hackathon/what-do-I-tap-helper
docker compose up --build -d
```
Verify both containers are running:
```bash
docker ps
```
You will see:
- `what-do-i-tap-app` on port `7860`
- `what-do-i-tap-ollama` on port `11434`

### Step 3.2: Pull the Multimodal Model
Run this once to download the Gemma 4 model into the persistent volume:
```bash
docker compose exec ollama ollama pull gemma4:e4b
```
*(If low on RAM or internet bandwidth, use `gemma4:e2b` and set `MODEL_NAME=gemma4:e2b` in `.env`)*

### Step 3.3: Access the Application
Open your browser to:
👉 **[http://localhost:7860](http://localhost:7860)**

---

## 4. UI Feature Walkthrough

### Tab 1: 👉 "Help me" (મને મદદ કરો / मुझे मदद चाहिए)

Designed for users who are stuck on a screen and don't know what to tap.

```
+-----------------------------------------------------------------------------------+
|  [📸 Upload Screenshot]               |  [📋 Step-by-Step Instructions]           |
|                                       |                                           |
|  Quick Samples:                       |  1. Verify bill amount ₹1,450 in center.  |
|  [⚡ 1. Light Bill] [⚙️ 2. Settings]   |  2. Look at bottom for green "Pay Now".   |
|  [📦 3. Delivery]                     |  3. Tap "Pay Now" once.                   |
|                                       |  4. Select UPI or Bank app.               |
|  🌐 Language: Gujarati (ગુજરાતી)       |  5. ⚠️ Never share your UPI PIN.          |
|                                       |                                           |
|  🎯 Preset: How do I pay this bill?   |  [🔊 Read Aloud (Browser Voice)] [⏹️ Stop]|
|  ✍️ Custom Question: [              ]  |  [🎧 Audio File Playback]                 |
|                                       |                                           |
|  [🔍 Explain Step-by-Step (Button)]   |                                           |
+-----------------------------------------------------------------------------------+
```

1. **Image Input:** Drag and drop any phone screenshot or tap one of the 1-click sample buttons (`⚡ Light Bill`, `⚙️ Settings`, `📦 Delivery`).
2. **Language Selector:** Choose Gujarati (`ગુજરાતી`), Hindi (`हिन्दी`), or English.
3. **Question Input:** Pick from common questions or type a custom question.
4. **Output Action Card:**
   - Maximum 5 numbered steps.
   - Names buttons exactly as printed on the phone screen.
   - Specifies physical locations (`top`, `bottom`, `middle`, `left`, `right`).
   - Inserts security warnings if a PIN, password, or OTP is mentioned.
5. **Senior Voice Assistance:**
   - Click **"🔊 Read Aloud"** to trigger native browser Web Speech API synthesis in Gujarati or Hindi without cloud latency.

---

### Tab 2: 🛡️ "Is this safe?" (શું આ સુરક્ષિત છે? / क्या यह सुरक्षित है?)

Designed to evaluate suspicious SMS alerts, unexpected WhatsApp links, or threatening popups.

```
+-----------------------------------------------------------------------------------+
|  [📸 Upload Message Screenshot]       |  [🔍 Safety Analysis & Verdict]           |
|                                       |                                           |
|  Quick Samples:                       |  +-------------------------------------+  |
|  [🚨 1. Fake Bank SMS] [✅ 2. Safe Bill]|  | 🔴 SCAM WARNING (સાયબર ફ્રોડ)      |  |
|                                       |  +-------------------------------------+  |
|  🌐 Language: Gujarati (ગુજરાતી)       |  - Artificial urgency & threat of block   |
|                                       |  - Suspicious non-bank link URL           |
|  [🛡️ Check for Scam (Button)]          |  - Unauthorized KYC update request        |
|                                       |                                           |
|                                       |  💡 Next Step: Delete & block sender.     |
|                                       |                                           |
|                                       |  🛡️ Golden Rule: Banks never ask for OTP!|
+-----------------------------------------------------------------------------------+
```

1. **Color-Coded Verdict Badges:**
   - 🟢 **SAFE:** Legitimate screens with verified context.
   - 🟡 **SUSPICIOUS:** Unknown sender or ambiguous request.
   - 🔴 **SCAM WARNING:** High-risk fraud, OTP harvesting, or phishing URLs.
2. **Key Reasons:** Up to 3 concise bullet points identifying red flags.
3. **Concrete Advice:** Direct, simple instruction (e.g. *"Delete this message immediately and do not open the link"*).
4. **Permanent Safety Notice:** Reinforces that banks never request UPI PINs or OTPs over phone or SMS.

---

### Tab 3: ℹ️ System Status & Info

Provides real-time visibility into the system:
- Connection status with the local Ollama daemon (🟢 Online / 🟠 Offline).
- List of pulled models currently available locally.
- Active endpoint (`http://localhost:11434` or container bridge).
- Privacy verification confirmation.

---

## 5. Walkthrough of Built-in Test Cases

The application includes 4 pre-loaded test cases that can be triggered with one click:

| Test Case | Scenario | Expected Behavior & Output |
|---|---|---|
| **1. Electricity Bill** (`1_electricity_bill.png`) | Older user wants to pay electricity bill. | **Output:** 5 numbered steps identifying the green **"PAY NOW"** button at the bottom center, due date, and a reminder never to disclose UPI PIN. |
| **2. Fake Bank SMS** (`2_fake_bank_sms.png`) | Urgent phishing SMS claiming account is blocked. | **Output:** **🔴 SCAM WARNING**. Reasons highlight false urgency ("penalty of ₹25,000"), unverified URL, and phishing for OTP. Advice: Delete and block. |
| **3. Phone Settings** (`3_phone_settings.png`) | User wants to enlarge small system text. | **Output:** Navigates user to tap **"Display"**, scroll down to **"Font size and style"**, and slide text scaler to the right. |
| **4. Delivery Order** (`4_order_delivered.png`) | User checks grocery delivery status. | **Output:** **🟢 SAFE**. Confirms valid order status, mentions item receipt, and directs to "Need Help?" button if package is missing. |

---

## 6. Key Developer & Operational Commands

| Action | Command |
|---|---|
| Start services | `docker compose up --build -d` |
| View live application logs | `docker compose logs -f app` |
| View Ollama server logs | `docker compose logs -f ollama` |
| Check pulled models | `docker compose exec ollama ollama list` |
| Pull Gemma 4 model | `docker compose exec ollama ollama pull gemma4:e4b` |
| Stop all services | `docker compose down` |
| Run test suite | `python3 scratch/test_suite.py` |
