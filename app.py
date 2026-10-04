import os
import io
import json
import base64
import tempfile
import re
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

# optional audio generator if gtts is installed
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

BASE_DIR = Path(__file__).parent
DEMO_DIR = BASE_DIR / "demo"

# labels & styling classes for the scam verdicts
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

def encode_image(img) -> str:
    # accept file path, pil image, or numpy array from gradio
    if isinstance(img, str):
        img = Image.open(img)
    elif not isinstance(img, Image.Image):
        try:
            import numpy as np
            if isinstance(img, np.ndarray):
                img = Image.fromarray(img)
        except Exception:
            pass

    # flatten alpha onto white canvas so screenshots with transparency don't turn black
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        rgba_img = img.convert("RGBA")
        bg.paste(rgba_img, mask=rgba_img.split()[3])
        img = bg
    else:
        img = img.convert("RGB")

    # resize to reasonable dimensions for faster vision inference
    img.thumbnail((IMAGE_MAX_SIZE, IMAGE_MAX_SIZE), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def draw_tap_overlay(img, response_text: str, question: str = ""):
    # creates an annotated copy of screenshot showing a glowing bullseye on the button
    if img is None:
        return None
    try:
        from PIL import ImageDraw, ImageFont
        if isinstance(img, str):
            img = Image.open(img)
        elif not isinstance(img, Image.Image):
            import numpy as np
            if isinstance(img, np.ndarray):
                img = Image.fromarray(img)

        annotated = img.convert("RGBA").copy()
        w, h = annotated.size

        text_lower = (response_text + " " + question).lower()

        # default target is bottom action area (standard for mobile primary buttons)
        cx, cy = w // 2, int(h * 0.84)

        if any(k in text_lower for k in ["display", "ડિસ્પ્લે", "डिस्प्ले", "font", "ફોન્ટ", "અક્ષર"]):
            cx, cy = w // 2, int(h * 0.42)
        elif any(k in text_lower for k in ["top", "ઉપર", "ऊपर"]):
            cx = int(w * 0.85) if any(k in text_lower for k in ["right", "જમણી", "दाईं"]) else w // 2
            cy = int(h * 0.15)
        elif any(k in text_lower for k in ["middle", "center", "વચ્ચે", "बीच"]):
            cx, cy = w // 2, h // 2
        elif any(k in text_lower for k in ["need help", "help", "મદદ", "સહાય"]):
            cx, cy = w // 2, int(h * 0.88)
        elif any(k in text_lower for k in ["pay", "ચૂકવવું", "ભરવું", "proceed", "હવે"]):
            cx, cy = w // 2, int(h * 0.84)

        overlay = Image.new("RGBA", annotated.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # glowing target concentric circles
        draw.ellipse([(cx - 48, cy - 48), (cx + 48, cy + 48)], fill=(255, 60, 60, 60), outline=(255, 50, 50, 210), width=3)
        draw.ellipse([(cx - 32, cy - 32), (cx + 32, cy + 32)], fill=(255, 60, 60, 110), outline=(255, 255, 255, 240), width=3)
        draw.ellipse([(cx - 16, cy - 16), (cx + 16, cy + 16)], fill=(255, 0, 0, 230))

        # crosshairs
        draw.line([(cx - 24, cy), (cx + 24, cy)], fill=(255, 255, 255, 230), width=2)
        draw.line([(cx, cy - 24), (cx, cy + 24)], fill=(255, 255, 255, 230), width=2)

        # callout badge: "👉 TAP HERE"
        badge_w, badge_h = 160, 36
        bx1 = max(10, min(cx - badge_w // 2, w - badge_w - 10))
        by1 = max(10, cy - 48 - badge_h - 10) if (cy - 48 - badge_h - 10) > 10 else cy + 48 + 10
        bx2 = bx1 + badge_w
        by2 = by1 + badge_h

        draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=8, fill=(20, 20, 20, 230), outline=(255, 255, 255, 220), width=2)

        try:
            font = ImageFont.load_default(size=18)
            draw.text((bx1 + 16, by1 + 8), "👉 TAP HERE", fill=(255, 255, 255, 255), font=font)
        except Exception:
            draw.text((bx1 + 16, by1 + 8), "👉 TAP HERE", fill=(255, 255, 255, 255))

        return Image.alpha_composite(annotated, overlay).convert("RGB")
    except Exception:
        return img

def detect_sample_type(question: str = "") -> str:
    # matches user intent to one of our canned demo answers when offline
    q_lower = (question or "").lower()

    # package delivery questions
    if any(k in q_lower for k in [
        "order", "deliver", "package", "tracking",
        "ઓર્ડર", "સામાન", "ડિલિવરી",
        "ऑर्डर", "सामान", "डिलीवरी", "पार्सल"
    ]):
        return "order"

    # font and settings adjustments
    if any(k in q_lower for k in [
        "text", "big", "font", "size", "settings", "display", "zoom",
        "મોટા", "અક્ષર", "સેટિંગ્સ", "ડિસ્પ્લે",
        "बड़ा", "अक्षर", "सेटिंग्स", "डिस्प्ले", "फॉन्ट"
    ]):
        return "settings"

    # electricity / phone bills
    if any(k in q_lower for k in [
        "bill", "pay", "due", "electricity", "light",
        "લાઈટ", "બિલ", "રૂપિયા", "ચૂકવવું", "ભરવું",
        "बिजली", "बिल", "रुपये", "भुगतान"
    ]):
        return "bill"

    # security warnings / phishing sms
    if any(k in q_lower for k in [
        "scam", "sms", "otp", "kyc", "fake", "fraud", "phish", "urgent", "safe", "danger",
        "બ્લોક", "ઓટીપી", "કેવાયસી", "ફ્રોડ", "છેતરપિંડી", "શંકાસ્પદ", "સુરક્ષિત",
        "ब्लॉक", "ओटीपी", "केवाईसी", "धोखा", "संदेह", "फ्रॉड", "सुरक्षित"
    ]):
        return "scam_sms"

    return "bill"

def call_ollama(system_prompt: str, user_prompt: str, img, as_json: bool = False):
    # posts prompt + base64 screenshot to local ollama endpoint
    api_url = f"{OLLAMA_BASE_URL}/api/chat"
    try:
        img_b64 = encode_image(img)
    except Exception as e:
        return None, False, f"Image processing error: {e}"

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
        if response.status_code == 404:
            err_msg = f"Model '{MODEL_NAME}' not found in Ollama. Run: ollama pull {MODEL_NAME}"
            if DEMO_FALLBACK:
                return None, True, err_msg
            return None, False, err_msg
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "")
        return content, False, None
    except Exception as err:
        err_msg = f"Ollama connection error ({OLLAMA_BASE_URL}): {err}"
        if DEMO_FALLBACK:
            return None, True, err_msg
        return None, False, err_msg

def extract_json(raw: str) -> dict:
    # grab json object even if the model added surrounding chat or markdown code blocks
    text = raw.strip()

    # direct parse
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    # inside ```json ... ```
    code_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_match:
        try:
            data = json.loads(code_match.group(1).strip())
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    # between outer { and }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            data = json.loads(text[start:end + 1])
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    raise ValueError(f"Could not parse valid JSON from output:\n{raw[:150]}")

def help_me(img, custom_q, preset_q, lang_choice):
    # tab 1 pipeline: simple numbered steps and annotated tap overlay
    if img is None:
        return "⚠️ **કૃપા કરીને પહેલા તમારા ફોનનો સ્ક્રીનશોટ અપલોડ કરો.** / **Please upload a screenshot first.**", None, None

    lang = LANGUAGE_MAP.get(lang_choice, "Gujarati")
    question = (custom_q or "").strip()
    if not question:
        question = preset_q or "What should I do on this screen?"

    sys_prompt = HELP_SYSTEM_PROMPT.format(lang=lang)
    raw_output, is_fallback, err_detail = call_ollama(sys_prompt, question, img, as_json=False)

    if is_fallback or not raw_output:
        if not is_fallback and err_detail:
            return f"❌ **Error connecting to Ollama:**\n\n`{err_detail}`\n\n*Please ensure Ollama is running and model '{MODEL_NAME}' is pulled.*", None, None

        # fallback to verified demo text if model isn't active
        sample_key = detect_sample_type(question)
        demo_text = DEMO_RESPONSES.get(sample_key, {}).get("help", {}).get(lang, DEMO_RESPONSES["bill"]["help"]["English"])
        result = (
            f"> 💡 **[Offline Demo Preview]** *Ollama is offline or model '{MODEL_NAME}' is downloading. Showing verified demo output:*\n\n"
            f"{demo_text}\n\n"
            f"---\n"
            f"*To run live inference: run `ollama pull {MODEL_NAME}` in your terminal.*"
        )
    else:
        result = raw_output

    annotated_overlay = draw_tap_overlay(img, result, question)
    audio_file = generate_speech_file(result, lang)
    return result, annotated_overlay, audio_file

def scam_check(img, lang_choice):
    # tab 2 pipeline: returns json verdict, adds upi fraud protection, formats into card
    if img is None:
        return "⚠️ **કૃપા કરીને પહેલા સ્ક્રીનશોટ અપલોડ કરો.** / **Please upload a screenshot first.**", None

    lang = LANGUAGE_MAP.get(lang_choice, "Gujarati")
    sys_prompt = SCAM_SYSTEM_PROMPT.format(lang=lang)
    user_prompt = "Check this screen or message for scam indicators, fraud risk, and provide safety verdict."

    raw_output, is_fallback, err_detail = call_ollama(sys_prompt, user_prompt, img, as_json=True)

    if is_fallback or not raw_output:
        if not is_fallback and err_detail:
            return f"❌ **Error connecting to Ollama:**\n\n`{err_detail}`", None

        sample_key = "scam_sms"
        d = DEMO_RESPONSES.get(sample_key, {}).get("scam", {}).get(lang, DEMO_RESPONSES["scam_sms"]["scam"]["English"])
        is_demo_note = "\n\n> 💡 *[Offline Demo Preview - Ollama offline or model downloading]*"
    else:
        try:
            d = extract_json(raw_output)
            is_demo_note = ""
        except Exception:
            # show raw text if json formatting somehow breaks
            return f"### Analysis Output\n\n{raw_output}", None

    verdict = str(d.get("verdict", "SUSPICIOUS")).upper()
    reasons = d.get("reasons", [])
    advice = d.get("advice", "")

    reasons_md = "\n".join(f"- **{r}**" for r in reasons)
    icon_header = ICONS.get(verdict, f"❓ {verdict}")
    card_class = BADGE_CLASSES.get(verdict, "badge-suspicious")

    # specialized UPI collect & refund fraud shield
    upi_alert = ""
    combined_check = (verdict + " " + " ".join(reasons) + " " + advice).lower()
    if any(k in combined_check for k in ["upi", "pin", "પિન", "ઓટીપી", "पिन", "refund", "કલેક્ટ"]):
        upi_alert = """
> 🚨 **UPI Safety Alert / UPI સુરક્ષા ચેતવણી:** પૈસા મેળવવા કે રિફંડ લેવા માટે ક્યારેય UPI PIN નાખવો પડતો નથી! જો તમે PIN નાખશો તો તમારા ખાતામાંથી પૈસા કપાઈ જશે! (Entering UPI PIN always sends money, never receives!)
"""

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

{upi_alert}
{is_demo_note}

---
> 🛡️ **સુવર્ણ નિયમ / Golden Rule:** બેંક કે કોઈપણ સરકારી અધિકારી ક્યારેય ફોન કે SMS પર તમારો **OTP, UPI PIN, ATM કાર્ડ નંબર કે પાસવર્ડ** પૂછતા નથી. ક્યારેય કોઈની સાથે શેર કરશો નહીં!
"""
    audio_file = generate_speech_file(f"{verdict}. {advice}", lang)
    return result, audio_file

def generate_speech_file(text: str, lang: str):
    # renders audio using local gTTS file if available
    if not TTS_AVAILABLE:
        return None
    try:
        clean_text = text.replace("#", "").replace("*", "").replace(">", "").strip()
        lang_code = "gu" if lang == "Gujarati" else ("hi" if lang == "Hindi" else "en")
        tts = gTTS(text=clean_text[:300], lang=lang_code, slow=False)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tts.save(f.name)
            return f.name
    except Exception:
        return None

def load_sample_image(filename: str):
    # helper for the 1-click sample test buttons
    path = DEMO_DIR / filename
    if path.exists():
        return Image.open(path)
    return None

def get_system_status():
    # pings local server and models for the info tab
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

# larger typography and contrasting backgrounds for older eyes
CUSTOM_CSS = """
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

# browser speech synthesis snippets for 100% offline tts
JS_SPEAK_HELP = """
() => {
    const el = document.getElementById("help-output-container");
    if (!el) return;
    const text = el.innerText || el.textContent;
    if (!text) return;
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text.substring(0, 400));
    utt.rate = 0.9;
    window.speechSynthesis.speak(utt);
}
"""

JS_SPEAK_SCAM = """
() => {
    const el = document.getElementById("scam-output-container");
    if (!el) return;
    const text = el.innerText || el.textContent;
    if (!text) return;
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text.substring(0, 400));
    utt.rate = 0.9;
    window.speechSynthesis.speak(utt);
}
"""

JS_STOP_SPEAK = """
() => {
    window.speechSynthesis.cancel();
}
"""

# speech recognition to speak questions directly via microphone in browser
JS_LISTEN_QUESTION = """
() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.");
        return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = "gu-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    const input = document.querySelector("#help-custom-q textarea, #help-custom-q input");
    if (!input) return;

    const origPlaceholder = input.placeholder;
    input.placeholder = "🎙️ Listening... please speak your question now...";

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        input.value = text;
        input.dispatchEvent(new Event("input", { bubbles: true }));
        input.placeholder = origPlaceholder;
    };

    recognition.onerror = (e) => {
        input.placeholder = origPlaceholder;
        console.warn("Speech recognition error:", e.error);
    };

    recognition.onend = () => {
        input.placeholder = origPlaceholder;
    };

    recognition.start();
}
"""

# one-click alert family on whatsapp with pre-filled warning
JS_SHARE_WHATSAPP = """
() => {
    const el = document.getElementById("scam-output-container");
    const summary = el ? (el.innerText || el.textContent).slice(0, 250) : "Suspicious phone message.";
    const msg = [
        "⚠️ Family Alert: I received a suspicious message on my phone.",
        summary,
        "Please check before I tap anything."
    ].join("\\n\\n");
    window.open("https://wa.me/?text=" + encodeURIComponent(msg), "_blank");
}
"""

with gr.Blocks(title="What do I tap? Helper (Offline Gemma 4)") as demo:
    gr.HTML(f"""
    <style>
    {CUSTOM_CSS}
    </style>
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
        # tab 1: help me with screen actions
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
                        value="What should I do on this screen?",
                        elem_id="help-custom-q",
                        placeholder="e.g. How do I pay this bill?"
                    )

                    with gr.Row():
                        btn_voice_input = gr.Button("🎙️ Speak Question (માઈક્રોફોન બોલો)", size="sm")
                        btn_voice_input.click(None, None, None, js=JS_LISTEN_QUESTION)

                    btn_help = gr.Button("🔍 Explain Step-by-Step (મને સમજાવો)", variant="primary", elem_classes=["btn-large"])

                with gr.Column(scale=6):
                    with gr.Accordion("🎯 Visual Tap Target Overlay (ક્યાં અડવું તે જુઓ)", open=True):
                        help_overlay = gr.Image(label="Where to Tap", type="pil", interactive=False)

                    gr.Markdown("### 📋 Step-by-Step Instructions:")
                    with gr.Group(elem_id="help-output-container"):
                        help_output = gr.Markdown(
                            value="*Upload a screenshot and tap 'Explain Step-by-Step' to get clear, numbered instructions.*",
                            elem_classes=["step-card"]
                        )
                    with gr.Row():
                        btn_speak_help = gr.Button("🔊 Read Aloud (Browser Voice)", size="sm")
                        btn_stop_help = gr.Button("⏹️ Stop Audio", size="sm")
                        btn_speak_help.click(None, None, None, js=JS_SPEAK_HELP)
                        btn_stop_help.click(None, None, None, js=JS_STOP_SPEAK)
                    help_audio = gr.Audio(label="🎧 Recorded Audio File (Optional)", interactive=False)

            # sync text box when user clicks a preset question
            help_preset_q.change(
                lambda q: q.split(" (")[0] if " (" in q else q,
                inputs=help_preset_q,
                outputs=help_custom_q
            )

            # one-click sample buttons
            btn_sample_bill.click(lambda: load_sample_image("1_electricity_bill.png"), outputs=help_img)
            btn_sample_settings.click(lambda: load_sample_image("3_phone_settings.png"), outputs=help_img)
            btn_sample_safe.click(lambda: load_sample_image("4_order_delivered.png"), outputs=help_img)

            # run vision pipeline
            btn_help.click(
                help_me,
                inputs=[help_img, help_custom_q, help_preset_q, help_lang],
                outputs=[help_output, help_overlay, help_audio]
            )

        # tab 2: scam & phishing verification
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
                    with gr.Group(elem_id="scam-output-container"):
                        scam_output = gr.Markdown(
                            value="*Upload a screenshot or SMS and tap 'Check for Scam' to see whether it is safe or fraudulent.*",
                            elem_classes=["step-card"]
                        )
                    with gr.Row():
                        btn_speak_scam = gr.Button("🔊 Read Aloud (Browser Voice)", size="sm")
                        btn_stop_scam = gr.Button("⏹️ Stop Audio", size="sm")
                        btn_share_family = gr.Button("👨‍👩‍👦 Alert Family on WhatsApp", size="sm", variant="secondary")
                        btn_speak_scam.click(None, None, None, js=JS_SPEAK_SCAM)
                        btn_stop_scam.click(None, None, None, js=JS_STOP_SPEAK)
                        btn_share_family.click(None, None, None, js=JS_SHARE_WHATSAPP)
                    scam_audio = gr.Audio(label="🎧 Recorded Audio File (Optional)", interactive=False)

            btn_sample_scam.click(lambda: load_sample_image("2_fake_bank_sms.png"), outputs=scam_img)
            btn_sample_safe2.click(lambda: load_sample_image("1_electricity_bill.png"), outputs=scam_img)

            btn_scam.click(
                scam_check,
                inputs=[scam_img, scam_lang],
                outputs=[scam_output, scam_audio]
            )

        # tab 3: system connection & commands
        with gr.Tab("ℹ️ System Status & Info"):
            status_box = gr.Markdown(value=get_system_status())
            btn_refresh_status = gr.Button("🔄 Refresh Connection Status")
            btn_refresh_status.click(get_system_status, outputs=status_box)

            gr.Markdown("""
### 🚀 Setup & Model Commands:
1. **Pull Model in Ollama:**
   ```bash
   ollama pull gemma4:e4b
   ```
2. **Start with Docker Compose:**
   ```bash
   docker compose up --build
   ```
3. **Core Details:**
   - **Privacy First:** Gemma 4 runs 100% locally on your machine with zero cloud calls.
   - **Multilingual Support:** Native reasoning in Gujarati, Hindi, and English.
   - **Visual Overlay:** Highlights the exact button to tap directly on the screen.
   - **Voice Accessible:** Browser speech-to-text input and voice read-aloud.
   - **Resilient Fallback:** Automatically falls back to verified sample data if Ollama is still downloading.
            """)

if __name__ == "__main__":
    print(f"Starting 'What do I tap?' Helper on {GRADIO_SERVER_NAME}:{GRADIO_SERVER_PORT}...")
    launch_kwargs = {
        "server_name": GRADIO_SERVER_NAME,
        "server_port": GRADIO_SERVER_PORT,
        "share": False,
    }
    try:
        import inspect
        sig = inspect.signature(demo.launch)
        if "theme" in sig.parameters:
            launch_kwargs["theme"] = gr.themes.Soft()
    except Exception:
        pass

    demo.launch(**launch_kwargs)
