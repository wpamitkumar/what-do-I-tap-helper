# prompts for gemma 4 vision instructions

HELP_SYSTEM_PROMPT = """You are a patient helper for an older adult who is not comfortable with smartphones.
You are shown a screenshot and a question. Reply ONLY in {lang}.
Rules:
- Use very simple words. No technical jargon.
- Give at most 5 numbered steps. One action per step.
- Name each button exactly as it appears on screen, and say where it is
  (top, bottom, left, right, middle).
- If the screen asks for a PIN, OTP, password or card number, add a
  warning: "Never share this with anyone."
- If you cannot see what is needed, say so and ask the person to
  send a clearer screenshot. Do not guess."""


SCAM_SYSTEM_PROMPT = """You check screenshots and messages for scams. Reply in {lang}.
Return ONLY valid JSON with exactly these keys:
{{"verdict": "SAFE" | "SUSPICIOUS" | "SCAM",
 "reasons": ["short reason 1", "short reason 2", "short reason 3"],
 "advice": "one sentence on what to do next"}}
Look for: urgency or threats, requests for OTP/PIN/UPI PIN, unknown links,
lookalike sender names, prizes or refunds, requests to install apps.
Max 3 reasons, each under 15 words."""


# pre-baked sample responses for dry-runs or when ollama is still pulling models
DEMO_RESPONSES = {
    "bill": {
        "help": {
            "Gujarati": """૧. સ્ક્રીનની વચ્ચે તમારું લાઈટ બિલ અને રકમ ₹1,450 દેખાશે તેની ખાતરી કરો.
૨. સ્ક્રીન પર સૌથી નીચે લીલા રંગનું **"Pay Now" (હવે ચૂકવો)** બટન છે તે શોધો.
૩. તે **"Pay Now"** બટન પર એક વાર ટેપ કરો.
૪. ત્યારબાદ તમારી બેંક અથવા UPI એપ્લિકેશન પસંદ કરો.
૫. ⚠️ **ચેતવણી:** તમારો ગુપ્ત UPI PIN કોઈની પણ સાથે ક્યારેય શેર કરશો નહીં.""",
            "Hindi": """૧. स्क्रीन के बीच में अपना बिजली का बिल और राशि ₹1,450 चेक करें।
२. स्क्रीन के सबसे नीचे हरे रंग का **"Pay Now" (अभी भुगतान करें)** बटन देखें।
३. उस **"Pay Now"** बटन पर एक बार टैप करें।
४. इसके बाद अपना बैंक या UPI ऐप चुनें।
५. ⚠️ **चेतावनी:** अपना गोपनीय UPI PIN कभी भी किसी के साथ साझा न करें।""",
            "English": """1. Verify your electricity bill amount of ₹1,450 shown in the middle of the screen.
2. Look at the bottom of the screen for the green **"Pay Now"** button.
3. Tap on the **"Pay Now"** button once.
4. Select your preferred payment method (UPI or Net Banking).
5. ⚠️ **Warning:** Never share your secret UPI PIN or password with anyone."""
        },
        "scam": {
            "Gujarati": {
                "verdict": "SAFE",
                "reasons": [
                    "સત્તાવાર વીજળી બિલિંગ પોર્ટલનું ચકાસાયેલ પેજ છે.",
                    "કોઈ શંકાસ્પદ લિંક અથવા અનધિકૃત એકાઉન્ટની વિનંતી નથી.",
                    "યોગ્ય ગ્રાહક નંબર અને બિલ રકમ દર્શાવેલ છે."
                ],
                "advice": "તમે સત્તાવાર એપ દ્વારા સુરક્ષિત રીતે આગળ વધી શકો છો."
            },
            "Hindi": {
                "verdict": "SAFE",
                "reasons": [
                    "यह बिजली बोर्ड का आधिकारिक बिलिंग पेज है।",
                    "कोई संदिग्ध लिंक या अनधिकृत ऐप डाउनलोड नहीं है।",
                    "सही उपभोक्ता संख्या और वैध राशि दिखाई गई है।"
                ],
                "advice": "आप आधिकारिक ऐप के माध्यम से सुरक्षित रूप से बिल का भुगतान कर सकते हैं।"
            },
            "English": {
                "verdict": "SAFE",
                "reasons": [
                    "Official electricity utility provider payment interface.",
                    "Valid consumer account details and billing period shown.",
                    "No suspicious links or third-party payment requests."
                ],
                "advice": "You can safely proceed with paying the bill on this official screen."
            }
        }
    },
    "scam_sms": {
        "help": {
            "Gujarati": """૧. આ મેસેજમાં આપેલી કોઈપણ લિંક પર ભૂલથી પણ ક્લિક કરશો નહીં.
૨. આ મેસેજનો કોઈ પણ જવાબ આપશો નહીં.
૩. સ્ક્રીનની ઉપર જમણી બાજુ આવેલા ત્રણ ટપકાં (More Options) પર ટેપ કરો.
૪. **"Block & Report Spam"** વિકલ્પ પસંદ કરો.
૫. ⚠️ **ચેતવણી:** બેંક ક્યારેય મેસેજમાં એકાઉન્ટ બ્લોકની ધમકી આપીને OTP કે PIN પૂછતી નથી.""",
            "Hindi": """१. इस संदेश में दिए गए किसी भी लिंक पर भूलकर भी क्लिक न करें।
२. इस संदेश का कोई उत्तर न दें।
३. स्क्रीन के ऊपर दाईं ओर तीन बिंदुओं (More Options) पर टैप करें।
४. **"Block & Report Spam"** विकल्प चुनें।
५. ⚠️ **चेतावनी:** बैंक कभी भी मैसेज में अकाउंट ब्लॉक करने की धमकी देकर OTP या PIN नहीं मांगता।""",
            "English": """1. Do NOT click on any link provided in this SMS message.
2. Do not reply to this message with any personal information.
3. Tap the three dots (menu) at the top right of your SMS screen.
4. Select **"Block & Report Spam"** to block this sender.
5. ⚠️ **Warning:** Never share your OTP, PIN, or passwords with anyone."""
        },
        "scam": {
            "Gujarati": {
                "verdict": "SCAM",
                "reasons": [
                    "એકાઉન્ટ બ્લોક કરવાની ખોટી તાકીદ અને ધમકી આપવામાં આવી છે.",
                    "અજાણી શંકાસ્પદ લિંક પર ક્લિક કરવાનું દબાણ છે.",
                    "બેંકિંગ KYC ના નામે છેતરપિંડી કરવાનો સ્પષ્ટ પ્રયાસ છે."
                ],
                "advice": "આ મેસેજ તરત જ ડિલીટ કરો અને મોકલનારને બ્લોક કરો, કોઈ લિંક ખોલશો નહીં."
            },
            "Hindi": {
                "verdict": "SCAM",
                "reasons": [
                    "खाता ब्लॉक होने की झूठी चेतावनी और घबराहट पैदा करने का प्रयास।",
                    "संदिग्ध अनधिकृत लिंक पर क्लिक करने के लिए कहा गया है।",
                    "केवाईसी के नाम पर वित्तीय धोखाधड़ी की योजना है।"
                ],
                "advice": "इस संदेश को तुरंत डिलीट करें और नंबर को ब्लॉक करें, कोई भी लिंक न खोलें।"
            },
            "English": {
                "verdict": "SCAM",
                "reasons": [
                    "Creates artificial urgency threatening imminent bank account suspension.",
                    "Contains suspicious non-official web link asking for credentials.",
                    "Classic phishing attempt impersonating official banking authority."
                ],
                "advice": "Delete this message immediately and block the sender. Do not open the link."
            }
        }
    },
    "settings": {
        "help": {
            "Gujarati": """૧. સ્ક્રીનની મધ્યમાં આવેલા **"Display" (ડિસ્પ્લે)** વિકલ્પ પર ટેપ કરો.
૨. નવી સ્ક્રીન પર નીચે સ્ક્રોલ કરીને **"Font size and style" (ફોન્ટ સાઇઝ)** શોધો.
૩. **"Font size and style"** પર ટેપ કરો.
૪. નીચે આપેલી સ્લાઇડર લાઇન પર ગોળ ટપકું જમણી બાજુ ખેંચો.
૫. અક્ષરો મોટા થઈ જશે અને વાંચવામાં સરળતા રહેશે.""",
            "Hindi": """१. स्क्रीन के बीच में स्थित **"Display" (डिस्प्ले)** विकल्प पर टैप करें।
२. नए पेज पर नीचे स्क्रॉल करके **"Font size and style"** खोजें।
३. **"Font size and style"** पर टैપ करें।
४. नीचे दिए गए स्लाइडर को दाईं ओर खिसकाएं।
५. स्क्रीन पर अक्षर तुरंत बड़े और स्पष्ट हो जाएंगे।""",
            "English": """1. Tap on **"Display"** option in the middle of your Settings screen.
2. Scroll down until you see **"Font size and style"**.
3. Tap on **"Font size and style"**.
4. Drag the blue circular slider to the right side to enlarge the text.
5. Notice how all the text becomes bigger and much easier to read."""
        },
        "scam": {
            "Gujarati": {
                "verdict": "SAFE",
                "reasons": [
                    "આ તમારા ફોનનું અસલ સેટિંગ્સ પેજ છે.",
                    "કોઈ બાહ્ય લિંક અથવા ઓનલાઇન જોખમ નથી.",
                    "સંપૂર્ણપણે સુરક્ષિત સિસ્ટમ મેનૂ છે."
                ],
                "advice": "તમે તમારી જરૂરિયાત મુજબ ફોન સેટિંગ્સ સુરક્ષિત રીતે બદલી શકો છો."
            },
            "Hindi": {
                "verdict": "SAFE",
                "reasons": [
                    "यह आपके फोन का वास्तविक सेटिंग्स मेनू है।",
                    "कोई बाहरी लिंक या साइबर सुरक्षा खतरा नहीं है।",
                    "यह पूरी तरह से सुरक्षित फोन सिस्टम स्क्रीन है।"
                ],
                "advice": "आप बिना किसी डर के अपनी पसंद के अनुसार फोन सेटिंग्स बदल सकते हैं।"
            },
            "English": {
                "verdict": "SAFE",
                "reasons": [
                    "Standard native operating system settings screen.",
                    "No external communications, advertisements, or scam links.",
                    "Completely safe local device settings interface."
                ],
                "advice": "You are inside safe phone settings. No threat detected."
            }
        }
    },
    "order": {
        "help": {
            "Gujarati": """૧. સ્ક્રીન પર તમારા ઓર્ડરની વિગતો અને "Delivered" (ડિલિવર થયેલ) સ્ટેટસ જુઓ.
૨. જો તમને સામાન મળી ગયો હોય તો કશું કરવાની જરૂર નથી.
૩. જો સામાન ન મળ્યો હોય, તો સ્ક્રીન પર નીચે આપેલ **"Need Help?"** પર ટેપ કરો.
૪. ⚠️ **ચેતવણી:** રિફંડ માટે કોઈ પણ વ્યક્તિ તમારો UPI PIN માંગે તો આપશો નહીં.""",
            "Hindi": """१. स्क्रीन पर अपने आर्डर का विवरण और "Delivered" स्थिति देखें।
२. यदि सामान मिल गया है, तो आपको कुछ भी करने की आवश्यकता नहीं है।
३. यदि सामान नहीं मिला है, तो नीचे दिए गए **"Need Help?"** पर टैप करें।
४. ⚠️ **चेतावनी:** रिफंड के नाम पर कभी भी किसी को अपना UPI PIN न बताएं।""",
            "English": """1. Review your order details and the "Delivered" status shown on screen.
2. If you already received your package safely, no action is needed.
3. If package was not delivered, tap on the **"Need Help?"** button at the bottom.
4. ⚠️ **Warning:** Customer care will NEVER ask for your bank UPI PIN or OTP."""
        },
        "scam": {
            "Gujarati": {
                "verdict": "SAFE",
                "reasons": [
                    "સત્તાવાર શોપિંગ એપની ખરીદી પુષ્ટિ સ્ક્રીન છે.",
                    "કોઈ શંકાસ્પદ તૃતીય પક્ષ લિંક નથી.",
                    "સામાન્ય ઓર્ડર સ્ટેટસ માહિતી છે."
                ],
                "advice": "આ સ્ક્રીન સુરક્ષિત છે."
            },
            "Hindi": {
                "verdict": "SAFE",
                "reasons": [
                    "यह आधिकारिक शॉपिंग ऐप का डिलीवरी पुष्टिकरण पेज है।",
                    "कोई भ्रामक या धोखाधड़ी वाला लिंक नहीं है।",
                    "सामान्य ऑर्डर ट्रैकिंग विवरण है।"
                ],
                "advice": "यह स्क्रीन सुरक्षित है।"
            },
            "English": {
                "verdict": "SAFE",
                "reasons": [
                    "Legitimate e-commerce delivery confirmation screen.",
                    "Contains valid order tracking details and timeline.",
                    "No suspicious outbound links or credential phishing."
                ],
                "advice": "This screen is safe. No threats detected."
            }
        }
    }
}
