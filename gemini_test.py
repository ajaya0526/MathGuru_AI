import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
print("[DEBUG] Loaded Key:", api_key)
genai.configure(api_key=api_key)

try:
    print("[DEBUG] Connecting to Gemini 1.5 Flash...")
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("What is 10 divided by 2?")
    print("✅ Gemini Response:", response.text)
except Exception as e:
    print("❌ ERROR calling Gemini:", e)
