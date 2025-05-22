import os
import json
import uuid
import time
import re
import pyttsx3
from gtts import gTTS
import google.generativeai as genai
from dotenv import load_dotenv

# 🔐 Load Gemini API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 📁 Feedback storage path
FEEDBACK_DB = os.path.join(os.path.dirname(__file__), 'feedbacks.json')

# 📝 Create feedback file if not exists
if not os.path.exists(FEEDBACK_DB):
    with open(FEEDBACK_DB, 'w', encoding='utf-8') as f:
        json.dump([], f)

# 💬 Save a feedback entry (name, message, rating)
def save_feedback(name, message, rating):
    entry = {
        "id": uuid.uuid4().hex,
        "name": name,
        "message": message,
        "rating": rating,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        with open(FEEDBACK_DB, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = []

    data.append(entry)

    with open(FEEDBACK_DB, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# 🤖 Generate explanation and audio using Gemini + gTTS
def evaluate_and_speak(expression):
    try:
        print(f"[MATHGURU] Processing expression: {expression}")
        model = genai.GenerativeModel("models/gemini-2.0-flash")

        prompt = f"""
Act like a friendly math tutor. The student wants help solving: "{expression}"

✅ Instructions:
- Don't give the final answer first.
- Give 1 hint per step.
- Ask helpful guiding questions.
- Then, give a final explanation if explicitly asked.

Now explain step-by-step:
"""

        response = model.generate_content(prompt)
        result_text = response.text.strip()
        print("[GEMINI RESPONSE]:", result_text)

        # Extract final answer line for TTS
        match = re.search(r"(Final Answer|Answer)[:：]?\s*(.+)", result_text, re.IGNORECASE)
        answer_line = match.group(2).strip() if match else "No direct answer given."

        # 🎧 English TTS (Online)
        tts = gTTS(text=answer_line, lang='en')
        audio_filename = f"static/audio/feedback_{uuid.uuid4().hex}.mp3"
        tts.save(audio_filename)

        return {
            "answer": answer_line,
            "steps": result_text
        }, audio_filename

    except Exception as e:
        print(f"[GEMINI ERROR]: {e}")
        return {
            "answer": "Unable to generate explanation.",
            "steps": "There was an error. Please try again."
        }, ""

# 🔊 Speak hint/explanation in Hindi using offline pyttsx3
def synthesize_hindi_audio(text):
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
                        print(f"✅ Hindi voice selected: {voice.name}")
                        selected = True
                        break
                except:
                    continue

        if not selected:
            print("⚠️ Hindi voice not found. Using system default.")

        output_file = f"static/audio/{uuid.uuid4().hex}.mp3"
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        return output_file

    except Exception as e:
        print(f"[HINDI AUDIO ERROR]: {e}")
        return ""
