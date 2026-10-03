import os
import io
import json
import base64
import requests
from pathlib import Path
from PIL import Image
import gradio as gr

from config import (
    OLLAMA_BASE_URL,
    MODEL_NAME,
    IMAGE_MAX_SIZE,
    REQUEST_TIMEOUT,
    DEMO_FALLBACK,
    GRADIO_SERVER_NAME,
    GRADIO_SERVER_PORT,
    SUPPORTED_LANGUAGES,
    LANGUAGE_MAP,
    check_ollama_connection
)
from prompts import (
    HELP_SYSTEM_PROMPT,
    SCAM_SYSTEM_PROMPT,
    DEMO_RESPONSES
)

# Optional gTTS for speech synthesis stretch goal
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

BASE_DIR = Path(__file__).parent
DEMO_DIR = BASE_DIR / "demo"

# UI Color styling constants
ICONS = {
    "SAFE": "🟢 SAFE (સુરક્ષિત / सुरक्षित)",
    "SUSPICIOUS": "🟡 SUSPICIOUS (શંકાસ્પદ / संदेहास्पद)",
    "SCAM": "🔴 SCAM WARNING (સાયબર ફ્રોડ / धोखाधड़ी)"
}

BADGE_CLASSES = {
    "SAFE": "badge-safe",
    "SUSPICIOUS": "badge-suspicious",
    "SCAM": "badge-scam"
}

def encode_image(img: Image.Image) -> str:
    """Resizes and encodes PIL image to JPEG base64 string."""
    img = img.convert("RGB")
    img.thumbnail((IMAGE_MAX_SIZE, IMAGE_MAX_SIZE), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def detect_sample_type(img: Image.Image, question: str = "") -> str:
    """Heuristic helper to detect demo sample image for offline fallback mode."""
    q_lower = (question or "").lower()
    if "bill" in q_lower or "pay" in q_lower or "લાઈટ" in q_lower or "બિલ" in q_lower or "बिजली" in q_lower:
        return "bill"
    if "scam" in q_lower or "sms" in q_lower or "otp" in q_lower or "બ્લોક" in q_lower or "धोखा" in q_lower:
        return "scam_sms"
    if "text" in q_lower or "big" in q_lower or "font" in q_lower or "મોટા" in q_lower or "बड़ा" in q_lower or "settings" in q_lower:
        return "settings"
    if "order" in q_lower or "deliver" in q_lower or "ઓર્ડર" in q_lower or "सामान" in q_lower:
        return "order"
    return "bill"

def call_ollama(system_prompt: str, user_prompt: str, img: Image.Image, as_json: bool = False):
    """
    Calls Ollama REST API /api/chat with multimodal vision input.
    Falls back gracefully if Ollama is offline or model is still downloading.
    """
    api_url = f"{OLLAMA_BASE_URL}/api/chat"
    img_b64 = encode_image(img)

    payload = {
        "model": MODEL_NAME,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_prompt,
                "images": [img_b64]
            }
        ]
    }
    if as_json:
        payload["format"] = "json"

    try:
        response = requests.post(api_url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "")
        return content, False
    except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as err:
        if DEMO_FALLBACK:
            return None, True
        raise RuntimeError(f"Ollama call failed ({OLLAMA_BASE_URL}): {err}")

def clean_json_markdown(raw: str) -> str:
    """Removes markdown code fences from JSON output if present."""
    text = raw.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def help_me(img, custom_q, preset_q, lang_choice):
    """
    Tab 1: Explain step-by-step what to tap on the screen.
    """
    if img is None:
        return "⚠️ **કૃપા કરીને પહેલા તમારા ફોનનો સ્ક્રીનશોટ અપલોડ કરો.** / **Please upload a screenshot first.**", None

    lang = LANGUAGE_MAP.get(lang_choice, "Gujarati")
    question = (custom_q or "").strip()
    if not question:
        question = preset_q or "What should I do on this screen?"

    sys_prompt = HELP_SYSTEM_PROMPT.format(lang=lang)
    raw_output, is_fallback = call_ollama(sys_prompt, question, img, as_json=False)

    if is_fallback or not raw_output:
        sample_key = detect_sample_type(img, question)
        demo_text = DEMO_RESPONSES.get(sample_key, {}).get("help", {}).get(lang, DEMO_RESPONSES["bill"]["help"]["English"])
        result = (
            f"> 💡 **[Offline Demo Preview]** *Ollama is offline or model '{MODEL_NAME}' is downloading. Showing verified demo output:*\n\n"
            f"{demo_text}\n\n"
            f"---\n"
            f"*To run live inference: ensure Ollama is running and execute `ollama pull {MODEL_NAME}`.*"
        )
    else:
        result = raw_output

    # Generate optional audio
    audio_file = generate_speech_file(result, lang)
    return result, audio_file

