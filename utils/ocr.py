import os
import re
import cv2
import pytesseract
import easyocr
import socket
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

# 🔐 Load and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# 🧠 Initialize EasyOCR reader
reader = easyocr.Reader(['en', 'hi'], gpu=False)

# 📁 Log file for OCR
LOG_PATH = "ocr_log.txt"

# 📝 Logging utility
def log(msg):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - {msg}\n")
    except Exception as e:
        print("[LOGGING ERROR]:", e)

# 🌐 Check internet connection
def is_internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# 🧪 Image preprocessing
def preprocess(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return cv2.bitwise_not(thresh)
    except Exception as e:
        log(f"[PREPROCESS ERROR]: {e}")
        return cv2.imread(image_path)

# 📷 Main OCR function (hybrid)
def extract_text(image_path):
    results = {}

    # ✅ 1. Try Gemini (only if online)
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

    # ✅ 2. Try Tesseract
    try:
        img = preprocess(image_path)
        tess = pytesseract.image_to_string(img, config="--psm 6", lang='eng+hin')
        if tess.strip():
            results["Tesseract"] = tess.strip()
            log(f"[SUCCESS] Tesseract: {tess.strip()}")
    except Exception as e:
        log(f"[Tesseract Error]: {e}")

    # ✅ 3. Try EasyOCR
    try:
        easy_text = reader.readtext(image_path, detail=0)
        joined = " ".join(easy_text).strip()
        if joined:
            results["EasyOCR"] = joined
            log(f"[SUCCESS] EasyOCR: {joined}")
    except Exception as e:
        log(f"[EasyOCR Error]: {e}")

    # ✅ 4. Return first valid match
    for engine in ["Gemini", "Tesseract", "EasyOCR"]:
        if engine in results and re.search(r"[\d\+\-\*/=xX÷×]", results[engine]):
            return results[engine]

    # ❌ No valid result
    log("[FAIL] No valid math expression found.")
    return "❌ No valid math expression found. Please try again."
