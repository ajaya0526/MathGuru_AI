import os
import re
import socket
import uuid
import pyttsx3
from gtts import gTTS
import google.generativeai as genai
from dotenv import load_dotenv

# 🔐 Load environment
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 🌐 Check internet connection
def is_internet_available():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# 🤖 Gemini model
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    print("[Gemini model init failed]", e)

# 📦 Session cache
conversation = {
    "question": "",
    "grade": "5",
    "step": 1,
    "history": []
}

def reset_conversation():
    conversation["question"] = ""
    conversation["step"] = 1
    conversation["grade"] = "5"
    conversation["history"] = []

# 🎯 Intelligent offline fallback hints
def offline_hint(question, step):
    q = question.lower()
    if "add" in q or "+" in q:
        return f"💡 Hint {step}: Try lining up the numbers and adding each column."
    elif "subtract" in q or "-" in q:
        return f"💡 Hint {step}: Start from the rightmost digit. Do you need to borrow?"
    elif "multiply" in q or "*" in q or "times" in q:
        return f"💡 Hint {step}: Break one number into parts. Try the distributive method."
    elif "divide" in q or "/" in q:
        return f"💡 Hint {step}: Think of how many times the divisor fits into the dividend."
    elif "^" in q or "square" in q or "power" in q:
        return f"💡 Hint {step}: Multiply the base by itself for the number of times in the exponent."
    else:
        return f"💡 Hint {step}: Try identifying what operation is required first."

# 💬 Generate next hint
def get_next_hint(question):
    if conversation["question"] != question:
        reset_conversation()
        conversation["question"] = question

    step = conversation["step"]
    conversation["step"] += 1

    if is_internet_available():
        try:
            prompt = f"""
You are a helpful math tutor for Grade {conversation['grade']}.

Problem: "{question}"

Give only 💡 Hint {step}. Use a friendly tone.
Don't solve fully, just one helpful hint.

Format:
💡 Hint {step}: [your hint here]
"""
            response = model.generate_content(prompt)
            text = response.text.strip() if response and response.text else f"💡 Hint {step}: (no response)"
        except Exception as e:
            text = f"💡 Hint {step}: ❌ Gemini error: {e}"
    else:
        text = offline_hint(question, step)

    conversation["history"].append(text)
    return text

# ✅ Full step-by-step solution
def get_final_solution(question):
    if is_internet_available():
        try:
            prompt = f"""
Solve this Grade {conversation['grade']} math problem step-by-step:

"{question}"

Use this format:
🧠 Let's solve this...
Step 1: ...
...
Final Answer: ...
"""
            response = model.generate_content(prompt)
            full = response.text.strip() if response and response.text else "❌ No explanation generated."

            return {
                "answer": extract_final_answer(full),
                "explanation": full
            }
        except Exception as e:
            return {
                "answer": "Error",
                "explanation": f"❌ Could not generate solution: {e}"
            }
    else:
        return {
            "answer": "Offline Mode",
            "explanation": "❌ No internet. Please solve manually or check later."
        }

# 🔍 Extract final answer from Gemini output
def extract_final_answer(text):
    match = re.search(r'(final answer|answer)\s*[:=]?\s*(.+)', text, re.IGNORECASE)
    return match.group(2).strip() if match else "--"

# 🔊 Generate offline English TTS for hint
def speak_hint_english(text):
    try:
        tts = gTTS(text=text, lang='en')
        filename = f"static/audio/hint_eng_{uuid.uuid4().hex}.mp3"
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"[ENGLISH TTS ERROR]: {e}")
        return ""

# 🔊 Generate offline Hindi TTS using pyttsx3
def speak_hint_hindi(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 140)
        voices = engine.getProperty('voices')
        selected = False

        for voice in voices:
            langs = voice.languages
            if isinstance(langs, list) and langs:
                try:
                    lang_code = langs[0].decode('utf-8')
                    if 'hi' in lang_code or 'Hindi' in voice.name:
                        engine.setProperty('voice', voice.id)
                        selected = True
                        print(f"✅ Hindi voice selected: {voice.name}")
                        break
                except:
                    continue

        if not selected:
            print("⚠️ Hindi voice not found. Using default voice.")

        filename = f"static/audio/hint_hi_{uuid.uuid4().hex}.mp3"
        engine.save_to_file(text, filename)
        engine.runAndWait()
        return filename

    except Exception as e:
        print(f"[HINDI AUDIO ERROR]: {e}")
        return ""