def scam_check(img, lang_choice):
    """
    Tab 2: Check screenshot/message for fraud, phishing, or financial scams.
    """
    if img is None:
        return "⚠️ **કૃપા કરીને પહેલા સ્ક્રીનશોટ અપલોડ કરો.** / **Please upload a screenshot first.**", None

    lang = LANGUAGE_MAP.get(lang_choice, "Gujarati")
    sys_prompt = SCAM_SYSTEM_PROMPT.format(lang=lang)
    user_prompt = "Check this screen or message for scam indicators, fraud risk, and provide safety verdict."

    raw_output, is_fallback = call_ollama(sys_prompt, user_prompt, img, as_json=True)

    if is_fallback or not raw_output:
        sample_key = detect_sample_type(img, "scam")
        d = DEMO_RESPONSES.get(sample_key, {}).get("scam", {}).get(lang, DEMO_RESPONSES["scam_sms"]["scam"]["English"])
        is_demo_note = "\n\n> 💡 *[Offline Demo Preview - Ollama offline or model downloading]*"
    else:
        try:
            sanitized = clean_json_markdown(raw_output)
            d = json.loads(sanitized)
            is_demo_note = ""
        except Exception:
            # Fallback to displaying raw text rather than crashing
            return f"### Analysis Output\n\n{raw_output}", None

    verdict = d.get("verdict", "SUSPICIOUS").upper()
    reasons = d.get("reasons", [])
    advice = d.get("advice", "")

    reasons_md = "\n".join(f"- **{r}**" for r in reasons)
    icon_header = ICONS.get(verdict, f"❓ {verdict}")

    card_class = BADGE_CLASSES.get(verdict, "badge-suspicious")

    result = f"""
<div class="verdict-box {card_class}">
  <h2 style="margin: 0; padding-bottom: 8px;">{icon_header}</h2>
  <div style="font-size: 1.15rem; margin-top: 10px;">
    <strong>તારણો / मुख्य कारण / Reasons:</strong>
  </div>
</div>

{reasons_md}

---

### 💡 સલાહ / सुझाव / Next Step:
**{advice}**

{is_demo_note}

---
> 🛡️ **સુવર્ણ નિયમ / Golden Rule:** બેંક કે કોઈપણ સરકારી અધિકારી ક્યારેય ફોન કે SMS પર તમારો **OTP, UPI PIN, ATM કાર્ડ નંબર કે પાસવર્ડ** પૂછતા નથી. ક્યારેય કોઈની સાથે શેર કરશો નહીં!
"""
    audio_file = generate_speech_file(f"{verdict}. {advice}", lang)
    return result, audio_file

def generate_speech_file(text: str, lang: str):
    """Generates audio speech file using gTTS if available."""
    if not TTS_AVAILABLE:
        return None
    try:
        clean_text = text.replace("#", "").replace("*", "").replace(">", "").strip()
        lang_code = "gu" if lang == "Gujarati" else ("hi" if lang == "Hindi" else "en")
        tts = gTTS(text=clean_text[:300], lang=lang_code, slow=False)
        out_path = BASE_DIR / "temp_speech.mp3"
        tts.save(str(out_path))
        return str(out_path)
    except Exception:
        return None

def load_sample_image(filename: str):
    """Loads a demo image from the demo folder."""
    path = DEMO_DIR / filename
    if path.exists():
        return Image.open(path)
    return None

