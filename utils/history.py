import json
import os
import socket
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# 🔐 Load environment & configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 📁 Local history file
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'history.json')

# 🌐 Check internet connection
def is_internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# 🌐 Optionally send summary to Gemini
def sync_to_gemini(entry):
    try:
        prompt = f"""
Log this student's math session:

Problem: {entry['expression']}
Hint Given: {entry['hint']}
Final Answer: {entry['result']}
Timestamp: {entry['timestamp']}

Summarize and confirm this has been logged successfully.
"""
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        print("[Gemini Sync]:", response.text.strip())
    except Exception as e:
        print("[Gemini Sync Error]:", e)

# 💾 Save a new math record locally + online
def save_history(expression, result, hint=""):
    new_entry = {
        'expression': expression,
        'result': result,
        'hint': hint,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Load current history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    else:
        history = []

    history.append(new_entry)

    # Save locally
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

    # 🌐 Sync to Gemini if online
    if is_internet_available():
        sync_to_gemini(new_entry)

# 🔍 Load all local history
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    else:
        return []
