import os
import zlib
import struct
from pathlib import Path

DEMO_DIR = Path(__file__).parent / "demo"
DEMO_DIR.mkdir(parents=True, exist_ok=True)

def generate_with_pil():
    from PIL import Image, ImageDraw, ImageFont

    def create_mockup(title_text, accent_color, content_builder):
        width, height = 720, 1280
        img = Image.new("RGB", (width, height), color=(245, 247, 250))
        draw = ImageDraw.Draw(img)

        # Phone Status bar
        draw.rectangle([(0, 0), (width, 48)], fill=(30, 35, 45))
        draw.text((24, 14), "10:30 AM", fill=(255, 255, 255))
        draw.text((width - 120, 14), "5G  | 98%", fill=(255, 255, 255))

        # App Bar
        draw.rectangle([(0, 48), (width, 130)], fill=accent_color)
        draw.text((30, 75), title_text, fill=(255, 255, 255))

        # Build custom content
        content_builder(draw, width, height)

        # Phone Navigation Bar (Bottom)
        draw.rectangle([(0, height - 60), (width, height)], fill=(20, 24, 30))
        # Home bar indicator
        draw.rounded_rectangle([(width // 2 - 80, height - 35), (width // 2 + 80, height - 25)], radius=5, fill=(180, 180, 180))

        return img

    # 1. Electricity Bill Screen
    def draw_bill(draw, w, h):
        # Card
        draw.rounded_rectangle([(30, 160), (w - 30, 520)], radius=16, fill=(255, 255, 255), outline=(220, 224, 230), width=2)
        draw.text((60, 190), "GUJARAT ELECTRICITY BOARD (UGVCL)", fill=(80, 90, 105))
        draw.text((60, 230), "Consumer No: 08392-49102-1", fill=(30, 40, 55))
        draw.text((60, 270), "Bill Period: SEP 2026", fill=(100, 110, 125))
        draw.text((60, 320), "Total Amount Due:", fill=(80, 90, 105))
        draw.text((60, 355), "₹ 1,450.00", fill=(25, 135, 84))
        draw.text((60, 430), "Due Date: 15 Oct 2026", fill=(220, 53, 69))

        # Green Pay Now button
        draw.rounded_rectangle([(40, 560), (w - 40, 650)], radius=12, fill=(25, 135, 84))
        draw.text((w // 2 - 60, 590), "PAY NOW", fill=(255, 255, 255))

        # Security note
        draw.rectangle([(40, 680), (w - 40, 780)], fill=(235, 245, 255), outline=(180, 210, 245))
        draw.text((60, 710), "Official Utility Payment Portal", fill=(13, 110, 253))
        draw.text((60, 740), "Never share your UPI PIN or Bank OTP with anyone.", fill=(100, 100, 100))

    img_bill = create_mockup("Electricity Bill Payment", (13, 110, 253), draw_bill)
    img_bill.save(DEMO_DIR / "1_electricity_bill.png")

    # 2. Fake Bank SMS Phishing Screen
    def draw_scam(draw, w, h):
        # SMS conversation card
        draw.rounded_rectangle([(30, 160), (w - 30, 300)], radius=12, fill=(255, 255, 255), outline=(220, 224, 230))
        draw.text((60, 185), "Sender: VK-SBI-ALERT (Unknown)", fill=(220, 53, 69))
        draw.text((60, 220), "Today, 10:14 AM", fill=(120, 120, 120))

        # Scam SMS Bubble
        draw.rounded_rectangle([(30, 330), (w - 30, 680)], radius=16, fill=(255, 235, 235), outline=(230, 160, 160), width=2)
        lines = [
            "URGENT NOTICE:",
            "Dear Customer, your Bank Account is BLOCKED today",
            "due to pending KYC verification.",
            "",
            "Tap link immediately to update KYC and enter OTP:",
            "http://sbi-kyc-verify-urgent.link/login",
            "",
            "Failing which ₹25,000 penalty will be charged.",
            "DO NOT IGNORE."
        ]
        y_offset = 360
        for line in lines:
            color = (200, 20, 20) if "http" in line or "URGENT" in line else (30, 30, 30)
            draw.text((50, y_offset), line, fill=color)
            y_offset += 32

        # Threat highlights
        draw.rectangle([(40, 720), (w - 40, 840)], fill=(255, 243, 205), outline=(255, 193, 7))
        draw.text((60, 750), "Warning Signs: Threatens penalty + fake urgent link", fill=(133, 100, 4))
        draw.text((60, 790), "Legitimate banks never send unverified link URLs.", fill=(133, 100, 4))

    img_scam = create_mockup("Messages (SMS)", (50, 60, 75), draw_scam)
    img_scam.save(DEMO_DIR / "2_fake_bank_sms.png")

    # 3. Settings Screen (Font Size / Display)
    def draw_settings(draw, w, h):
        # Settings list
        items = [
            ("Connections", "Wi-Fi, Bluetooth, Flight mode"),
            ("Sounds and vibration", "Sound mode, Ringtone"),
            ("Notifications", "App notifications, Status bar"),
            ("Display", "Brightness, Eye comfort shield, Font size"),
            ("Wallpaper and style", "Color palette, Dark mode"),
            ("Home screen", "Layout, App icon badges"),
            ("Lock screen", "Screen lock type, Always On Display")
        ]
        y = 160
        for title, sub in items:
            is_highlight = (title == "Display")
            bg_color = (230, 242, 255) if is_highlight else (255, 255, 255)
            outline_col = (13, 110, 253) if is_highlight else (230, 230, 230)
            draw.rounded_rectangle([(30, y), (w - 30, y + 90)], radius=10, fill=bg_color, outline=outline_col, width=2 if is_highlight else 1)
            draw.text((60, y + 18), title, fill=(13, 110, 253) if is_highlight else (20, 25, 35))
            draw.text((60, y + 50), sub, fill=(110, 115, 125))
            draw.text((w - 70, y + 30), ">", fill=(150, 150, 150))
            y += 105

        # Callout arrow pointing to Display
        draw.rounded_rectangle([(40, y + 20), (w - 40, y + 90)], radius=8, fill=(240, 240, 240))
        draw.text((60, y + 45), "Tap 'Display' to adjust font size and text scaling", fill=(50, 50, 50))

    img_settings = create_mockup("Settings", (33, 37, 41), draw_settings)
    img_settings.save(DEMO_DIR / "3_phone_settings.png")

    # 4. Genuine Order Delivery Screen
    def draw_order(draw, w, h):
        draw.rounded_rectangle([(30, 160), (w - 30, 500)], radius=14, fill=(255, 255, 255), outline=(220, 225, 230))
        draw.text((60, 190), "DELIVERED TODAY", fill=(25, 135, 84))
        draw.text((60, 230), "Grocery & Household Supplies Order #940182", fill=(40, 45, 55))
        draw.text((60, 270), "Delivered to: Home (Tower B, Flat 402)", fill=(100, 105, 115))
        draw.line([(60, 310), (w - 60, 310)], fill=(230, 230, 230), width=1)
        draw.text((60, 330), "Package handed to resident at front door.", fill=(60, 70, 80))
        draw.text((60, 370), "Item total: ₹ 820.00 (Paid via UPI)", fill=(100, 105, 115))

        # Buttons
        draw.rounded_rectangle([(40, 540), (w - 40, 620)], radius=10, fill=(255, 255, 255), outline=(13, 110, 253), width=2)
        draw.text((w // 2 - 50, 565), "Need Help?", fill=(13, 110, 253))

        draw.rounded_rectangle([(40, 640), (w - 40, 720)], radius=10, fill=(245, 245, 245))
        draw.text((w // 2 - 60, 665), "Rate Delivery", fill=(80, 80, 80))

    img_order = create_mockup("Order Details", (245, 130, 32), draw_order)
    img_order.save(DEMO_DIR / "4_order_delivered.png")

    print("Successfully generated 4 demo screenshots with Pillow.")

def generate_pure_python():
    """Fallback generator using standard library zlib & struct to create PNGs"""
    def write_png(filepath, width, height, get_rgb):
        raw = bytearray()
        for y in range(height):
            raw.append(0)
            for x in range(width):
                r, g, b = get_rgb(x, y)
                raw.extend((r, g, b))
        compressor = zlib.compressobj()
        compressed = compressor.compress(raw) + compressor.flush()

        def chunk(tag, data):
            return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

        png = b'\x89PNG\r\n\x1a\n'
        png += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
        png += chunk(b'IDAT', compressed)
        png += chunk(b'IEND', b'')

        with open(filepath, 'wb') as f:
            f.write(png)

    w, h = 400, 600

    # 1. Bill
    def rgb_bill(x, y):
        if y < 40: return (13, 110, 253) # header
        if 480 < y < 540 and 40 < x < 360: return (25, 135, 84) # Pay button
        if 80 < y < 350 and 30 < x < 370: return (255, 255, 255) # card
        return (240, 243, 248) # bg
    write_png(DEMO_DIR / "1_electricity_bill.png", w, h, rgb_bill)

    # 2. Scam SMS
    def rgb_scam(x, y):
        if y < 40: return (50, 60, 75)
        if 100 < y < 300 and 30 < x < 370: return (255, 230, 230) # red alert box
        return (245, 245, 247)
    write_png(DEMO_DIR / "2_fake_bank_sms.png", w, h, rgb_scam)

    # 3. Settings
    def rgb_settings(x, y):
        if y < 40: return (33, 37, 41)
        if 180 < y < 240 and 30 < x < 370: return (210, 235, 255) # Display highlighted
        return (250, 250, 250)
    write_png(DEMO_DIR / "3_phone_settings.png", w, h, rgb_settings)

    # 4. Safe Order
    def rgb_order(x, y):
        if y < 40: return (245, 130, 32)
        if 80 < y < 280 and 30 < x < 370: return (255, 255, 255)
        return (242, 244, 247)
    write_png(DEMO_DIR / "4_order_delivered.png", w, h, rgb_order)

    print("Successfully generated 4 demo screenshots with standard library fallback.")

if __name__ == "__main__":
    try:
        generate_with_pil()
    except ImportError:
        generate_pure_python()