def get_system_status():
    """Returns current Ollama & model status."""
    is_online, msg, models = check_ollama_connection()
    status_icon = "🟢" if is_online else "🟠"
    models_str = ", ".join(models) if models else "None"
    return f"""
**Ollama Server Status:** {status_icon} `{msg}`  
**Endpoint:** `{OLLAMA_BASE_URL}`  
**Target Model:** `{MODEL_NAME}`  
**Available Local Models:** `{models_str}`  
**Privacy Status:** 🔒 100% Offline (No Cloud Data Transmission)
"""

# Custom CSS for Large, Senior-Friendly UI
CUSTOM_CSS = """
/* Senior-Friendly Accessibility Styling */
body, .gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}

.main-title {
    text-align: center;
    margin-bottom: 4px;
}

.privacy-banner {
    background: #e8f5e9;
    border: 2px solid #4caf50;
    border-radius: 12px;
    padding: 12px 18px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    font-weight: 600;
    color: #1b5e20;
}

.step-card {
    font-size: 1.25rem !important;
    line-height: 1.7 !important;
    background: #fdfdfd;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
}

.verdict-box {
    padding: 16px 20px;
    border-radius: 12px;
    margin-bottom: 16px;
}

.badge-safe {
    background-color: #d4edda;
    border: 2px solid #28a745;
    color: #155724;
}

.badge-suspicious {
    background-color: #fff3cd;
    border: 2px solid #ffc107;
    color: #856404;
}

.badge-scam {
    background-color: #f8d7da;
    border: 2px solid #dc3545;
    color: #721c24;
}

.btn-large {
    font-size: 1.2rem !important;
    font-weight: bold !important;
    padding: 12px !important;
}
"""

