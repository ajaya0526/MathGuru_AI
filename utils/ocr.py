import os
import re
import cv2
import pytesseract
import socket
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
import time

# 🔐 Load and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# 🧠 Lazy-load EasyOCR
reader = None
def get_easyocr_reader():
    global reader
    if reader is None:
        import easyocr
        reader = easyocr.Reader(['en', 'hi'], gpu=False)
    return reader

# 🧾 Logging setup
LOG_PATH = "ocr_log.txt"
def log(msg):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - {msg}\n")
    except Exception as e:
        print("[LOGGING ERROR]:", e)

# 🌐 Internet check
def is_internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# 🧹 Clean old audio
def clean_old_audio(folder="static/audio", max_age_sec=3600):
    now = time.time()
    if not os.path.exists(folder):
        os.makedirs(folder)
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path) and filename.endswith(".mp3"):
            if now - os.path.getmtime(path) > max_age_sec:
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"[CLEANUP ERROR] {e}")

# 🧪 Preprocess image with resize
def preprocess(image_path, max_width=800, max_height=800):
    try:
        img = cv2.imread(image_path)

        # Resize if larger than max
        height, width = img.shape[:2]
        if width > max_width or height > max_height:
            scale = min(max_width / width, max_height / height)
            img = cv2.resize(img, (int(width * scale), int(height * scale)))

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return cv2.bitwise_not(thresh)
    except Exception as e:
        log(f"[PREPROCESS ERROR]: {e}")
        return cv2.imread(image_path)

# 🔍 Main OCR logic
def extract_text(image_path):
    clean_old_audio()  # 🧹 Clear old audio

    results = {}

    # 1. Gemini
    if is_internet_available():
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = "Extract only the math expression (in Hindi or English) from this image. Do not explain. Just the expression."
            response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_bytes}])
            gemini_text = response.text.strip()
            if gemini_text:
                results["Gemini"] = gemini_text
                log(f"[SUCCESS] Gemini: {gemini_text}")
        except Exception as e:
            log(f"[Gemini Error]: {e}")

    # 2. Tesseract
    try:
        img = preprocess(image_path)
        tess = pytesseract.image_to_string(img, config="--psm 6", lang='eng+hin')
        if tess.strip():
            results["Tesseract"] = tess.strip()
            log(f"[SUCCESS] Tesseract: {tess.strip()}")
    except Exception as e:
        log(f"[Tesseract Error]: {e}")

    # 3. EasyOCR with temporary resize
    try:
        reader = get_easyocr_reader()
        img = cv2.imread(image_path)
        resized = cv2.resize(img, (800, 800))
        temp_path = "temp_easyocr.jpg"
        cv2.imwrite(temp_path, resized)
        easy_text = reader.readtext(temp_path, detail=0)
        os.remove(temp_path)
        joined = " ".join(easy_text).strip()
        if joined:
            results["EasyOCR"] = joined
            log(f"[SUCCESS] EasyOCR: {joined}")
    except Exception as e:
        log(f"[EasyOCR Error]: {e}")

    # 4. Return first valid math expression
    for engine in ["Gemini", "Tesseract", "EasyOCR"]:
        if engine in results and re.search(r"[\d\+\-\*/=xX÷×]", results[engine]):
            return results[engine]

    log("[FAIL] No valid math expression found.")
    return "❌ No valid math expression found. Please try again."