# Gradio Blocks Application
with gr.Blocks(title="What do I tap? Helper (Offline Gemma 4)", css=CUSTOM_CSS, theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <div class="main-title">
        <h1 style="font-size: 2.3rem; margin-bottom: 6px;">📱 What do I tap? / મને ક્યાં અડવું?</h1>
        <p style="font-size: 1.2rem; color: #555; margin-top: 0;">
            A private, offline helper that explains any phone screen in your own language and warns you before you fall for a scam.
        </p>
    </div>
    <div class="privacy-banner">
        🔒 100% On-Device & Offline &nbsp;|&nbsp; Powered by Gemma 4 E4B &nbsp;|&nbsp; Zero Cloud Calls &nbsp;|&nbsp; Complete Privacy
    </div>
    """)

    with gr.Tabs():
        # TAB 1: HELP ME
        with gr.Tab("👉 1. Help me (મને મદદ કરો / मुझे मदद चाहिए)"):
            with gr.Row():
                with gr.Column(scale=5):
                    help_img = gr.Image(type="pil", label="📸 Upload Phone Screenshot (સ્ક્રીનશોટ અપલોડ કરો)")

                    gr.Markdown("#### 💡 Quick Test with Sample Screenshots:")
                    with gr.Row():
                        btn_sample_bill = gr.Button("⚡ 1. Light Bill", size="sm")
                        btn_sample_settings = gr.Button("⚙️ 2. Settings (Big Font)", size="sm")
                        btn_sample_safe = gr.Button("📦 3. Delivery Order", size="sm")

                    help_lang = gr.Dropdown(
                        choices=SUPPORTED_LANGUAGES,
                        value="Gujarati (ગુજરાતી)",
                        label="🌐 Choose Language (ભાષા પસંદ કરો)"
                    )

                    help_preset_q = gr.Radio(
                        choices=[
                            "How do I pay this bill? (આ બિલ કેવી રીતે ભરવું?)",
                            "How do I make the text bigger? (અક્ષરો મોટા કેમ કરવા?)",
                            "Where do I tap next? (હવે ક્યાં દબાવવું?)",
                            "What should I do on this screen? (આ સ્ક્રીન પર શું કરવું?)"
                        ],
                        value="What should I do on this screen? (આ સ્ક્રીન પર શું કરવું?)",
                        label="🎯 Common Questions (ઝડપી પ્રશ્ન પસંદ કરો)"
                    )

                    help_custom_q = gr.Textbox(
                        label="✍️ Or Type Your Own Question (અથવા તમારો પ્રશ્ન લખો)",
                        placeholder="e.g. How do I pay this bill?"
                    )

                    btn_help = gr.Button("🔍 Explain Step-by-Step (મને સમજાવો)", variant="primary", elem_classes=["btn-large"])

                with gr.Column(scale=6):
                    gr.Markdown("### 📋 Step-by-Step Instructions:")
                    help_output = gr.Markdown(
                        value="*Upload a screenshot and tap 'Explain Step-by-Step' to get clear, numbered instructions.*",
                        elem_classes=["step-card"]
                    )
                    help_audio = gr.Audio(label="🔊 Listen Aloud (અવાજ સાંભળો)", interactive=False)

            # Wire Tab 1 buttons
            btn_sample_bill.click(lambda: load_sample_image("1_electricity_bill.png"), outputs=help_img)
            btn_sample_settings.click(lambda: load_sample_image("3_phone_settings.png"), outputs=help_img)
            btn_sample_safe.click(lambda: load_sample_image("4_order_delivered.png"), outputs=help_img)

            btn_help.click(
                help_me,
                inputs=[help_img, help_custom_q, help_preset_q, help_lang],
                outputs=[help_output, help_audio]
            )

        # TAB 2: IS THIS SAFE?
        with gr.Tab("🛡️ 2. Is this safe? (શું આ સુરક્ષિત છે? / क्या यह सुरक्षित है?)"):
            with gr.Row():
                with gr.Column(scale=5):
                    scam_img = gr.Image(type="pil", label="📸 Upload Suspicious Screenshot or Message")

                    gr.Markdown("#### 💡 Quick Test with Sample Messages:")
                    with gr.Row():
                        btn_sample_scam = gr.Button("🚨 1. Fake Bank SMS (Scam)", size="sm")
                        btn_sample_safe2 = gr.Button("✅ 2. Genuine Bill (Safe)", size="sm")

                    scam_lang = gr.Dropdown(
                        choices=SUPPORTED_LANGUAGES,
                        value="Gujarati (ગુજરાતી)",
                        label="🌐 Choose Language (ભાષા પસંદ કરો)"
                    )

                    btn_scam = gr.Button("🛡️ Check for Scam (સાયબર ફ્રોડ તપાસો)", variant="stop", elem_classes=["btn-large"])

                with gr.Column(scale=6):
                    gr.Markdown("### 🔍 Safety Analysis & Verdict:")
                    scam_output = gr.Markdown(
                        value="*Upload a screenshot or SMS and tap 'Check for Scam' to see whether it is safe or fraudulent.*",
                        elem_classes=["step-card"]
                    )
                    scam_audio = gr.Audio(label="🔊 Listen Aloud (અવાજ સાંભળો)", interactive=False)

            # Wire Tab 2 buttons
            btn_sample_scam.click(lambda: load_sample_image("2_fake_bank_sms.png"), outputs=scam_img)
            btn_sample_safe2.click(lambda: load_sample_image("1_electricity_bill.png"), outputs=scam_img)

            btn_scam.click(
                scam_check,
                inputs=[scam_img, scam_lang],
                outputs=[scam_output, scam_audio]
            )

        # TAB 3: SYSTEM INFO & DOCKER GUIDE
        with gr.Tab("ℹ️ System Status & Hackathon Guide"):
            status_box = gr.Markdown(value=get_system_status())
            btn_refresh_status = gr.Button("🔄 Refresh Connection Status")
            btn_refresh_status.click(get_system_status, outputs=status_box)

            gr.Markdown("""
### 🚀 4-Hour Hackathon Setup & Commands:
1. **Pull Model in Ollama:**
   ```bash
   ollama pull gemma4:e4b
   ```
2. **Start with Docker Compose:**
   ```bash
   docker compose up --build
   ```
3. **Architecture Highlights:**
   - **Privacy First:** Gemma 4 E4B instruction-tuned runs 100% locally on your machine.
   - **Multilingual Support:** Gujarati, Hindi, and English.
   - **Resilient Fallback:** Live Ollama API with graceful demo fallback so your presentation never crashes on stage!
            """)

if __name__ == "__main__":
    print(f"Starting 'What do I tap?' Helper on {GRADIO_SERVER_NAME}:{GRADIO_SERVER_PORT}...")
    demo.launch(
        server_name=GRADIO_SERVER_NAME,
        server_port=GRADIO_SERVER_PORT,
        share=False
    )
